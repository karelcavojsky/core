"""Platform for sensor integration."""

from __future__ import annotations

import random

# from pprint import pprint
import time

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AtleaConfigEntry
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

    async_add_entities(
        [
            TemeratureNumber("devnumber", f"{time.time}", entry.runtime_data),
        ]
    )


class TemeratureNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True
    _attr_translation_key = "temp_oda"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    # _attr_min_value = -10
    # _attr_max_value = 45

    def __init__(
        self, name: str, unique_id: str, coordinator: AtleaDataUpdateCoordinator
    ) -> None:
        """Init the base entity."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{name}-{unique_id}"

    def set_native_value(self, value: float) -> None:
        """Update the current value."""

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = random.randrange(220, 260) / 10
        self.async_write_ha_state()
