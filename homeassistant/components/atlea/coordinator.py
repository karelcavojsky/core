"""The aurora component."""

from __future__ import annotations

from datetime import timedelta
import logging

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .connector import aMotionConnector

_LOGGER = logging.getLogger(__name__)


class AtleaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the aMotion device."""

    def __init__(self, hass: HomeAssistant, connector: aMotionConnector) -> None:
        """Initialize the data updater."""

        self._connector = connector
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name="Atloa",
            update_interval=timedelta(seconds=10),
        )

    async def _async_update_data(self):
        """Fetch the data from the aMotion device."""

        try:
            return await self._connector.update()
        except ClientError as error:
            raise UpdateFailed(
                f"Error updating from aMotion device: {error}"
            ) from error
