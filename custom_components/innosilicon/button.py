from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.exceptions import HomeAssistantError

from .api import InnosiliconApiError
from .const import (
    CONF_POOL_1_PASSWORD,
    CONF_POOL_1_URL,
    CONF_POOL_1_USERNAME,
    CONF_POOL_2_PASSWORD,
    CONF_POOL_2_URL,
    CONF_POOL_2_USERNAME,
    CONF_POOL_3_PASSWORD,
    CONF_POOL_3_URL,
    CONF_POOL_3_USERNAME,
)
from .entity import InnosiliconEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["innosilicon"][entry.entry_id]
    async_add_entities([
        MinerRebootButton(coordinator, entry),
        ApplyPoolsButton(coordinator, entry),
    ])


class MinerButton(InnosiliconEntity, ButtonEntity):
    def __init__(self, coordinator, entry, suffix: str) -> None:
        super().__init__(coordinator, entry, suffix)
        self.entry = entry


class MinerRebootButton(MinerButton):
    _attr_name = "Redemarrer"
    _attr_icon = "mdi:restart"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "reboot")

    async def async_press(self) -> None:
        try:
            await self.coordinator.api.reboot()
        except InnosiliconApiError as err:
            raise HomeAssistantError(f"Impossible de redemarrer le mineur: {err}") from err


class ApplyPoolsButton(MinerButton):
    _attr_name = "Appliquer les pools"
    _attr_icon = "mdi:server-network"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "apply_pools")

    @property
    def available(self) -> bool:
        return super().available and any(pool["url"] for pool in self._configured_pools())

    async def async_press(self) -> None:
        pools = self._configured_pools()
        if not any(pool["url"] for pool in pools):
            raise HomeAssistantError("Aucun pool n'est configure dans les options de l'integration")

        try:
            await self.coordinator.api.update_pools(pools)
            await self.coordinator.async_request_refresh()
        except InnosiliconApiError as err:
            raise HomeAssistantError(f"Impossible d'appliquer les pools: {err}") from err

    def _configured_pools(self) -> list[dict[str, str]]:
        options = self.entry.options
        return [
            {
                "url": options.get(CONF_POOL_1_URL, ""),
                "username": options.get(CONF_POOL_1_USERNAME, ""),
                "password": options.get(CONF_POOL_1_PASSWORD, ""),
            },
            {
                "url": options.get(CONF_POOL_2_URL, ""),
                "username": options.get(CONF_POOL_2_USERNAME, ""),
                "password": options.get(CONF_POOL_2_PASSWORD, ""),
            },
            {
                "url": options.get(CONF_POOL_3_URL, ""),
                "username": options.get(CONF_POOL_3_USERNAME, ""),
                "password": options.get(CONF_POOL_3_PASSWORD, ""),
            },
        ]
