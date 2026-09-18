from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import InnosiliconApi, InnosiliconApiError
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class InnosiliconCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, api: InnosiliconApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Innosilicon Miner",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        try:
            return await self.api.summary()
        except InnosiliconApiError as err:
            raise UpdateFailed(str(err)) from err
