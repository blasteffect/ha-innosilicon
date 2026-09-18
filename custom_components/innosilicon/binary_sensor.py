from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from .entity import InnosiliconEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["innosilicon"][entry.entry_id]
    async_add_entities([MinerOnlineSensor(coordinator, entry)])


class MinerOnlineSensor(InnosiliconEntity, BinarySensorEntity):
    _attr_name = "En ligne"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "online")

    @property
    def is_on(self):
        return self.coordinator.last_update_success and any(d.get("Status") == "Alive" for d in self.coordinator.data.get("DEVS", []))
