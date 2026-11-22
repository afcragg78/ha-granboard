"""Which sound to play for a dart, an award or a turn. Pure Python."""

from __future__ import annotations

import random
from collections.abc import Iterable
from pathlib import Path

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

THEME_OFF = "Off"
DEFAULT_THEME = "default"
AUDIO_SUFFIXES = {".mp3", ".wav", ".ogg"}
SOUNDS_WWW_SUBPATH = "www/granboard/sounds"


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


def candidate_keys(hit: dict | None = None, awards: Iterable[dict] = (), event: str | None = None) -> list[str]:
    """Trigger keys to try, same order as pick_sound (event, then awards, then the hit chain)."""
    keys: list[str] = []
    if event:
        keys.append(event)
    keys += award_keys(awards)
    if hit is not None:
        keys += _hit_keys(hit)
    return keys


def _safe_folder(name: str) -> bool:
    if not name or name in {".", ".."} or name.startswith("."):
        return False
    if "/" in name or "\\" in name or name.lower() == THEME_OFF.lower():
        return False
    return True


def list_theme_names(root: Path | None) -> list[str]:
    """Theme folders under the sounds root, sorted, excluding Off and hidden names."""
    if root is None or not root.is_dir():
        return []
    names = [p.name for p in root.iterdir() if p.is_dir() and _safe_folder(p.name)]
    return sorted(names, key=str.casefold)


def theme_options(root: Path | None, current: str | None = None) -> list[str]:
    """Select options: Off, then discovered themes, plus the current value if it is missing."""
    options = [THEME_OFF]
    for name in list_theme_names(root):
        if name not in options:
            options.append(name)
    if current and current not in options:
        options.append(current)
    return options


def list_clips(root: Path | None, theme: str, key: str) -> list[Path]:
    """Audio files in <root>/<theme>/<key>/ (mp3, wav, ogg)."""
    if root is None or not _safe_folder(theme) or not _safe_folder(key):
        return []
    folder = root / theme / key
    if not folder.is_dir():
        return []
    files = [
        path
        for path in folder.iterdir()
        if path.is_file() and not path.name.startswith(".") and path.suffix.lower() in AUDIO_SUFFIXES
    ]
    return sorted(files, key=lambda path: path.name.casefold())


def clip_url(theme: str, key: str, filename: str) -> str:
    return f"/local/granboard/sounds/{theme}/{key}/{filename}"


def pick_sound_clip(
    root: Path | None,
    theme: str | None,
    sounds: dict[str, str],
    *,
    hit: dict | None = None,
    awards: Iterable[dict] = (),
    event: str | None = None,
    rng: random.Random | None = None,
) -> tuple[str, str, str | None] | None:
    """Pick (key, url, folder_theme_or_none).

    For each candidate key, try the current theme folder, then ``default``, then the
    Configure single-file path. Then try the next key in the existing fallback chain.
    Theme Off (or empty) skips folders and uses only the Configure paths.
    """
    choose = (rng or random).choice
    use_theme = bool(theme) and theme != THEME_OFF and _safe_folder(theme or "")
    layers: list[str] = []
    if use_theme and theme is not None:
        layers.append(theme)
        if theme != DEFAULT_THEME:
            layers.append(DEFAULT_THEME)
    for key in candidate_keys(hit=hit, awards=awards, event=event):
        if not _safe_folder(key) and key != "Off":
            # SOUND_KEYS are all safe; still guard path joins
            if not key or "/" in key or "\\" in key or key.startswith("."):
                continue
        for folder in layers:
            clips = list_clips(root, folder, key)
            if clips:
                chosen = choose(clips)
                return key, clip_url(folder, key, chosen.name), folder
        url = str(sounds.get(key) or "").strip()
        if url:
            return key, url, None
    return None
