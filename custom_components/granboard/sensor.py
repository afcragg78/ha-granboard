"""Last hit, last raw frame, RSSI, the game, and Influx-friendly career stats."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import MATCH_ALL, PERCENTAGE, SIGNAL_STRENGTH_DECIBELS_MILLIWATT, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import GranboardConfigEntry, GranboardCoordinator
from .entity import GranboardEntity
from .game import STATUS_FINISHED, STATUS_IDLE, STATUS_PLAYING
from .player_stats import LAST_DART_KEY, LAST_VISIT_KEY, PLAYER_STATS, PlayerStat, player_object_id


async def async_setup_entry(hass: HomeAssistant, entry: GranboardConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        [
            LastHitSensor(coordinator, "last_hit"),
            LastRawSensor(coordinator, "last_raw"),
            RssiSensor(coordinator, "rssi"),
            GameSensor(coordinator, "game"),
            PlayersSensor(coordinator, "players"),
            LastVisitScoreSensor(coordinator, LAST_VISIT_KEY),
            LastDartScoreSensor(coordinator, LAST_DART_KEY),
        ]
    )

    known: dict[tuple[str, str], PlayerStatSensor] = {}

    @callback
    def _sync_player_sensors() -> None:
        current = {profile.id: profile for profile in coordinator.directory.profiles if not profile.archived}
        new: list[PlayerStatSensor] = []
        for player_id, profile in current.items():
            for stat in PLAYER_STATS:
                ident = (player_id, stat.key)
                if ident in known:
                    continue
                sensor = PlayerStatSensor(coordinator, player_id, stat)
                known[ident] = sensor
                new.append(sensor)
        stale = [ident for ident in known if ident[0] not in current]
        for ident in stale:
            sensor = known.pop(ident)
            if sensor.hass is not None:
                hass.async_create_task(sensor.async_remove())
        if new:
            async_add_entities(new)

    _sync_player_sensors()
    entry.async_on_unload(coordinator.async_on_profiles_changed(_sync_player_sensors))


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


class PlayersSensor(GranboardEntity, SensorEntity):
    """Saved profiles, the current lineup, and career stats."""

    _attr_icon = "mdi:account-group"
    # Career stats and the profile list change often enough; keep the recorder lean.
    _unrecorded_attributes = frozenset({MATCH_ALL})

    @property
    def native_value(self) -> int:
        return self.coordinator.directory.active_count()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        directory = self.coordinator.directory
        career = self.coordinator.career
        return {
            "profiles": [profile.public(career.stats_for(profile.id)) for profile in directory.profiles],
            "lineup": directory.lineup_public(),
        }


class _LazyCoordinatorSensor(GranboardEntity, SensorEntity):
    """A coordinator entity that only writes state when `_should_publish` says so."""

    def _handle_coordinator_update(self) -> None:
        if self._should_publish():
            self.async_write_ha_state()

    def _should_publish(self) -> bool:
        return True


class LastVisitScoreSensor(_LazyCoordinatorSensor):
    """Numeric turn total, written once when a visit ends (or the game does)."""

    _attr_icon = "mdi:counter"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _unrecorded_attributes = frozenset({"darts"})

    def __init__(self, coordinator: GranboardCoordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._last_seq = 0

    def _should_publish(self) -> bool:
        seq = self.coordinator.visit_seq
        if seq == self._last_seq:
            return False
        self._last_seq = seq
        return True

    @property
    def native_value(self) -> int | None:
        visit = self.coordinator.last_visit
        return None if visit is None else int(visit.get("score") or 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        visit = self.coordinator.last_visit
        if not visit:
            return {}
        return {
            "player": visit.get("player"),
            "player_id": visit.get("player_id"),
            "bust": visit.get("bust"),
            "dart_count": visit.get("dart_count"),
            "round": visit.get("round"),
            "last_dart_segment": visit.get("last_dart_segment"),
        }


class LastDartScoreSensor(_LazyCoordinatorSensor):
    """Score of the last dart in the visit that just ended."""

    _attr_icon = "mdi:bullseye"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: GranboardCoordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._last_seq = 0

    def _should_publish(self) -> bool:
        seq = self.coordinator.visit_seq
        if seq == self._last_seq:
            return False
        self._last_seq = seq
        return True

    @property
    def native_value(self) -> int | None:
        visit = self.coordinator.last_visit
        return None if visit is None else int(visit.get("last_dart_score") or 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        visit = self.coordinator.last_visit
        if not visit:
            return {}
        return {
            "player": visit.get("player"),
            "player_id": visit.get("player_id"),
            "segment": visit.get("last_dart_segment"),
            "visit_score": visit.get("score"),
            "bust": visit.get("bust"),
        }


class PlayerStatSensor(_LazyCoordinatorSensor):
    """One numeric career figure for a saved profile, cheap to keep in Influx."""

    def __init__(self, coordinator: GranboardCoordinator, player_id: str, stat: PlayerStat) -> None:
        super().__init__(coordinator, stat.translation_key)
        self._player_id = player_id
        self._stat = stat
        self._attr_unique_id = f"{coordinator.address}_{player_id}_{stat.key}"
        self._attr_icon = stat.icon
        self._attr_suggested_object_id = self._object_id()
        if stat.state_class == "total":
            # Totals can fall when a finish is undone, so not total_increasing.
            self._attr_state_class = SensorStateClass.TOTAL
        else:
            self._attr_state_class = SensorStateClass.MEASUREMENT
        if stat.unit == "percent":
            self._attr_native_unit_of_measurement = PERCENTAGE
        if stat.precision is not None:
            self._attr_suggested_display_precision = stat.precision
        self._last_value: object = object()
        self._last_name: str | None = None

    def _profile(self):
        return self.coordinator.directory.get(self._player_id)

    def _object_id(self) -> str:
        profile = self._profile()
        name = profile.name if profile else self._player_id
        return player_object_id(name, self._stat.suffix)

    @property
    def translation_placeholders(self) -> dict[str, str]:
        profile = self._profile()
        return {"player": profile.name if profile else "Player"}

    def _should_publish(self) -> bool:
        profile = self._profile()
        name = profile.name if profile else None
        value = self.native_value
        if value == self._last_value and name == self._last_name:
            return False
        self._last_value = value
        self._last_name = name
        return True

    @property
    def available(self) -> bool:
        profile = self._profile()
        return bool(profile) and not profile.archived

    @property
    def native_value(self) -> float | int:
        stats = self.coordinator.career.stats_for(self._player_id)
        value = stats.get(self._stat.key, 0)
        if isinstance(value, float):
            places = 0 if self._stat.precision is None else self._stat.precision
            return round(value, places)
        return int(value or 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        profile = self._profile()
        if profile is None:
            return {"player_id": self._player_id}
        return {
            "player": profile.name,
            "player_id": profile.id,
            "color": profile.color,
            "initials": profile.initials,
        }
