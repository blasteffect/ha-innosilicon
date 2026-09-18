from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import InnosiliconApi, InnosiliconApiError, InnosiliconAuthError
from .const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, DEFAULT_USERNAME, DOMAIN


class InnosiliconConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip().rstrip("/")
            unique = host.lower().replace("http://", "").replace("https://", "")
            await self.async_set_unique_id(unique)
            self._abort_if_unique_id_configured()

            api = InnosiliconApi(
                async_get_clientsession(self.hass),
                host,
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
            try:
                await api.authenticate()
                await api.summary()
            except InnosiliconAuthError:
                errors["base"] = "invalid_auth"
            except InnosiliconApiError:
                errors["base"] = "cannot_connect"
            else:
                title = unique.split(":")[0]
                return self.async_create_entry(title=title, data={**user_input, CONF_HOST: host})

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
