from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature, PERCENTAGE

from .entity import InnosiliconEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["innosilicon"][entry.entry_id]
    entities = [
        TotalHashrateSensor(coordinator, entry),
        TotalHashrateWindowSensor(coordinator, entry, "1m", "MHS 1m"),
        TotalHashrateWindowSensor(coordinator, entry, "5m", "MHS 5m"),
        TotalHashrateWindowSensor(coordinator, entry, "15m", "MHS 15m"),
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
            BoardHashrateWindowSensor(coordinator, entry, idx, "1m", "MHS 1m"),
            BoardHashrateWindowSensor(coordinator, entry, idx, "5m", "MHS 5m"),
            BoardHashrateWindowSensor(coordinator, entry, idx, "15m", "MHS 15m"),
            BoardTemperatureSensor(coordinator, entry, idx),
        ])
    for idx, _pool in enumerate(coordinator.data.get("POOLS", []), start=1):
        entities.extend([
            PoolUrlSensor(coordinator, entry, idx),
            PoolUserSensor(coordinator, entry, idx),
            PoolStatusSensor(coordinator, entry, idx),
            PoolAcceptedSensor(coordinator, entry, idx),
            PoolRejectedSensor(coordinator, entry, idx),
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


class TotalHashrateWindowSensor(InnosiliconEntity, SensorEntity):
    _attr_native_unit_of_measurement = "KSol/s"
    _attr_icon = "mdi:chart-line"

    def __init__(self, coordinator, entry, window: str, key: str):
        super().__init__(coordinator, entry, f"hashrate_{window}")
        self.key = key
        self._attr_name = f"Hashrate {window}"

    @property
    def native_value(self):
        total = sum(float(d.get(self.key, 0) or 0) for d in self.coordinator.data.get("DEVS", []))
        return round(total, 3)


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


class BoardHashrateWindowSensor(InnosiliconEntity, SensorEntity):
    _attr_native_unit_of_measurement = "KSol/s"
    _attr_icon = "mdi:chart-line"

    def __init__(self, coordinator, entry, board, window: str, key: str):
        super().__init__(coordinator, entry, f"board_{board}_hashrate_{window}")
        self.board = board
        self.key = key
        self._attr_name = f"Hashboard {board} hashrate {window}"

    def _dev(self):
        devs = self.coordinator.data.get("DEVS", [])
        return next((d for d in devs if int(d.get("ASC", d.get("ID", -1))) + 1 == self.board), {})

    @property
    def native_value(self):
        return round(float(self._dev().get(self.key, 0) or 0), 3)


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


class PoolDetailSensor(InnosiliconEntity, SensorEntity):
    _attr_icon = "mdi:server-network"

    def __init__(self, coordinator, entry, pool: int, suffix: str, name: str):
        super().__init__(coordinator, entry, f"pool_{pool}_{suffix}")
        self.pool = pool
        self._attr_name = f"Pool {pool} {name}"

    def _pool(self):
        pools = self.coordinator.data.get("POOLS", [])
        if len(pools) < self.pool:
            return {}
        return pools[self.pool - 1]


class PoolUrlSensor(PoolDetailSensor):
    def __init__(self, coordinator, entry, pool: int):
        super().__init__(coordinator, entry, pool, "url", "URL")

    @property
    def native_value(self):
        pool = self._pool()
        return pool.get("Stratum URL") or pool.get("URL")


class PoolUserSensor(PoolDetailSensor):
    _attr_icon = "mdi:account"

    def __init__(self, coordinator, entry, pool: int):
        super().__init__(coordinator, entry, pool, "user", "user")

    @property
    def native_value(self):
        return self._pool().get("User")


class PoolStatusSensor(PoolDetailSensor):
    _attr_icon = "mdi:connection"

    def __init__(self, coordinator, entry, pool: int):
        super().__init__(coordinator, entry, pool, "status", "status")

    @property
    def native_value(self):
        pool = self._pool()
        if pool.get("Stratum Active"):
            return "Actif"
        return pool.get("Status") or "Inactif"


class PoolAcceptedSensor(PoolDetailSensor):
    _attr_icon = "mdi:check-circle-outline"

    def __init__(self, coordinator, entry, pool: int):
        super().__init__(coordinator, entry, pool, "accepted", "accepted")

    @property
    def native_value(self):
        return int(self._pool().get("Accepted", 0) or 0)


class PoolRejectedSensor(PoolDetailSensor):
    _attr_icon = "mdi:close-circle-outline"

    def __init__(self, coordinator, entry, pool: int):
        super().__init__(coordinator, entry, pool, "rejected", "rejected")

    @property
    def native_value(self):
        return int(self._pool().get("Rejected", 0) or 0)
