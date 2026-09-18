from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature, PERCENTAGE

from .entity import InnosiliconEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["innosilicon"][entry.entry_id]
    entities = [
        TotalHashrateSensor(coordinator, entry),
        FanDutySensor(coordinator, entry),
        PoolSensor(coordinator, entry),
        AggregateSensor(coordinator, entry, "accepted", "Accepted", "Accepted"),
        AggregateSensor(coordinator, entry, "rejected", "Rejected", "Rejected"),
        AggregateSensor(coordinator, entry, "hardware_errors", "Hardware errors", "Hardware Errors"),
    ]
    for dev in coordinator.data.get("DEVS", []):
        idx = int(dev.get("ASC", dev.get("ID", 0))) + 1
        entities.extend([
            BoardHashrateSensor(coordinator, entry, idx),
            BoardTemperatureSensor(coordinator, entry, idx),
        ])
    async_add_entities(entities)


class TotalHashrateSensor(InnosiliconEntity, SensorEntity):
    _attr_name = "Hashrate total"
    _attr_native_unit_of_measurement = "KSol/s"
    _attr_icon = "mdi:pickaxe"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "total_hashrate")

    @property
    def native_value(self):
        return round(float(self.coordinator.data.get("TotalHash", {}).get("Hash Rate", 0)), 3)


class BoardHashrateSensor(InnosiliconEntity, SensorEntity):
    _attr_native_unit_of_measurement = "KSol/s"
    _attr_icon = "mdi:chip"

    def __init__(self, coordinator, entry, board):
        super().__init__(coordinator, entry, f"board_{board}_hashrate")
        self.board = board
        self._attr_name = f"Hashboard {board} hashrate"

    def _dev(self):
        devs = self.coordinator.data.get("DEVS", [])
        return next((d for d in devs if int(d.get("ASC", d.get("ID", -1))) + 1 == self.board), {})

    @property
    def native_value(self):
        return round(float(self._dev().get("Hash Rate", 0)), 3)

    @property
    def extra_state_attributes(self):
        d = self._dev()
        return {
            "status": d.get("Status"),
            "1_min": d.get("MHS 1m"),
            "5_min": d.get("MHS 5m"),
            "15_min": d.get("MHS 15m"),
            "accepted": d.get("Accepted"),
            "rejected": d.get("Rejected"),
            "hardware_errors": d.get("Hardware Errors"),
        }


class BoardTemperatureSensor(InnosiliconEntity, SensorEntity):
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = "temperature"
    _attr_state_class = "measurement"

    def __init__(self, coordinator, entry, board):
        super().__init__(coordinator, entry, f"board_{board}_temperature")
        self.board = board
        self._attr_name = f"Hashboard {board} température"

    @property
    def native_value(self):
        devs = self.coordinator.data.get("DEVS", [])
        d = next((x for x in devs if int(x.get("ASC", x.get("ID", -1))) + 1 == self.board), {})
        return d.get("Temperature")


class FanDutySensor(InnosiliconEntity, SensorEntity):
    _attr_name = "Ventilateur"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:fan"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "fan_duty")

    @property
    def native_value(self):
        return self.coordinator.data.get("HARDWARE", {}).get("Fan duty")


class AggregateSensor(InnosiliconEntity, SensorEntity):
    def __init__(self, coordinator, entry, suffix, name, key):
        super().__init__(coordinator, entry, suffix)
        self._attr_name = name
        self.key = key

    @property
    def native_value(self):
        return sum(int(d.get(self.key, 0) or 0) for d in self.coordinator.data.get("DEVS", []))


class PoolSensor(InnosiliconEntity, SensorEntity):
    _attr_name = "Pool active"
    _attr_icon = "mdi:server-network"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "active_pool")

    @property
    def native_value(self):
        pools = self.coordinator.data.get("POOLS", [])
        pool = next((p for p in pools if p.get("Stratum Active")), None)
        return pool.get("Stratum URL") if pool else "Aucune"

    @property
    def extra_state_attributes(self):
        pools = self.coordinator.data.get("POOLS", [])
        pool = next((p for p in pools if p.get("Stratum Active")), None)
        if not pool:
            return {}
        return {"url": pool.get("URL"), "user": pool.get("User"), "accepted": pool.get("Accepted"), "rejected": pool.get("Rejected")}
