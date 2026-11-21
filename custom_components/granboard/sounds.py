"""Which sound to play for a dart, an award or a turn. Pure Python."""

from __future__ import annotations

from collections.abc import Iterable

# Options keys, in the order Configure shows them.
SOUND_KEYS = (
    "hit", "single", "double", "triple", "triple_20", "outer_bull", "inner_bull", "miss",
    "ton", "ton_40", "high_ton", "ton_80", "hat_trick", "three_in_a_bed", "white_horse",
    "bust", "checkout", "winner", "next_player", "game_start",
)

# Highest first: one sound per dart, the most important one that has a file.
AWARD_PRIORITY = (
    "winner", "checkout", "bust", "ton_80", "hat_trick", "white_horse", "three_in_a_bed",
    "high_ton", "ton_40", "ton",
)

MAX_VOLUME = 0.6  # never louder than 60 % (the Onkyo rule); applies to every player


def _hit_keys(hit: dict) -> list[str]:
    ring = hit.get("ring")
    if ring == "bullseye":
        return ["inner_bull", "hit"]
    if ring == "bull":
        return ["outer_bull", "hit"]
    if ring == "miss":
        return ["miss"]
    if ring == "treble":
        return (["triple_20"] if hit.get("number") == 20 else []) + ["triple", "hit"]
    if ring == "double":
        return ["double", "hit"]
    if ring in ("single_inner", "single_outer"):
        return ["single", "hit"]
    return []


def award_keys(awards: Iterable[dict]) -> list[str]:
    kinds = {a.get("type") for a in awards}
    return [k for k in AWARD_PRIORITY if k in kinds]


def pick_sound(sounds: dict[str, str], hit: dict | None = None, awards: Iterable[dict] = (), event: str | None = None) -> str | None:
    """Return the sound key to play, or None. Awards beat the plain hit sound."""
    candidates: list[str] = []
    if event:
        candidates.append(event)
    candidates += award_keys(awards)
    if hit is not None:
        candidates += _hit_keys(hit)
    for key in candidates:
        if str(sounds.get(key) or "").strip():
            return key
    return None


def volume_level(percent: object) -> float | None:
    """Options store 0-100; None or blank means leave the player's volume alone. Capped at 60 %."""
    if percent in (None, ""):
        return None
    try:
        value = float(percent)
    except (TypeError, ValueError):
        return None
    if value < 0:
        return None
    return round(min(value / 100.0, MAX_VOLUME), 2)
