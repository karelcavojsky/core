from pymodbus import FramerType  # noqa: D100
import pymodbus.client as ModbusClient

import sys
import glob
import serial
import asyncio
from functools import wraps, partial

def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run 




class VentboxAddress:
    """Available parts of the Ventbox system."""

    MAIN_UNIT = 3


class _VentboxValueType:
    def __init__(self):
        self.register = 0
        self.type = "range"
        self.unit = "°C"
        self.valueType = "UNKNOWN"
        self.name = "UNKNOWN"
        self.multiplier = 1


class _VentboxValueTypeTemperature(_VentboxValueType):
    def __init__(self, register: int, name="unknown", max=50.0, min=-30.0, step=0.1):
        """Init data."""
        super().__init__()
        self.register = register
        self.name = name
        self.valueType = "t_outside"
        self.max = max
        self.min = min
        self.step = step
        self.multiplier = 0.1


class _VentboxValueTypeNumber(_VentboxValueType):
    def __init__(
        self, register: int, name="unknown", max=50.0, min=-30.0, step=0.1, unit="", valueType="number"
    ):
        """Init data."""
        super().__init__()
        self.register = register
        self.name = name
        self.valueType = valueType
        self.max = max
        self.min = min
        self.step = step
        self.unit = unit


class _VentboxValueTypeFactor(_VentboxValueType):
    def __init__(self, register: int, name="unknown", max=50.0, min=-30.0, step=0.1):
        """Init data."""
        super().__init__()
        self.register = register
        self.name = name
        self.valueType = "percent"
        self.max = max
        self.min = min
        self.step = step
        self.unit = "%"


class _VentboxValueTypeEnum(_VentboxValueType):
    def __init__(self, register: int, name="unknown", values=list[str]):
        """Init data."""
        super().__init__()
        self.register = register
        self.name = name
        self.values = values
        self.type = "enum"
        self.unit = "enum"
        self.valueType = "enum"


class _VentboxValueTypeBool(_VentboxValueType):
    def __init__(self, register: int, name="unknown"):
        """Init data."""
        super().__init__()
        self.register = register
        self.name = name
        self.type = "bool"
        self.unit = "On"


class VentboxDescription:
    """Store ventbox data."""

    def __init__(self):
        """Init ventbox data."""
        self.device_name = "Ventbox Device"
        self.device_type = "ventbox"
        self.board_type = "Unknown"
        self.production_number = "E334"
        self.brand = "Unknown"
        self.requests = list[str]
        self.unit = list[str]
        self.types = {}
        self.control = {}
        self.sensors = {}


class VentboxConnector:
    """Adapter to connect ventbox family device."""

    _client: ModbusClient.ModbusBaseClient

    def __init__(self, port: str) -> None:
        """Initialize connection.

        Args:
            port (str): Port as a string - example '/dev/ttyUSB0'

        """
        self._port = port

    @property
    def port(self):  # noqa: D102
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @staticmethod
    def serialPorts():
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    async def close(self, force=False):  # noqa: D102
        try:
            if self._client.connected:
                self._client.close()
                return True
        except Exception:  # noqa: BLE001
            pass
        return False

    async def connect(self, force=False):  # noqa: D102
        # pymodbus_apply_logging_config("DEBUG")
        try:
            if self._client.connected:
                return True
        except Exception:  # noqa: BLE001
            pass

        self._client = ModbusClient.AsyncModbusSerialClient(
            port=self._port,
            framer=FramerType.RTU,
            timeout=1,
            retries=3,
            baudrate=19200,
            bytesize=8,
            parity="E",
            stopbits=1,
            reconnect_delay=0.5,
            handle_local_echo=False,
        )
        await self._client.connect()
        # test client is connected
        assert self._client.connected
        return True

    async def getRequests(self):
        """Get the control parameters."""
        req = {}
        req["co2"] = vars(_VentboxValueTypeNumber(107,name="co2", max=2000, min=400, step=1, unit="ppm"))
        req["tvoc"] = vars(_VentboxValueTypeNumber(109,name="tvoc", max=10, min=0, step=1, unit="ppm"))
        req["radon"] = vars(_VentboxValueTypeNumber(110,name="radon", max=1000, min=0, step=1, unit="Bq/m3"))
        req["rh"] = vars(_VentboxValueTypeFactor(108,name="rh"))
        req["power_req"] = vars(_VentboxValueTypeFactor(106,name="power_req"))
        req["year"] = vars(_VentboxValueTypeNumber(100,name="year", max=3000, min=0, step=1, unit="Y"))
        req["month"] = vars(_VentboxValueTypeNumber(101,name="month", max=12, min=1, step=1, unit="M"))
        req["day"] = vars(_VentboxValueTypeNumber(102,name="day", max=31, min=1, step=1, unit="D"))
        req["hour"] = vars(_VentboxValueTypeNumber(103,name="hour", max=24, min=0, step=1, unit="h"))
        req["min"] = vars(_VentboxValueTypeNumber(104,name="min", max=60, min=0, step=1, unit="m"))
        req["sec"] = vars(_VentboxValueTypeNumber(105,name="sec", max=60, min=0, step=1, unit="s"))

        return req

    async def getUnit(self):
        """Get the monitor parameters."""
        unit = {}
        unit["te1"] = vars(_VentboxValueTypeTemperature(110,"te1"))
        unit["te1p"] = vars(_VentboxValueTypeTemperature(111,"te1p"))
        unit["te2"] = vars(_VentboxValueTypeTemperature(112,"te2"))
        unit["ti1"] = vars(_VentboxValueTypeTemperature(113,"ti1"))
        unit["ti2"] = vars(_VentboxValueTypeTemperature(114,"ti2"))
        unit["efficiency"] = vars(_VentboxValueTypeFactor(115,"efficiency"))
        unit["in_power"] = vars(_VentboxValueTypeNumber(116,name="in_power", max=3000, min=0, step=1, unit="W"))
        unit["m1_power"] = vars(_VentboxValueTypeFactor(118,name="m1_power"))
        unit["m2_power"] = vars(_VentboxValueTypeFactor(119,name="m2_power"))
        unit["m1_rpm"] = vars(_VentboxValueTypeNumber(120,name="m1_rpm", max=6000, min=0, step=1, unit="RPM"))
        unit["m2_rpm"] = vars(_VentboxValueTypeNumber(121,name="m2_rpm", max=6000, min=0, step=1, unit="RPM"))
        unit["m1_rh"] = vars(_VentboxValueTypeFactor(122,name="m1_rh"))
        unit["m2_rh"] = vars(_VentboxValueTypeFactor(123,name="m2_rh"))
        unit["m1_te"] = vars(_VentboxValueTypeTemperature(124,name="m1_te"))
        unit["m2_te"] = vars(_VentboxValueTypeTemperature(125,name="m2_te"))
        unit["m1_mass_flow"] = vars(_VentboxValueTypeNumber(126,name="m1_mass_flow", max=6000, min=0, step=1, unit="kg/h"))
        unit["m2_mass_flow"] = vars(_VentboxValueTypeNumber(127,name="m2_mass_flow", max=6000, min=0, step=1, unit="kg/h"))
        unit["year"] = vars(_VentboxValueTypeNumber(128,name="year", max=3000, min=0, step=1, unit="Y"))
        unit["month"] = vars(_VentboxValueTypeNumber(129,name="month", max=12, min=1, step=1, unit="M"))
        unit["day"] = vars(_VentboxValueTypeNumber(130,name="day", max=31, min=1, step=1, unit="D"))
        unit["hour"] = vars(_VentboxValueTypeNumber(131,name="hour", max=24, min=0, step=1, unit="h"))
        unit["min"] = vars(_VentboxValueTypeNumber(132,name="min", max=60, min=0, step=1, unit="m"))
        unit["sec"] = vars(_VentboxValueTypeNumber(133,name="sec", max=60, min=0, step=1, unit="s"))

        return unit

    async def description(self) -> VentboxDescription: 
        """Return data for entitiy assembling."""
        desc = VentboxDescription()
        startRegister = 100
        res = await self._client.read_input_registers(startRegister, count=30, slave=VentboxAddress.MAIN_UNIT)
        desc.production_number = res.registers[0]
        desc.device_name = f'{desc.device_name} - {desc.production_number}'
        desc.sensors = await self.getUnit()
        desc.unit = []
        for re in desc.sensors:
            desc.unit.append(str(re))
        desc.control = await self.getRequests()
        desc.requests = []
        for re in desc.sensors:
            desc.requests.append(str(re))

        return desc

    async def update(self) -> dict: 
        """Return monitor data."""
        data = {}
        await self.connect()
        try:
            startRegister = 110
            res = await self._client.read_input_registers(startRegister, count=30, slave=VentboxAddress.MAIN_UNIT)
            units = await self.getUnit()
            for unit in units:
                #print(units[unit]['name'])
                val = res.registers[units[unit]['register'] - startRegister] * units[unit]['multiplier']
                data[units[unit]['name']] = val
            
        except Exception: # noqa: BLE001
            pass
        # uinfo = await self.getUiInfo()
        # controlPanel = await self.getControlPanel()
        # uinfo["current"] = controlPanel["control_panel"]["current"]

        # sourceKeys = ["requests", "unit", "current"]

        # for skey in sourceKeys:
        #     source = uinfo[skey]
        #     for iname in source:
        #         data[iname] = source[iname]
        print((data))
        return data  # noqa: RET504

    async def control(self, variable, value) -> bool:
        """Send the control request."""

        return False
