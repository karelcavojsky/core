"""Platform for sensor integration."""

from __future__ import annotations

# from pprint import pprint
import time

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import LiconConfigEntry
from .connector import VentboxConnector
from .coordinator import LiconDataUpdateCoordinator


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiconConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    controls = entry.options["device_description"]["control"]
    production_number = entry.options["device_description"]["production_number"]

    entities = []

    for key in controls:
        function = controls[key]
        if (function['valueType'] != 'bool'):
            continue
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
        coordinator: LiconDataUpdateCoordinator,
        function,
        production_number: str,
        connector: VentboxConnector,
    ) -> None:
        """Init the base entity."""
        super().__init__(coordinator)
        self._attr_name = function["name"]
        self._attr_unique_id = f"{name}-{unique_id}"
        self._attr_translation_key = name
        self._connector = connector
        self.function = function
        self._attr_device_info = coordinator.device_info

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self._connector.setBool(self.function["name"], False)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self._connector.setBool(self.function["name"], True)
