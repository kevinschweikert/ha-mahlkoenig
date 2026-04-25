"""Select platform for Mahlkönig X54."""

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

    async_add_entities(
        [
            AutoSleepTimeSelect(
                coordinator,
                SelectEntityDescription(
                    key="select_auto_sleep_time",
                    name="Auto Sleep Time",
                    entity_category=EntityCategory.CONFIG,
                    icon="mdi:clock-time-four",
                ),
            )
        ],
        update_before_add=True,
    )


class AutoSleepTimeSelect(MahlkonigEntity[SelectEntityDescription], SelectEntity):
    """Auto-sleep time setting — keeps last-known value while grinder sleeps."""

    entity_description: SelectEntityDescription

    @property
    def options(self) -> list[str]:
        return [str(preset) for preset in AutoSleepTimePreset]

    @property
    def current_option(self) -> str | None:
        sleep = self.coordinator.grinder.auto_sleep_time
        return str(sleep) if sleep is not None else None

    @property
    def available(self) -> bool:
        """Available as long as we have observed a value at least once."""
        return self.current_option is not None

    async def async_select_option(self, option: str) -> None:
        """Called when the user chooses a new preset."""
        preset = next(preset for preset in AutoSleepTimePreset if option == str(preset))
        await self.coordinator.grinder.set_auto_sleep_time(preset)
        await self.coordinator.async_request_refresh()
