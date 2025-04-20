from pymodbus import FramerType  # noqa: D100
import pymodbus.client as ModbusClient


class VentboxAddress:
    """Available parts of the Ventbox system."""

    MAIN_UNIT = 3


class _VentboxValueType:
    def __init__(self):
        self.type = "range"
        self.unit = "°C"
        self.valueType = "UNKNOWN"
        self.name = "UNKNOWN"


class _VentboxValueTypeTemperature(_VentboxValueType):
    def __init__(self, name="unknown", max=50.0, min=-30.0, step=0.1):
        """Init data."""
        super().__init__()
        self.name = name
        self.valueType = "t_outside"
        self.max = max
        self.min = min
        self.step = step


class _VentboxValueTypeNumber(_VentboxValueType):
    def __init__(
        self, name="unknown", max=50.0, min=-30.0, step=0.1, unit="", valueType="number"
    ):
        """Init data."""
        super().__init__()
        self.name = name
        self.valueType = valueType
        self.max = max
        self.min = min
        self.step = step
        self.unit = unit


class _VentboxValueTypeFactor(_VentboxValueType):
    def __init__(self, name="unknown", max=50.0, min=-30.0, step=0.1):
        """Init data."""
        super().__init__()
        self.name = name
        self.valueType = "percent"
        self.max = max
        self.min = min
        self.step = step
        self.unit = "%"


class _VentboxValueTypeEnum(_VentboxValueType):
    def __init__(self, name="unknown", values=list[str]):
        """Init data."""
        super().__init__()
        self.name = name
        self.values = values
        self.type = "enum"
        self.unit = "enum"
        self.valueType = "enum"


class _VentboxValueTypeBool(_VentboxValueType):
    def __init__(self, name="unknown"):
        """Init data."""
        super().__init__()
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
        self.production_number = "Unknown"
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
        req["co2"] = vars(
            _VentboxValueTypeNumber(name="co2", max=2000, min=400, step=1, unit="ppm")
        )
        req["tvoc"] = vars(
            _VentboxValueTypeNumber(name="tvoc", max=10, min=0, step=1, unit="ppm")
        )
        req["radon"] = vars(
            _VentboxValueTypeNumber(name="radon", max=1000, min=0, step=1, unit="Bq/m3")
        )
        req["rh"] = vars(_VentboxValueTypeFactor(name="rh"))
        req["power_req"] = vars(_VentboxValueTypeFactor(name="power_req"))
        req["year"] = vars(
            _VentboxValueTypeNumber(name="year", max=3000, min=0, step=1, unit="Y")
        )
        req["month"] = vars(
            _VentboxValueTypeNumber(name="month", max=12, min=1, step=1, unit="M")
        )
        req["day"] = vars(
            _VentboxValueTypeNumber(name="day", max=31, min=1, step=1, unit="D")
        )
        req["hour"] = vars(
            _VentboxValueTypeNumber(name="hour", max=24, min=0, step=1, unit="h")
        )
        req["min"] = vars(
            _VentboxValueTypeNumber(name="min", max=60, min=0, step=1, unit="m")
        )
        req["sec"] = vars(
            _VentboxValueTypeNumber(name="sec", max=60, min=0, step=1, unit="s")
        )

        return req

    async def getUnit(self):
        """Get the monitor parameters."""
        unit = {}
        unit["te1"] = vars(_VentboxValueTypeTemperature("te1"))
        unit["te1p"] = vars(_VentboxValueTypeTemperature("te1p"))
        unit["te2"] = vars(_VentboxValueTypeTemperature("te2"))
        unit["ti1"] = vars(_VentboxValueTypeTemperature("ti1"))
        unit["ti2"] = vars(_VentboxValueTypeTemperature("ti2"))
        unit["efficiency"] = vars(_VentboxValueTypeFactor("efficiency"))
        unit["in_power"] = vars(
            _VentboxValueTypeNumber(name="in_power", max=3000, min=0, step=1, unit="W")
        )
        unit["m1_power"] = vars(_VentboxValueTypeFactor(name="m1_power"))
        unit["m2_power"] = vars(_VentboxValueTypeFactor(name="m2_power"))
        unit["m1_rpm"] = vars(
            _VentboxValueTypeNumber(name="m1_rpm", max=6000, min=0, step=1, unit="RPM")
        )
        unit["m2_rpm"] = vars(
            _VentboxValueTypeNumber(name="m2_rpm", max=6000, min=0, step=1, unit="RPM")
        )
        unit["m1_rh"] = vars(_VentboxValueTypeFactor(name="m1_rh"))
        unit["m2_rh"] = vars(_VentboxValueTypeFactor(name="m2_rh"))
        unit["m1_te"] = vars(_VentboxValueTypeTemperature(name="m1_te"))
        unit["m2_te"] = vars(_VentboxValueTypeTemperature(name="m2_te"))
        unit["m1_mass_flow"] = vars(
            _VentboxValueTypeNumber(
                name="m1_mass_flow", max=6000, min=0, step=1, unit="kg/h"
            )
        )
        unit["m2_mass_flow"] = vars(
            _VentboxValueTypeNumber(
                name="m2_mass_flow", max=6000, min=0, step=1, unit="kg/h"
            )
        )
        unit["year"] = vars(
            _VentboxValueTypeNumber(name="year", max=3000, min=0, step=1, unit="Y")
        )
        unit["month"] = vars(
            _VentboxValueTypeNumber(name="month", max=12, min=1, step=1, unit="M")
        )
        unit["day"] = vars(
            _VentboxValueTypeNumber(name="day", max=31, min=1, step=1, unit="D")
        )
        unit["hour"] = vars(
            _VentboxValueTypeNumber(name="hour", max=24, min=0, step=1, unit="h")
        )
        unit["min"] = vars(
            _VentboxValueTypeNumber(name="min", max=60, min=0, step=1, unit="m")
        )
        unit["sec"] = vars(
            _VentboxValueTypeNumber(name="sec", max=60, min=0, step=1, unit="s")
        )

        return unit

    async def description(self) -> VentboxDescription:  # noqa: D102
        desc = VentboxDescription()
        desc.sensors = await self.getUnit()
        desc.unit = []
        for re in desc.sensors:
            desc.unit.append(str(re))
        desc.control = await self.getRequests()
        desc.requests = []
        for re in desc.sensors:
            desc.requests.append(str(re))

        return desc

    async def update(self) -> dict:  # noqa: D102
        data = {"dummy": False}
        # uinfo = await self.getUiInfo()
        # controlPanel = await self.getControlPanel()
        # uinfo["current"] = controlPanel["control_panel"]["current"]

        # sourceKeys = ["requests", "unit", "current"]

        # for skey in sourceKeys:
        #     source = uinfo[skey]
        #     for iname in source:
        #         data[iname] = source[iname]

        return data  # noqa: RET504

    async def control(self, variable, value) -> bool:
        """Send the control request."""

        return False

    async def close(self):  # noqa: D102
        try:  # noqa: SIM105
            await self.getUnit()
        except Exception:  # noqa: BLE001
            pass
