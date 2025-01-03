"""Platform for sensor integration."""

from __future__ import annotations

# from pprint import pprint
import time

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import AtleaConfigEntry


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
    # pprint(vars(entry))

    async_add_entities(
        [
            TemeratureSensor("devanm", f"{time.time}"),
            TemeratureSensor("devbnm", f"{time.time}"),
            TemeratureSensor("devcnm", f"{time.time}"),
        ]
    )


class TemeratureSensor(SensorEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True
    _attr_translation_key = "temp_oda"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, name: str, unique_id: str) -> None:
        """Init the base entity."""
        self._attr_name = name
        self._attr_unique_id = f"{name}-{unique_id}"

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = 23
