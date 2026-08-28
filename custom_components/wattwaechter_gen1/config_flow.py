"""Config flow for Wattwächter Gen1."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    WattwaechterApi,
    WattwaechterAuthenticationError,
    WattwaechterCannotConnect,
    WattwaechterInvalidResponse,
    normalize_host,
)
from .const import CONF_PASSWORD, CONF_USERNAME, DEFAULT_NAME, DOMAIN

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
    }
)


class WattwaechterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wattwächter Gen1."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                host = normalize_host(user_input[CONF_HOST])
                api = WattwaechterApi(
                    async_get_clientsession(self.hass),
                    host,
                    user_input.get(CONF_USERNAME),
                    user_input.get(CONF_PASSWORD),
                )
                device_info = await api.async_get_device_info()
                await api.async_get_sensor_data()
            except ValueError:
                errors[CONF_HOST] = "invalid_host"
            except WattwaechterAuthenticationError:
                errors["base"] = "invalid_auth"
            except WattwaechterCannotConnect:
                errors["base"] = "cannot_connect"
            except WattwaechterInvalidResponse:
                errors["base"] = "invalid_response"
            else:
                unique_id = device_info.mac or host.lower()
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})

                data = {CONF_HOST: host}
                for key in (CONF_USERNAME, CONF_PASSWORD):
                    if value := user_input.get(key):
                        data[key] = value
                return self.async_create_entry(
                    title=device_info.name or DEFAULT_NAME,
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_SCHEMA, user_input or {}
            ),
            errors=errors,
        )

