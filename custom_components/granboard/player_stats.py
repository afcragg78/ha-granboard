"""Keys and entity-id suffixes for Influx-friendly career sensors. Pure Python."""

from __future__ import annotations

import re
from dataclasses import dataclass


def slugify(text: str) -> str:
    """Match Home Assistant's usual object-id slug (ascii names)."""
    return re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")


@dataclass(frozen=True)
class PlayerStat:
    """One numeric career sensor, created once per saved profile."""

    key: str
    suffix: str
    name: str
    translation_key: str
    state_class: str
    unit: str | None
    icon: str
    precision: int | None


# suffix is the entity-id tail after the slugged player name, e.g. andrew_3_dart_average
PLAYER_STATS: tuple[PlayerStat, ...] = (
    PlayerStat("three_dart_avg", "3_dart_average", "3-Dart Average", "player_3_dart_average", "measurement", None, "mdi:target", 2),
    PlayerStat("first_9_avg", "first_9_average", "First 9 Average", "player_first_9_average", "measurement", None, "mdi:numeric-9-box", 2),
    PlayerStat("checkout_pct", "checkout_percent", "Checkout Percent", "player_checkout_percent", "measurement", "percent", "mdi:bullseye", 1),
    PlayerStat("one_eighties", "180s", "180s", "player_180s", "total", None, "mdi:star-four-points", None),
    PlayerStat("ton_plus", "ton_plus", "Ton Plus", "player_ton_plus", "total", None, "mdi:chevron-triple-up", None),
    PlayerStat("games", "games_played", "Games Played", "player_games_played", "total", None, "mdi:scoreboard", None),
    PlayerStat("wins", "games_won", "Games Won", "player_games_won", "total", None, "mdi:trophy", None),
    PlayerStat("cricket_mpr", "cricket_mpr", "Cricket MPR", "player_cricket_mpr", "measurement", None, "mdi:chart-timeline-variant", 2),
    PlayerStat("highest_checkout", "highest_checkout", "Highest Checkout", "player_highest_checkout", "measurement", None, "mdi:arrow-collapse-down", 0),
)

LAST_VISIT_KEY = "last_visit_score"
LAST_DART_KEY = "last_dart_score"


def player_object_id(player_name: str, suffix: str) -> str:
    slug = slugify(player_name)
    if not slug:
        slug = "player"
    return f"{slug}_{suffix}"


def player_entity_id(device_object_id: str, player_name: str, suffix: str) -> str:
    """Full entity id, e.g. sensor.game_room_granboard_3s_andrew_3_dart_average."""
    return f"sensor.{slugify(device_object_id)}_{player_object_id(player_name, suffix)}"


def board_entity_id(device_object_id: str, key: str) -> str:
    return f"sensor.{slugify(device_object_id)}_{key}"
