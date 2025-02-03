"""Platform for sensor integration."""

from __future__ import annotations

# from pprint import pprint
import time

from homeassistant.components.button import ButtonEntity
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
    scenes = entry.options["device_description"]["scenes"]
    production_number = entry.options["device_description"]["production_number"]

    entities = []
    etypes = ["USER"]

    for scene in scenes:
        if etypes.count(scene["purpose"]) > 0:
            entities.append(  # noqa: PERF401
                SceneEntity(
                    f"{scene['name']}",
                    f"{production_number}-{time.time}",
                    entry.runtime_data["coordinator"],
                    scene,
                    production_number,
                    entry.runtime_data["connector"],
                )
            )

    async_add_entities(entities)


class SceneEntity(CoordinatorEntity, ButtonEntity):
    """Representation of a scene."""

    _attr_has_entity_name = True

    def __init__(
        self,
        name: str,
        unique_id: str,
        coordinator: AtleaDataUpdateCoordinator,
        scene,
        production_number: str,
        connector: aMotionConnector,
    ) -> None:
        """Init the base entity."""
        super().__init__(coordinator)
        self._attr_name = scene["name"]
        self._attr_unique_id = f"{name}-{unique_id}"
        self._attr_translation_key = name
        self._connector = connector
        self.scene = scene
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._connector.setScene(self.scene["id"])
