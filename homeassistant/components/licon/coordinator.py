"""The aurora component."""

from __future__ import annotations

from datetime import timedelta
import logging

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .connector import VentboxConnector

_LOGGER = logging.getLogger(__name__)


class LiconDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the ventbox device."""

    def __init__(
        self, hass: HomeAssistant, connector: VentboxConnector, device_info: DeviceInfo
    ) -> None:
        """Initialize the data updater."""
        self.device_info = device_info
        self.connector = connector
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name="Atloa",
            update_interval=timedelta(seconds=10),
        )

    async def _async_update_data(self):
        """Fetch the data from the ventbox device."""

        try:
            return await self.connector.update()
        except ClientError as error:
            raise UpdateFailed(
                f"Error updating from ventbox device: {error}"
            ) from error
