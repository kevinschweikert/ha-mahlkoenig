"""Base class for Mahlkonig entities."""

from dataclasses import dataclass

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MahlkonigUpdateCoordinator


@dataclass
class MahlkonigEntity[T](CoordinatorEntity[MahlkonigUpdateCoordinator]):
    """Common elements for all entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MahlkonigUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.grinder = coordinator.grinder
        self._attr_unique_id = (
            f"{self.grinder.machine_info.serial_no}_{self.entity_description.key}"
        )

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.grinder.machine_info.serial_no)},
            manufacturer="Mahlkönig",
            model="X54",
            suggested_area="Kitchen",
            sw_version=self.grinder.machine_info.sw_version,
            serial_number=self.grinder.machine_info.serial_no,
            hw_version=self.grinder.machine_info.product_no,
        )

    @property
    def available(self) -> bool:
        """Returns whether entity is available."""
        return self.coordinator.available
