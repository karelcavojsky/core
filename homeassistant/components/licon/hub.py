"""Base ventbox HUB."""

from .connector import VentboxConnector, async_wrap


class ventboxHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, port: str) -> None:
        """Initialize."""
        self.port = port
        self.connector = VentboxConnector(port)

    async def connect(self):
        """Connect to the device."""
        return await self.connector.connect()

    async def authenticate(self) -> bool:
        """Test if we can authenticate with the host."""
        return await self.connector.connect()

    async def load(self):
        """Load device description data."""
        desc = await self.connector.description()
        await self.connector.close()
        return desc

    async def control(self, variable, value) -> bool:
        """Send the control request."""
        return await self.connector.control(variable, value)

    async def close(self):
        """Close the session."""
        await self.connector.close()
    
    @staticmethod
    @async_wrap
    def serialPorts() -> list:
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        list = VentboxConnector.serialPorts()
        return list
