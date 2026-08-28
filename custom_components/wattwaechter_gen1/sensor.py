"""Sensor platform for Wattwächter Gen1."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WattwaechterConfigEntry
from .entity import WattwaechterEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, slots=True)
class SensorMetadata:
    """Home Assistant metadata inferred from a Tasmota field name."""

    device_class: SensorDeviceClass | None = None
    unit: str | None = None
    state_class: SensorStateClass | None = None
    icon: str | None = None
    entity_category: EntityCategory | None = None
    suggested_display_precision: int | None = None


def _measurement(
    device_class: SensorDeviceClass,
    unit: str,
    precision: int,
) -> SensorMetadata:
    """Build metadata for an instantaneous measurement."""
    return SensorMetadata(
        device_class=device_class,
        unit=unit,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=precision,
    )


EHZ_SENSOR_METADATA: dict[str, SensorMetadata] = {
    "ID": SensorMetadata(
        icon="mdi:identifier",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "meter_import_total": SensorMetadata(
        device_class=SensorDeviceClass.ENERGY,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
    ),
    "meter_export_total": SensorMetadata(
        device_class=SensorDeviceClass.ENERGY,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
    ),
    "net_frequency": _measurement(
        SensorDeviceClass.FREQUENCY,
        UnitOfFrequency.HERTZ,
        1,
    ),
    "actual_power": _measurement(
        SensorDeviceClass.POWER, UnitOfPower.WATT, 0
    ),
    **{
        f"current_l{phase}": _measurement(
            SensorDeviceClass.CURRENT,
            UnitOfElectricCurrent.AMPERE,
            2,
        )
        for phase in (1, 2, 3)
    },
    **{
        f"voltage_l{phase}": _measurement(
            SensorDeviceClass.VOLTAGE,
            UnitOfElectricPotential.VOLT,
            1,
        )
        for phase in (1, 2, 3)
    },
    **{
        f"eff_power_l{phase}": _measurement(
            SensorDeviceClass.POWER,
            UnitOfPower.WATT,
            0,
        )
        for phase in (1, 2, 3)
    },
    **{
        field: SensorMetadata(
            unit="°",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:angle-acute",
            suggested_display_precision=0,
        )
        for field in (
            "phase_l1_l2",
            "phase_l1_l3",
            "phase_l1",
            "phase_l2",
            "phase_l3",
        )
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WattwaechterConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up all values exposed by the installed Tasmota meter script."""
    del hass
    paths = list(_leaf_paths(entry.runtime_data.coordinator.data))
    async_add_entities(WattwaechterSensor(entry, path) for path in paths)


class WattwaechterSensor(WattwaechterEntity, SensorEntity):
    """A dynamically discovered Tasmota sensor value."""

    def __init__(self, entry: WattwaechterConfigEntry, path: tuple[str, ...]) -> None:
        """Initialize a sensor."""
        super().__init__(entry)
        self._path = path
        path_id = "_".join(_slugify(part) for part in path)
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_{path_id}"
        self._attr_name = _name_for(path)

        initial_value = _value_at(entry.runtime_data.coordinator.data, path)
        metadata = _metadata_for(path, initial_value)
        self._attr_device_class = metadata.device_class
        self._attr_native_unit_of_measurement = metadata.unit
        self._attr_state_class = metadata.state_class
        self._attr_icon = metadata.icon
        self._attr_entity_category = metadata.entity_category
        self._attr_suggested_display_precision = metadata.suggested_display_precision

    @property
    def native_value(self) -> Any:
        """Return the latest value at this sensor's path."""
        return _value_at(self.coordinator.data, self._path)


def _leaf_paths(
    value: Mapping[str, Any], prefix: tuple[str, ...] = ()
) -> Iterable[tuple[str, ...]]:
    """Yield paths to scalar values while ignoring Tasmota's timestamp."""
    for key, child in value.items():
        if not prefix and key == "Time":
            continue
        path = (*prefix, str(key))
        if isinstance(child, Mapping):
            yield from _leaf_paths(child, path)
        elif isinstance(child, (str, int, float)) and not isinstance(child, bool):
            yield path


def _value_at(value: Mapping[str, Any], path: tuple[str, ...]) -> Any:
    """Return the value at a path in a nested mapping."""
    current: Any = value
    for part in path:
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def _metadata_for(path: tuple[str, ...], value: Any) -> SensorMetadata:
    """Infer common electricity metadata without assuming a specific meter script."""
    if len(path) > 1 and path[-2].casefold() == "ehz":
        if metadata := EHZ_SENSOR_METADATA.get(path[-1]):
            return metadata

    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return SensorMetadata()

    key = _slugify(path[-1])
    parent = _slugify(path[-2]) if len(path) > 1 else ""
    if (
        any(
            token in key
            for token in ("total_in", "total_out", "energy", "kwh", "1_8", "2_8")
        )
        or parent == "energy" and key in ("today", "yesterday", "total")
    ):
        return SensorMetadata(
            SensorDeviceClass.ENERGY,
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorStateClass.TOTAL_INCREASING,
        )
    if any(
        token in key
        for token in ("power", "leistung", "watt", "16_7", "36_7", "56_7", "76_7")
    ):
        return SensorMetadata(
            SensorDeviceClass.POWER,
            UnitOfPower.WATT,
            SensorStateClass.MEASUREMENT,
        )
    if any(
        token in key
        for token in ("voltage", "spannung", "volt", "32_7", "52_7", "72_7")
    ):
        return SensorMetadata(
            SensorDeviceClass.VOLTAGE,
            UnitOfElectricPotential.VOLT,
            SensorStateClass.MEASUREMENT,
        )
    if any(
        token in key
        for token in ("current", "strom", "ampere", "31_7", "51_7", "71_7")
    ):
        return SensorMetadata(
            SensorDeviceClass.CURRENT,
            UnitOfElectricCurrent.AMPERE,
            SensorStateClass.MEASUREMENT,
        )
    return SensorMetadata()


def _slugify(value: str) -> str:
    """Create a stable entity-id fragment from an API field."""
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_") or "value"


def _name_for(path: tuple[str, ...]) -> str:
    """Use the field name supplied by Tasmota as the entity name."""
    return path[-1]
