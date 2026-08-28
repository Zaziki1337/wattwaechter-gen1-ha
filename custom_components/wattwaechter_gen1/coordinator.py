"""Data coordinator for Wattwächter Gen1."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WattwaechterApi, WattwaechterError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

LOGGER = logging.getLogger(__name__)


class WattwaechterCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch all Tasmota sensor values with one request."""

    def __init__(self, hass: HomeAssistant, api: WattwaechterApi) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest device data."""
        try:
            return await self.api.async_get_sensor_data()
        except WattwaechterError as err:
            raise UpdateFailed(f"Error communicating with Wattwächter: {err}") from err

