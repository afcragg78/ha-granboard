"""Last hit, last raw frame, RSSI, and the game."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import MATCH_ALL, SIGNAL_STRENGTH_DECIBELS_MILLIWATT, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import GranboardConfigEntry
from .entity import GranboardEntity
from .game import STATUS_FINISHED, STATUS_IDLE, STATUS_PLAYING


async def async_setup_entry(hass: HomeAssistant, entry: GranboardConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        [
            LastHitSensor(coordinator, "last_hit"),
            LastRawSensor(coordinator, "last_raw"),
            RssiSensor(coordinator, "rssi"),
            GameSensor(coordinator, "game"),
        ]
    )


class LastHitSensor(GranboardEntity, SensorEntity):
    _attr_icon = "mdi:bullseye-arrow"
    # Each dart is in the logbook via the event; keep the recorder lean.
    _unrecorded_attributes = frozenset({"raw", "time"})

    @property
    def native_value(self) -> str | None:
        hit = self.coordinator.data.last_hit
        return hit.segment if hit else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        if data.last_hit is None:
            return {}
        return {**data.last_hit.as_dict(), "time": data.last_hit_time.isoformat() if data.last_hit_time else None}


class LastRawSensor(GranboardEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:code-tags"

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.last_raw


class RssiSensor(GranboardEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data.rssi


class GameSensor(GranboardEntity, SensorEntity):
    """State is idle / playing / finished; attributes are the whole game."""

    _attr_icon = "mdi:scoreboard"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [STATUS_IDLE, STATUS_PLAYING, STATUS_FINISHED]
    # Game state is large and changes every dart; never write it to the database.
    _unrecorded_attributes = frozenset({MATCH_ALL})

    @property
    def native_value(self) -> str:
        return self.coordinator.game.status

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self.coordinator.game.as_dict()
