"""Platform for sensor integration."""

from __future__ import annotations

# from pprint import pprint
import time

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AtleaConfigEntry
from .connector import aMotionConnector
from .coordinator import AtleaDataUpdateCoordinator


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AtleaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    functions = entry.options["device_description"]["functions"]
    production_number = entry.options["device_description"]["production_number"]

    entities = []

    for function in functions:
        entities.append(  # noqa: PERF401
            SwitchFunctionEntity(
                f"{function['name']}",
                f"{production_number}-{time.time}",
                entry.runtime_data["coordinator"],
                function,
                production_number,
                entry.runtime_data["connector"],
            )
        )

    async_add_entities(entities)


class SwitchFunctionEntity(CoordinatorEntity, SwitchEntity):
    """Representation of a scene."""

    _attr_has_entity_name = True

    def __init__(
        self,
        name: str,
        unique_id: str,
        coordinator: AtleaDataUpdateCoordinator,
        function,
        production_number: str,
        connector: aMotionConnector,
    ) -> None:
        """Init the base entity."""
        super().__init__(coordinator)
        self._attr_name = function["name"]
        self._attr_unique_id = f"{name}-{unique_id}"
        self._attr_translation_key = name
        self._attr_device_class = SwitchDeviceClass.OUTLET
        self._connector = connector
        self.function = function
        self._attr_icon = "md.toggle-switch"
        self._attr_device_info = coordinator.device_info

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self._connector.setFce(self.function["id"], False)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self._connector.setFce(self.function["id"], True)
