"""The VZT integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from .connector import VentboxConnector
from .const import DOMAIN
from .coordinator import LiconDataUpdateCoordinator

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
]


type LiconConfigEntry = ConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: LiconConfigEntry) -> bool:
    """Set up VZT from a config entry."""
    connector = VentboxConnector(entry.data[CONF_PORT])

    device = DeviceInfo(
        # entry_type = DeviceEntryType.SERVICE,
        identifiers={
            (DOMAIN, entry.options["device_description"]["production_number"])
        },
        manufacturer="LICON",
        model="VentBox",
    )

    coordinator = LiconDataUpdateCoordinator(hass, connector, device)
    entry.runtime_data = {"coordinator": coordinator, "connector": connector}
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: LiconConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
