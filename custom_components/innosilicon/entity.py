from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import InnosiliconCoordinator


class InnosiliconEntity(CoordinatorEntity[InnosiliconCoordinator]):
    def __init__(self, coordinator, entry, suffix: str) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry.unique_id}_{suffix}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.unique_id)},
            name=self.entry.title,
            manufacturer="Innosilicon",
            model="A9 ZMaster",
            configuration_url=self.entry.data["host"] if self.entry.data["host"].startswith("http") else f"http://{self.entry.data['host']}",
        )
