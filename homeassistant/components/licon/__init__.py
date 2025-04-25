"""The VZT integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.components import frontend
from homeassistant.components.panel_custom import async_register_panel
from pathlib import Path
from homeassistant.components.http import StaticPathConfig

from .connector import VentboxConnector
from .const import DOMAIN
from .coordinator import LiconDataUpdateCoordinator

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]


type LiconConfigEntry = ConfigEntry

panelName = "New dashboard"

async def async_setup(hass, config):


    return True


async def async_setup_entry(hass: HomeAssistant, entry: LiconConfigEntry) -> bool:
    """Set up VZT from a config entry."""
    connector = VentboxConnector(entry.data[CONF_PORT])
    global panelName

    #panelName = entry.options["device_description"]["production_number"]

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

    # await hass.http.async_register_static_paths([
    #     StaticPathConfig(
    #     "/licon_static",
    #     hass.config.path("../homeassistant/components/licon/panel-frontend"),
    #     True)]
    # )

    # print(hass.config.path("../homeassistant/components/licon/panel-frontend"))

    # await async_register_panel(
    #     hass,
    #     frontend_url_path="licon",
    #     webcomponent_name="licon-panel",
    #     module_url="/licon_static/main.js",
    #     sidebar_title=panelName,
    #     sidebar_icon="mdi:view-dashboard",
    #     require_admin=False,
    #     embed_iframe=False
    # )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: LiconConfigEntry) -> bool:
    """Unload a config entry."""
    try:
        await entry.runtime_data['connector'].close()
    except:
        pass
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

async def async_remove_entry(hass: HomeAssistant, entry: LiconConfigEntry) -> bool:
    """Remove a config entry."""
    try:
        await entry.runtime_data['connector'].close()
    except:
        pass
