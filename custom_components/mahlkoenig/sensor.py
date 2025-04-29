"""Video Matrix Mapping Sensor"""

from collections.abc import Callable
from dataclasses import dataclass

from mahlkoenig import Grinder
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MahlkonigUpdateCoordinator
from .entity import MahlkonigEntity

# Coordinator is used to centralize the data updates
PARALLEL_UPDATES = 0


@dataclass(kw_only=True, frozen=True)
class MahlkonigSensorEntityDescription(SensorEntityDescription):
    """Description for X54 sensor entities."""

    value_fn: Callable[[Grinder], int | float | None]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[MahlkonigUpdateCoordinator],
    async_add_entities: AddEntitiesCallback,
):
    coordinator = entry.runtime_data

    entity_descriptions = [
        MahlkonigSensorEntityDescription(
            key="disc_life_time",
            name="Disc Life Time",
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            suggested_unit_of_measurement=UnitOfTime.HOURS,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:clock-time-four",
            state_class=None,
            value_fn=lambda grinder: grinder.machine_info.disc_life_time.total_seconds(),
        ),
        MahlkonigSensorEntityDescription(
            key="total_on_time",
            name="Total On Time",
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            suggested_unit_of_measurement=UnitOfTime.HOURS,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:clock-time-four",
            state_class=None,
            value_fn=lambda grinder: grinder.statistics.total_on_time.total_seconds(),
        ),
        MahlkonigSensorEntityDescription(
            key="total_grind_time",
            name="Total Grind Time",
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            suggested_unit_of_measurement=UnitOfTime.HOURS,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:clock-time-four",
            state_class=None,
            value_fn=lambda grinder: grinder.statistics.total_grind_time.total_seconds(),
        ),
        MahlkonigSensorEntityDescription(
            key="standby_time",
            name="Standby Time",
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            suggested_unit_of_measurement=UnitOfTime.HOURS,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:clock-time-four",
            state_class=None,
            value_fn=lambda grinder: grinder.statistics.standby_time.total_seconds(),
        ),
        MahlkonigSensorEntityDescription(
            key="active_menu",
            name="Active Menu",
            device_class=SensorDeviceClass.ENUM,
            options=["1", "2", "3", "4"],
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:dots-horizontal",
            state_class=None,
            value_fn=lambda grinder: str(grinder.system_status.active_menu),
        ),
    ]
    entity_descriptions.extend(
        # TODO: add recipe attrs
        [
            MahlkonigSensorEntityDescription(
                key=f"recipe_{recipe_no}_grind_time",
                name=f"Recipe {recipe_no} Grind Time",
                native_unit_of_measurement=UnitOfTime.SECONDS,
                device_class=SensorDeviceClass.DURATION,
                icon="mdi:av-timer",
                state_class=None,
                value_fn=lambda grinder, r=recipe_no: grinder.recipes[
                    r
                ].grind_time.total_seconds(),
            )
            for recipe_no in coordinator.grinder.recipes.keys()
        ]
    )

    sensors = [
        GrinderSensor(coordinator, entity_description)
        for entity_description in entity_descriptions
    ]

    async_add_entities(sensors, update_before_add=True)


class GrinderSensor(MahlkonigEntity[MahlkonigSensorEntityDescription], SensorEntity):
    """The mapping of the input port index to the corresponding output port index"""

    entity_description: MahlkonigSensorEntityDescription

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.entity_description.value_fn(
            self.coordinator.grinder
        )
        super()._handle_coordinator_update()
