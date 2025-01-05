import json  # noqa: D100

import aiohttp


class aMotionDescription:
    """Store amotion data."""

    def __init__(self):
        """Init amotion data."""
        self.device_name = "Atrea Device"
        self.device_type = "aMotion"
        self.board_type = "Unknown"
        self.production_number = "Unknown"
        self.brand = "Unknown"
        self.requests = list[str]
        self.unit = list[str]
        self.types = {}
        self.control = {}
        self.sensors = {}
        self.scenes = []
        self.functions = []


class aMotionConnectorEndpoints:
    """Store device data."""

    def __init__(self, host: str) -> None:  # noqa: D107
        if host.find("http") != 0:
            host = f"http://{host}"

        self._host = host

    def uri(self, ep):  # noqa: D102
        return f"{self._host}/{ep}"

    def login(self):  # noqa: D102
        return self.uri("api/login")

    def ui_control_scheme(self):  # noqa: D102
        return self.uri("api/ui_control_scheme")

    def get_scenes(self):  # noqa: D102
        return self.uri("api/control_admin/config/get_scenes")

    def get_triggers_fce(self):  # noqa: D102
        return self.uri("api/control_admin/config/get_trigger_functions")

    def get_ui_info(self):  # noqa: D102
        return self.uri("api/ui_info")

    def get_discovery(self):  # noqa: D102
        return self.uri("api/discovery")

    def get_control(self):  # noqa: D102
        return self.uri("api/control")

    def get_scene_activate(self):  # noqa: D102
        return self.uri("api/control_admin/config/activate_scene")

    def get_fce_enable(self):  # noqa: D102
        return self.uri("api/control_admin/config/enable_trigger_function")


class aMotionConnector:
    """Adapter to connect aMotion family device."""

    _session: aiohttp.ClientSession

    def __init__(self, username: str, password: str, host: str, port=80) -> None:
        """Initialize connection.

        Args:
            username (str): Username - the device user should be admin
            password (str): password
            host (str): IP address OR hostname of the device (default protocol is HTTP)
            port (int, optional): If there is a non default. Defaults to 80.

        """
        self._host = host
        self._username = username
        self._password = password
        self._api_key = ""
        self.headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "X-ATC-TOKEN": self._api_key,
        }

    @property
    def host(self):  # noqa: D102
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def username(self):  # noqa: D102
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):  # noqa: D102
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def api_key(self):  # noqa: D102
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    def __disconnect_check(self, status):
        if status == 401:
            self._api_key = ""

    async def connect(self, force=False):  # noqa: D102
        if (force == False) and (self._api_key != ""):  # noqa: E712
            return True
        session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)
        self._session = aiohttp.ClientSession(timeout=session_timeout)
        url = aMotionConnectorEndpoints(self._host).login()
        data = {"username": self._username, "password": self._password}
        r = await self._session.post(url, data=json.dumps(data), headers=self.headers)
        self.__disconnect_check(r.status)
        if r.status == 200:
            result = await r.json()
            self._api_key = result["result"]
            self.headers["X-ATC-TOKEN"] = self._api_key
            return True
        return False

    async def getControlSchema(self):  # noqa: D102
        if not await self.connect():
            pass
        url = aMotionConnectorEndpoints(self._host).ui_control_scheme()
        r = await self._session.get(url, headers=self.headers)
        self.__disconnect_check(r.status)
        if r.status == 200:
            result = await r.json()
            return result["result"]
        return {}

    async def getScenes(self):  # noqa: D102
        if not await self.connect():
            pass
        url = aMotionConnectorEndpoints(self._host).get_scenes()
        r = await self._session.get(url, headers=self.headers)
        self.__disconnect_check(r.status)
        if r.status == 200:
            result = await r.json()
            return result["result"]
        return {}

    async def getTriggerFunctions(self):  # noqa: D102
        if not await self.connect():
            pass
        url = aMotionConnectorEndpoints(self._host).get_triggers_fce()
        r = await self._session.get(url, headers=self.headers)
        self.__disconnect_check(r.status)
        if r.status == 200:
            result = await r.json()
            return result["result"]
        return {}

    async def getUiInfo(self):  # noqa: D102
        if not await self.connect():
            pass
        url = aMotionConnectorEndpoints(self._host).get_ui_info()
        r = await self._session.get(url, headers=self.headers)
        self.__disconnect_check(r.status)
        if r.status == 200:
            result = await r.json()
            return result["result"]
        return {}

    async def getDiscovery(self):  # noqa: D102
        if not await self.connect():
            pass
        url = aMotionConnectorEndpoints(self._host).get_discovery()
        r = await self._session.get(url, headers=self.headers)
        self.__disconnect_check(r.status)
        if r.status == 200:
            result = await r.json()
            return result["result"]
        return {}

    async def description(self) -> aMotionDescription:  # noqa: D102
        desc = aMotionDescription()
        control = await self.getControlSchema()
        discovery = await self.getDiscovery()
        scenes = await self.getScenes()
        functions = await self.getTriggerFunctions()
        desc.requests = control["requests"]
        desc.unit = control["unit"]
        desc.device_name = discovery["name"]
        desc.device_type = discovery["type"]
        desc.board_type = discovery["board_type"]
        desc.brand = discovery["brand"]
        desc.types = control["types"]
        desc.production_number = discovery["production_number"]
        desc.scenes = scenes["get_scenes_config"]
        desc.functions = functions["get_trigger_functions"]

        for iname in desc.requests:
            desc.control[iname] = desc.types[iname]
            if not hasattr(desc.control[iname], "name"):
                desc.control[iname]["name"] = iname

        for iname in desc.types:
            if desc.requests.count(iname) == 0:
                desc.sensors[iname] = desc.types[iname]

        return desc

    async def update(self) -> dict:  # noqa: D102
        data = {}
        uinfo = await self.getUiInfo()

        sourceKeys = ["requests", "unit"]

        for skey in sourceKeys:
            source = uinfo[skey]
            for iname in source:
                data[iname] = source[iname]

        return data

    async def control(self, variable, value) -> bool:
        """Send the control request."""
        if not await self.connect():
            return False
        data = {"variables": {variable: value}}
        url = aMotionConnectorEndpoints(self._host).get_control()
        r = await self._session.post(url, data=json.dumps(data), headers=self.headers)
        self.__disconnect_check(r.status)
        if r.status == 200:
            return True
        return False

    async def setScene(self, id: int) -> bool:
        """Send the scene setup."""
        if not await self.connect():
            return False
        data = {"sceneId": id}
        url = aMotionConnectorEndpoints(self._host).get_scene_activate()
        r = await self._session.post(url, data=json.dumps(data), headers=self.headers)
        self.__disconnect_check(r.status)
        if r.status == 200:
            return True
        return False

    async def setFce(self, id: int, state: bool) -> bool:
        """Enable or disable trigger function."""
        if not await self.connect():
            return False
        data = {"id": id, "enabled": state}
        url = aMotionConnectorEndpoints(self._host).get_fce_enable()
        r = await self._session.post(url, data=json.dumps(data), headers=self.headers)
        self.__disconnect_check(r.status)
        if r.status == 200:
            return True
        return False

    async def close(self):  # noqa: D102
        try:  # noqa: SIM105
            await self._session.close()
        except Exception:  # noqa: BLE001
            pass
