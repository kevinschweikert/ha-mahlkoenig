"""Video Matrix Mapping Sensor"""

from homeassistant.components.binary_sensor import (
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

    entity_descriptions = [
        BinarySensorEntityDescription(
            key="grind_running",
            name="Grinder running",
            entity_category=EntityCategory.DIAGNOSTIC,
        )
    ]

    sensors = [
        GrinderSensor(coordinator, entity_description)
        for entity_description in entity_descriptions
    ]

    async_add_entities(sensors, update_before_add=True)


class GrinderSensor(MahlkonigEntity[BinarySensorEntityDescription], BinarySensorEntity):
    """The mapping of the input port index to the corresponding output port index"""

    entity_description: BinarySensorEntityDescription

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.grinder.system_status.grind_running
        super()._handle_coordinator_update()
