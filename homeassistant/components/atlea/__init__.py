"""The VZT integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant

from .connector import aMotionConnector
from .coordinator import AtleaDataUpdateCoordinator

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.NUMBER, Platform.SELECT, Platform.SENSOR]


type AtleaConfigEntry = ConfigEntry  # noqa: F821


async def async_setup_entry(hass: HomeAssistant, entry: AtleaConfigEntry) -> bool:
    """Set up VZT from a config entry."""
    connector = aMotionConnector(
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        entry.data[CONF_HOST],
        8211,
    )
    coordinator = AtleaDataUpdateCoordinator(hass, connector)
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: AtleaConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
