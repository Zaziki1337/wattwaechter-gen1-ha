"""Diagnostics support for Wattwächter Gen1."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import WattwaechterConfigEntry
from .const import CONF_PASSWORD


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: WattwaechterConfigEntry
) -> dict[str, Any]:
    """Return diagnostics with credentials removed."""
    del hass
    return {
        "config": async_redact_data(entry.data, {CONF_PASSWORD}),
        "device": asdict(entry.runtime_data.device_info),
        "data": entry.runtime_data.coordinator.data,
    }
