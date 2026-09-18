from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import InnosiliconApi, InnosiliconApiError, InnosiliconAuthError
from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_POOL_1_PASSWORD,
    CONF_POOL_1_URL,
    CONF_POOL_1_USERNAME,
    CONF_POOL_2_PASSWORD,
    CONF_POOL_2_URL,
    CONF_POOL_2_USERNAME,
    CONF_POOL_3_PASSWORD,
    CONF_POOL_3_URL,
    CONF_POOL_3_USERNAME,
    CONF_USERNAME,
    DEFAULT_USERNAME,
    DOMAIN,
)


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

    @staticmethod
    def async_get_options_flow(config_entry):
        return InnosiliconOptionsFlow(config_entry)


class InnosiliconOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Optional(CONF_POOL_1_URL, default=options.get(CONF_POOL_1_URL, "")): str,
                vol.Optional(CONF_POOL_1_USERNAME, default=options.get(CONF_POOL_1_USERNAME, "")): str,
                vol.Optional(CONF_POOL_1_PASSWORD, default=options.get(CONF_POOL_1_PASSWORD, "")): str,
                vol.Optional(CONF_POOL_2_URL, default=options.get(CONF_POOL_2_URL, "")): str,
                vol.Optional(CONF_POOL_2_USERNAME, default=options.get(CONF_POOL_2_USERNAME, "")): str,
                vol.Optional(CONF_POOL_2_PASSWORD, default=options.get(CONF_POOL_2_PASSWORD, "")): str,
                vol.Optional(CONF_POOL_3_URL, default=options.get(CONF_POOL_3_URL, "")): str,
                vol.Optional(CONF_POOL_3_USERNAME, default=options.get(CONF_POOL_3_USERNAME, "")): str,
                vol.Optional(CONF_POOL_3_PASSWORD, default=options.get(CONF_POOL_3_PASSWORD, "")): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
