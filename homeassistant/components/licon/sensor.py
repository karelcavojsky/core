"""Platform for sensor integration."""

from __future__ import annotations

# from pprint import pprint
import time

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import LiconConfigEntry
from .coordinator import LiconDataUpdateCoordinator


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    # pylint: disable=hass-argument-type
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiconConfigEntry,
    # pylint: disable=hass-argument-type
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    sensors = entry.options["device_description"]["sensors"]
    production_number = entry.options["device_description"]["production_number"]

    entities = []
    etypes = ["range", "enum"]

    for sensor in sensors:
        if etypes.count(sensors[sensor]["type"]) > 0:
            entities.append(  # noqa: PERF401
                RangeValueSensor(
                    f"{sensor}",
                    f"{production_number}-{time.time}",
                    entry.runtime_data["coordinator"],
                    sensors[sensor],
                    production_number,
                )
            )

    async_add_entities(entities)


class RangeValueSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        name: str,
        unique_id: str,
        coordinator: LiconDataUpdateCoordinator,
        sensor,
        production_number: str,
    ) -> None:
        """Init the base entity."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{name}-{unique_id}"
        self._attr_translation_key = name
        self._attr_device_info = coordinator.device_info

        if str(sensor["valueType"]).find("t_") == 0:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        if str(sensor["valueType"]).find("flow") == 0:
            self._attr_native_unit_of_measurement = (
                UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
            )
            self._attr_device_class = SensorDeviceClass.VOLUME_FLOW_RATE
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_icon = "mdi:weather-windy"
        if str(sensor["valueType"]).find("percent") == 0:
            self._attr_native_unit_of_measurement = PERCENTAGE
            self._attr_device_class = SensorDeviceClass.POWER_FACTOR
            if name.find("fan") == 0:
                self._attr_icon = "mdi:fan"
            else:
                self._attr_icon = "mdi:gauge"
            self._attr_state_class = SensorStateClass.MEASUREMENT
        if str(sensor["valueType"]).find("press") == 0:
            self._attr_native_unit_of_measurement = UnitOfPressure.PA
            self._attr_device_class = SensorDeviceClass.PRESSURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        if str(sensor["type"]).find("enum") == 0:
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_native_value = "UNKNOWN"

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:  # noqa: SIM105
            self._attr_native_value = self.coordinator.data[str(self.name)]
        except Exception:  # noqa: BLE001
            pass

        self.async_write_ha_state()
