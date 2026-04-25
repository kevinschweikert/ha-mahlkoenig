"""Binary sensor platform for Mahlkönig X54."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MahlkonigUpdateCoordinator
from .entity import MahlkonigEntity

# Coordinator is used to centralize the data updates
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[MahlkonigUpdateCoordinator],
    async_add_entities: AddEntitiesCallback,
):
    coordinator = entry.runtime_data

    async_add_entities(
        [
            GrindRunningBinarySensor(
                coordinator,
                BinarySensorEntityDescription(
                    key="grind_running",
                    name="Grinder running",
                    entity_category=EntityCategory.DIAGNOSTIC,
                ),
            ),
            ConnectedBinarySensor(
                coordinator,
                BinarySensorEntityDescription(
                    key="connected",
                    name="Connected",
                    device_class=BinarySensorDeviceClass.CONNECTIVITY,
                    entity_category=EntityCategory.DIAGNOSTIC,
                ),
            ),
        ],
        update_before_add=True,
    )


class GrindRunningBinarySensor(
    MahlkonigEntity[BinarySensorEntityDescription], BinarySensorEntity
):
    """Live grinding state — unavailable when the grinder is offline."""

    entity_description: BinarySensorEntityDescription

    @property
    def available(self) -> bool:
        """Only available while connected; we don't show stale running state."""
        return self.coordinator.grinder.connected

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.coordinator.grinder.connected:
            return
        status = self.coordinator.grinder.system_status
        self._attr_is_on = status.grind_running if status is not None else None
        super()._handle_coordinator_update()


class ConnectedBinarySensor(
    MahlkonigEntity[BinarySensorEntityDescription], BinarySensorEntity
):
    """Reflects the live WebSocket connection state."""

    entity_description: BinarySensorEntityDescription

    @property
    def available(self) -> bool:
        """Always available — we always know the connection state."""
        return True

    @property
    def is_on(self) -> bool:
        """True when the grinder is reachable."""
        return self.coordinator.grinder.connected
