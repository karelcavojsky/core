"""The aurora component."""

from __future__ import annotations

from datetime import timedelta
import logging

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from . import AtleaConfigEntry

_LOGGER = logging.getLogger(__name__)


class AtleaDataUpdateCoordinator(DataUpdateCoordinator[int]):
    """Class to manage fetching data from the NOAA Aurora API."""

    config_entry: AtleaConfigEntry

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the data updater."""

        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name="Atloa",
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self) -> int:
        """Fetch the data from the NOAA Aurora Forecast."""

        try:
            return 25
        except ClientError as error:
            raise UpdateFailed(f"Error updating from NOAA: {error}") from error
