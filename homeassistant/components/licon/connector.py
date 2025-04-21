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
    def __init__(self, register: int, name="unknown", max=100, min=0, step=1):
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
        self.valueType = "bool"


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
        self._requests = {}
        self._units = {}

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
        try:
            if not self._client.connected:
                self._client.close()
                return False
        except Exception:  # noqa: BLE001
            pass
        return True

    async def getRequestRegister(self, key: str) -> _VentboxValueType | None:
        """Get the register number by key."""
        if (len(self._requests) == 0):
                await self.getRequests()
        for re in self._requests:
            if (str(self._requests[re].name) == str(key)):
                retval = self._requests[re]
                retval.__class__ = _VentboxValueType
                return retval
        return None

    async def getRequests(self):
        """Get the control parameters."""
        req = {}
        self._requests.clear()
        self._requests["co2"] = (_VentboxValueTypeNumber(107,name="co2", max=2000, min=400, step=1, unit="ppm"))
        self._requests["tvoc"] = (_VentboxValueTypeNumber(109,name="tvoc", max=10, min=0, step=1, unit="ppm"))
        self._requests["radon"] = (_VentboxValueTypeNumber(110,name="radon", max=1000, min=0, step=1, unit="Bq/m3"))
        self._requests["rh"] = (_VentboxValueTypeFactor(108,name="rh"))
        self._requests["power_req"] = (_VentboxValueTypeFactor(106,name="power_req"))
        self._requests["year_req"] = (_VentboxValueTypeNumber(100,name="year_req", max=3000, min=0, step=1, unit="Y"))
        self._requests["month_req"] = (_VentboxValueTypeNumber(101,name="month_req", max=12, min=1, step=1, unit="M"))
        self._requests["day_req"] = (_VentboxValueTypeNumber(102,name="day_req", max=31, min=1, step=1, unit="D"))
        self._requests["hour_req"] = (_VentboxValueTypeNumber(103,name="hour_req", max=24, min=0, step=1, unit="h"))
        self._requests["min_req"] = (_VentboxValueTypeNumber(104,name="min_req", max=60, min=0, step=1, unit="m"))
        self._requests["sec_req"] = (_VentboxValueTypeNumber(105,name="sec_req", max=60, min=0, step=1, unit="s"))
        self._requests["time_set"] = (_VentboxValueTypeBool(1,name="time_set"))

        for r in self._requests:
            req[r] = vars(self._requests[r])

        return req

    async def getUnit(self):
        """Get the monitor parameters."""
        unit = {}
        self._units.clear()
        # self._units["CO2"] = (_VentboxValueTypeNumber(101,name="CO2", max=2000, min=400, step=1, unit="ppm"))
        # self._units["TVOC"] = (_VentboxValueTypeNumber(104,name="TVOC", max=10, min=0, step=1, unit="ppm"))
        # self._units["RH"] = (_VentboxValueTypeFactor(102,name="RH"))
        # self._units["TE"] = (_VentboxValueTypeTemperature(103,"TE"))
        # self._units["MANUAL"] = (_VentboxValueTypeFactor(100,name="MANUAL"))
        self._units["te1"] = (_VentboxValueTypeTemperature(110,"te1"))
        self._units["te1p"] = (_VentboxValueTypeTemperature(111,"te1p"))
        self._units["te2"] = (_VentboxValueTypeTemperature(112,"te2"))
        self._units["ti1"] = (_VentboxValueTypeTemperature(113,"ti1"))
        self._units["ti2"] = (_VentboxValueTypeTemperature(114,"ti2"))
        self._units["efficiency"] = (_VentboxValueTypeFactor(115,"efficiency"))
        self._units["in_power"] = (_VentboxValueTypeNumber(116,name="in_power", max=3000, min=0, step=1, unit="W"))
        self._units["m1_power"] = (_VentboxValueTypeFactor(118,name="m1_power"))
        self._units["m2_power"] = (_VentboxValueTypeFactor(119,name="m2_power"))
        self._units["m1_rpm"] = (_VentboxValueTypeNumber(120,name="m1_rpm", max=6000, min=0, step=1, unit="RPM"))
        self._units["m2_rpm"] = (_VentboxValueTypeNumber(121,name="m2_rpm", max=6000, min=0, step=1, unit="RPM"))
        self._units["m1_rh"] = (_VentboxValueTypeFactor(122,name="m1_rh"))
        self._units["m2_rh"] = (_VentboxValueTypeFactor(123,name="m2_rh"))
        self._units["m1_te"] = (_VentboxValueTypeTemperature(124,name="m1_te"))
        self._units["m2_te"] = (_VentboxValueTypeTemperature(125,name="m2_te"))
        self._units["m1_mass_flow"] = (_VentboxValueTypeNumber(126,name="m1_mass_flow", max=6000, min=0, step=1, unit="kg/h"))
        self._units["m2_mass_flow"] = (_VentboxValueTypeNumber(127,name="m2_mass_flow", max=6000, min=0, step=1, unit="kg/h"))
        self._units["year"] = (_VentboxValueTypeNumber(128,name="year", max=3000, min=0, step=1, unit="Y"))
        self._units["month"] = (_VentboxValueTypeNumber(129,name="month", max=12, min=1, step=1, unit="M"))
        self._units["day"] = (_VentboxValueTypeNumber(130,name="day", max=31, min=1, step=1, unit="D"))
        self._units["hour"] = (_VentboxValueTypeNumber(131,name="hour", max=24, min=0, step=1, unit="h"))
        self._units["min"] = (_VentboxValueTypeNumber(132,name="min", max=60, min=0, step=1, unit="m"))
        self._units["sec"] = (_VentboxValueTypeNumber(133,name="sec", max=60, min=0, step=1, unit="s"))

        for r in self._units:
            unit[r] = vars(self._units[r])

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
        for re in desc.control:
            desc.requests.append(str(re))

        return desc

    async def update(self) -> dict: 
        """Return monitor data."""
        data = {}
        await self.connect()
        try:
            if (len(self._units) == 0):
                await self.getUnit()
            if (len(self._requests) == 0):
                await self.getRequests()
            startRegister = 110
            res = await self._client.read_input_registers(startRegister, count=30, slave=VentboxAddress.MAIN_UNIT)            
            for unit in self._units:
                #print(units[unit]['name'])
                val = res.registers[self._units[unit].register - startRegister] * self._units[unit].multiplier
                try:
                    min = self._units[unit].min
                    max = self._units[unit].max
                    if (val > max) or (val < min):
                        val = None
                except: # noqa: BLE001
                    pass
                data[self._units[unit].name] = val
            startRegister = 100
            res = await self._client.read_holding_registers(startRegister, count=11, slave=VentboxAddress.MAIN_UNIT)           
            for unit in self._requests:
                if (self._requests[unit].valueType == 'bool'):
                    continue                
                val = res.registers[self._requests[unit].register - startRegister] * self._requests[unit].multiplier
                try:
                    min = self._requests[unit].min
                    max = self._requests[unit].max
                    if (val > max) or (val < min):
                        val = None
                except: # noqa: BLE001
                    pass
                data[self._requests[unit].name] = val
            
        except Exception as e: # noqa: BLE001
            print (e)
            for unit in self._units:
                data[self._units[unit].name] = None
            for unit in self._requests:
                data[self._requests[unit].name] = None

        print((data))
        return data  # noqa: RET504

    async def control(self, variable, value) -> bool:
        """Send the control request."""
        item = await self.getRequestRegister(variable)
        if not item:
            return False
        if (item.multiplier != 0):
            value /=  item.multiplier
        print(f'CONTROL -- {variable} ({item.register}) = {value}')
        await self._client.write_register(item.register, int(value), slave=VentboxAddress.MAIN_UNIT)
        return True
    
    async def setBool(self, variable: str, status: bool) -> bool:
        item = await self.getRequestRegister(variable)
        print(f'BOOL -- {variable} ({item.register}) = {status}')
        await self._client.write_coil(item.register, status, slave=VentboxAddress.MAIN_UNIT)
        return True
