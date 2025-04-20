"""The Licon component."""

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LiconDataUpdateCoordinator


class LiconEntity(CoordinatorEntity[LiconDataUpdateCoordinator]):
    """Implementation of the base Licon Entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LiconDataUpdateCoordinator,
        translation_key: str,
    ) -> None:
        """Initialize the Licon Entity."""

        super().__init__(coordinator=coordinator)

        self._attr_translation_key = translation_key
        self._attr_unique_id = "kkll"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._attr_unique_id)},
            manufacturer="NOAATREA",
            model="Licon Visibility Sensor",
        )
