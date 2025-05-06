"""Video Matrix Mapping Sensor"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from mahlkoenig import Grinder, Recipe

from .coordinator import MahlkonigUpdateCoordinator
from .entity import MahlkonigEntity

# Coordinator is used to centralize the data updates
PARALLEL_UPDATES = 0


@dataclass(kw_only=True, frozen=True)
class MahlkonigSensorEntityDescription(SensorEntityDescription):
    """Description for X54 sensor entities."""

    enabled: bool = True
    value_fn: Callable[[Grinder], int | float | None] = lambda _: None
    attr_fn: Callable[[Grinder], dict[str, Any] | None] = lambda _: None


def _recipe_attrs(recipe: Recipe) -> dict[str, Any] | None:
    return {
        "bean_name": recipe.bean_name,
        "brewing_type": recipe.brewing_type.name,
        "grinding_degree": recipe.grinding_degree,
        "guid": recipe.guid,
        "last_modify_index": recipe.last_modify_index,
        "last_modify_time": recipe.last_modify_time,
        "name": recipe.name,
        "recipe_no": recipe.recipe_no,
    }


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
            state_class=SensorStateClass.MEASUREMENT,
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
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda grinder: grinder.statistics.total_on_time.total_seconds(),
        ),
        MahlkonigSensorEntityDescription(
            key="system_restarts",
            name="System Restarts",
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:numeric",
            state_class=SensorStateClass.TOTAL_INCREASING,
            value_fn=lambda grinder: grinder.statistics.system_restarts,
        ),
        MahlkonigSensorEntityDescription(
            key="total_grind_shots",
            name="Total Grind Shots",
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:numeric",
            state_class=SensorStateClass.TOTAL_INCREASING,
            value_fn=lambda grinder: grinder.statistics.total_grind_shots,
        ),
        MahlkonigSensorEntityDescription(
            key="total_grind_time",
            name="Total Grind Time",
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            suggested_unit_of_measurement=UnitOfTime.HOURS,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:clock-time-four",
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda grinder: grinder.statistics.total_grind_time.total_seconds(),
        ),
        MahlkonigSensorEntityDescription(
            key="total_motor_on_time",
            name="Total Motor On Time",
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            suggested_unit_of_measurement=UnitOfTime.MINUTES,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:clock-time-four",
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda grinder: grinder.statistics.total_motor_on_time.total_seconds(),
        ),
        MahlkonigSensorEntityDescription(
            key="standby_time",
            name="Standby Time",
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            suggested_unit_of_measurement=UnitOfTime.HOURS,
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:clock-time-four",
            state_class=SensorStateClass.MEASUREMENT,
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
        [
            MahlkonigSensorEntityDescription(
                key=f"recipe_{recipe_no}_grind_time",
                name=f"Recipe {recipe_no} Grind Time",
                native_unit_of_measurement=UnitOfTime.SECONDS,
                device_class=SensorDeviceClass.DURATION,
                icon="mdi:av-timer",
                state_class=SensorStateClass.TOTAL_INCREASING,
                attr_fn=lambda grinder, r=recipe_no: _recipe_attrs(grinder.recipes[r]),
                value_fn=lambda grinder, r=recipe_no: grinder.recipes[
                    r
                ].grind_time.total_seconds(),
            )
            for recipe_no in coordinator.grinder.recipes.keys()
        ]
    )

    entity_descriptions.extend(
        [
            MahlkonigSensorEntityDescription(
                key="manual_mode_grind_time",
                name="Manual Mode Grind Time",
                native_unit_of_measurement=UnitOfTime.SECONDS,
                suggested_unit_of_measurement=UnitOfTime.MINUTES,
                device_class=SensorDeviceClass.DURATION,
                icon="mdi:av-timer",
                state_class=SensorStateClass.TOTAL_INCREASING,
                value_fn=lambda grinder: grinder.statistics.manual_mode_grind_time.total_seconds(),
            )
        ]
    )

    entity_descriptions.extend(
        [
            MahlkonigSensorEntityDescription(
                key=f"recipe_{recipe_no}_shots",
                name=f"Recipe {recipe_no} Shots",
                state_class=SensorStateClass.TOTAL_INCREASING,
                icon="mdi:numeric",
                attr_fn=lambda grinder, r=recipe_no: _recipe_attrs(grinder.recipes[r]),
                value_fn=lambda grinder, r=recipe_no: getattr(
                    grinder.statistics, f"recipe_{r}_grind_shots"
                ),
            )
            for recipe_no in range(1, 5)
        ]
    )

    entity_descriptions.extend(
        [
            MahlkonigSensorEntityDescription(
                key=f"recipe_{recipe_no}_time",
                name=f"Recipe {recipe_no} Time",
                native_unit_of_measurement=UnitOfTime.SECONDS,
                suggested_unit_of_measurement=UnitOfTime.MINUTES,
                device_class=SensorDeviceClass.DURATION,
                state_class=SensorStateClass.TOTAL_INCREASING,
                icon="mdi:clock-time-four",
                attr_fn=lambda grinder, r=recipe_no: _recipe_attrs(grinder.recipes[r]),
                value_fn=lambda grinder, r=recipe_no: getattr(
                    grinder.statistics, f"recipe_{r}_grind_time"
                ).total_seconds(),
            )
            for recipe_no in range(1, 5)
        ]
    )

    entity_descriptions.extend(
        [
            MahlkonigSensorEntityDescription(
                key="manual_mode_shots",
                name="Manual Mode Shots",
                state_class=SensorStateClass.TOTAL_INCREASING,
                icon="mdi:numeric",
                value_fn=lambda grinder: grinder.statistics.manual_mode_grind_shots,
            )
        ]
    )

    entity_descriptions.extend(
        [
            MahlkonigSensorEntityDescription(
                key=f"total_errors_{error_no:02}",
                name=f"Total Errors {error_no:02}",
                state_class=SensorStateClass.TOTAL_INCREASING,
                entity_category=EntityCategory.DIAGNOSTIC,
                icon="mdi:numeric",
                enabled=False,
                value_fn=lambda grinder, e=error_no: getattr(
                    grinder.statistics, f"total_errors_{e:02}"
                ),
            )
            for error_no in (1, 2, 3, 4, 8, 9, 10)
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

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra attributes."""
        return self.entity_description.attr_fn(self.coordinator.grinder)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.entity_description.value_fn(
            self.coordinator.grinder
        )
        super()._handle_coordinator_update()
