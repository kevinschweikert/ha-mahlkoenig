"""Base class for Mahlkonig entities."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MahlkonigUpdateCoordinator


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

        # `coordinator.has_device_info` is enforced before entities are built,
        # so serial_no is guaranteed non-None here.
        serial_no = coordinator.serial_no
        assert serial_no is not None
        self._attr_unique_id = f"{serial_no}_{self.entity_description.key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial_no)},
            manufacturer="Mahlkönig",
            model="X54",
            suggested_area="Kitchen",
            sw_version=coordinator.sw_version,
            serial_number=serial_no,
            hw_version=coordinator.product_no,
        )

    @property
    def available(self) -> bool:
        """Returns whether entity is available."""
        return self.coordinator.available
