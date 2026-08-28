"""Small asynchronous client for the Tasmota API used by Wattwächter Gen1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from aiohttp import ClientError, ClientSession, ClientTimeout

REQUEST_TIMEOUT = ClientTimeout(total=10)


class WattwaechterError(Exception):
    """Base exception for Wattwächter communication errors."""


class WattwaechterCannotConnect(WattwaechterError):
    """Raised when the device cannot be reached."""


class WattwaechterAuthenticationError(WattwaechterError):
    """Raised when Tasmota rejects the credentials."""


class WattwaechterInvalidResponse(WattwaechterError):
    """Raised when the response is not a supported Tasmota response."""


@dataclass(frozen=True, slots=True)
class WattwaechterDeviceInfo:
    """Stable information read from Tasmota."""

    name: str
    model: str
    firmware: str | None
    mac: str | None


class WattwaechterApi:
    """Read Wattwächter data through the local Tasmota HTTP API."""

    def __init__(
        self,
        session: ClientSession,
        host: str,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self.host = normalize_host(host)
        self._username = username
        self._password = password

    async def async_get_device_info(self) -> WattwaechterDeviceInfo:
        """Return information used for the Home Assistant device entry."""
        payload = await self._async_command("Status 0")
        status = payload.get("Status", {})
        firmware = payload.get("StatusFWR", {})
        network = payload.get("StatusNET", {})

        if not isinstance(status, dict):
            status = {}
        if not isinstance(firmware, dict):
            firmware = {}
        if not isinstance(network, dict):
            network = {}

        friendly_name = status.get("FriendlyName")
        if isinstance(friendly_name, list):
            friendly_name = next(iter(friendly_name), None)

        return WattwaechterDeviceInfo(
            name=str(friendly_name or status.get("DeviceName") or "Wattwächter Gen1"),
            model=str(status.get("DeviceName") or "Wattwächter Gen1 (Tasmota)"),
            firmware=_optional_string(firmware.get("Version")),
            mac=_optional_string(network.get("Mac")),
        )

    async def async_get_sensor_data(self) -> dict[str, Any]:
        """Return the raw Tasmota sensor tree."""
        payload = await self._async_command("Status 10")
        sensor_data = payload.get("StatusSNS")
        if not isinstance(sensor_data, dict):
            raise WattwaechterInvalidResponse("StatusSNS is missing")
        return sensor_data

    async def _async_command(self, command: str) -> dict[str, Any]:
        params = {"cmnd": command}
        if self._username:
            params["user"] = self._username
        if self._password:
            params["password"] = self._password

        try:
            async with self._session.get(
                f"http://{self.host}/cm",
                params=params,
                timeout=REQUEST_TIMEOUT,
            ) as response:
                if response.status in (401, 403):
                    raise WattwaechterAuthenticationError
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except WattwaechterAuthenticationError:
            raise
        except (ClientError, TimeoutError, ValueError) as err:
            raise WattwaechterCannotConnect from err

        if not isinstance(payload, dict):
            raise WattwaechterInvalidResponse("Expected a JSON object")
        if "WARNING" in payload or "Command" in payload and "Error" in payload:
            raise WattwaechterAuthenticationError
        return payload


def normalize_host(value: str) -> str:
    """Normalize a hostname or IP address entered by the user."""
    value = value.strip().rstrip("/")
    parsed = urlsplit(value if "://" in value else f"//{value}")
    if not parsed.hostname:
        raise ValueError("Invalid host")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("Host must not contain a path, query, or fragment")
    return parsed.netloc


def _optional_string(value: Any) -> str | None:
    """Convert an optional API value to a string."""
    return str(value) if value is not None else None
