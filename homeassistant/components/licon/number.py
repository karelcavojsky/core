"""Platform for sensor integration."""

from __future__ import annotations

# from pprint import pprint
import time

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
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
from .connector import VentboxConnector
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
    controls = entry.options["device_description"]["control"]
    production_number = entry.options["device_description"]["production_number"]

    entities = []
    etypes = ["range"]

    for control in controls:
        if etypes.count(controls[control]["type"]) > 0:
            entities.append(  # noqa: PERF401
                RangeValueNumber(
                    f"{control}",
                    f"{production_number}-{time.time}",
                    entry.runtime_data["coordinator"],
                    controls[control],
                    production_number,
                    entry.runtime_data["connector"],
                )
            )

    async_add_entities(entities)


class RangeValueNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True
    _attr_translation_key = "temp"
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        name: str,
        unique_id: str,
        coordinator: LiconDataUpdateCoordinator,
        control,
        production_number: str,
        connector: VentboxConnector,
    ) -> None:
        """Init the base entity."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{name}-{unique_id}"
        self._attr_native_min_value = control["min"]
        self._attr_native_max_value = control["max"]
        self._attr_native_step = control["step"]
        self._connector = connector
        self._attr_device_info = coordinator.device_info

        

        if str(control["valueType"]).find("t_") == 0:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            self._attr_device_class = NumberDeviceClass.TEMPERATURE
        if str(control["valueType"]).find("flow") == 0:
            self._attr_native_unit_of_measurement = (
                UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
            )
            self._attr_device_class = NumberDeviceClass.VOLUME_FLOW_RATE
            self._attr_icon = "mdi:weather-windy"
        if str(control["valueType"]).find("percent") == 0:
            self._attr_native_unit_of_measurement = PERCENTAGE
            self._attr_device_class = NumberDeviceClass.POWER_FACTOR
            if name.find("fan") == 0:
                self._attr_icon = "mdi:fan"
            else:
                self._attr_icon = "mdi:gauge"
        if str(control["valueType"]).find("press") == 0:
            self._attr_native_unit_of_measurement = UnitOfPressure.PA
            self._attr_device_class = NumberDeviceClass.PRESSURE
        if str(control["valueType"]).find("number") == 0:
            self._attr_mode = NumberMode.BOX
            self._attr_icon = "mdi:numeric"

    def set_native_value(self, value: float) -> None:
        """Update the current value."""

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self._connector.control(str(self.name), value)

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:  # noqa: SIM105
            self._attr_native_value = self.coordinator.data[str(self.name)]
        except Exception:  # noqa: BLE001
            pass
        self.async_write_ha_state()
