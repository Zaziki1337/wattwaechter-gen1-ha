"""Base entity for Wattwächter Gen1."""

from __future__ import annotations

from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import WattwaechterConfigEntry
from .const import DOMAIN
from .coordinator import WattwaechterCoordinator


class WattwaechterEntity(CoordinatorEntity[WattwaechterCoordinator]):
    """Base class shared by Wattwächter entities."""

    _attr_has_entity_name = True

    def __init__(self, entry: WattwaechterConfigEntry) -> None:
        """Initialize the entity."""
        super().__init__(entry.runtime_data.coordinator)
        info = entry.runtime_data.device_info
        identifier = info.mac or entry.unique_id or entry.entry_id
        meter_data = entry.runtime_data.coordinator.data.get("eHZ", {})
        meter_id = meter_data.get("ID") if isinstance(meter_data, dict) else None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, identifier)},
            name=info.name,
            manufacturer="SmartCircuits GmbH",
            model=info.model,
            sw_version=info.firmware,
            serial_number=str(meter_id) if meter_id else None,
            configuration_url=f"http://{entry.data[CONF_HOST]}",
        )
