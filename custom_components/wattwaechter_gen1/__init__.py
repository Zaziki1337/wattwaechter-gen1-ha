"""Wattwächter Gen1 integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import WattwaechterApi, WattwaechterDeviceInfo, WattwaechterError
from .const import CONF_PASSWORD, CONF_USERNAME
from .coordinator import WattwaechterCoordinator

PLATFORMS = [Platform.SENSOR]


@dataclass(slots=True)
class WattwaechterRuntimeData:
    """Runtime objects associated with a config entry."""

    coordinator: WattwaechterCoordinator
    device_info: WattwaechterDeviceInfo


type WattwaechterConfigEntry = ConfigEntry[WattwaechterRuntimeData]


async def async_setup_entry(
    hass: HomeAssistant, entry: WattwaechterConfigEntry
) -> bool:
    """Set up Wattwächter Gen1 from a config entry."""
    api = WattwaechterApi(
        async_get_clientsession(hass),
        entry.data[CONF_HOST],
        entry.data.get(CONF_USERNAME),
        entry.data.get(CONF_PASSWORD),
    )
    try:
        device_info = await api.async_get_device_info()
        coordinator = WattwaechterCoordinator(hass, api)
        await coordinator.async_config_entry_first_refresh()
    except WattwaechterError as err:
        raise ConfigEntryNotReady from err

    entry.runtime_data = WattwaechterRuntimeData(coordinator, device_info)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: WattwaechterConfigEntry
) -> bool:
    """Unload a Wattwächter Gen1 config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
