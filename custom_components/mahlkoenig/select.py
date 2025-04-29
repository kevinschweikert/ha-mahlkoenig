"""Video Matrix Mapping Sensor"""

from mahlkoenig import AutoSleepTimePreset
from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
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
        SelectEntityDescription(
            key="select_auto_sleep_time",
            name="Auto Sleep Time",
            entity_category=EntityCategory.CONFIG,
            icon="mdi:clock-time-four",
        )
    ]

    sensors = [
        GrinderSensor(coordinator, entity_description)
        for entity_description in entity_descriptions
    ]

    async_add_entities(sensors, update_before_add=True)


class GrinderSensor(MahlkonigEntity[SelectEntityDescription], SelectEntity):
    """The mapping of the input port index to the corresponding output port index"""

    entity_description: SelectEntityDescription

    @property
    def options(self) -> list[str]:
        presets = [str(preset) for preset in AutoSleepTimePreset]
        return presets

    @property
    def current_option(self) -> str | None:
        return str(self.coordinator.grinder.auto_sleep_time)

    async def async_select_option(self, option: str) -> None:
        """Called when the user chooses a new preset."""

        preset = next(preset for preset in AutoSleepTimePreset if option == str(preset))

        await self.coordinator.grinder.set_auto_sleep_time(preset)
        await self.coordinator.async_request_refresh()
