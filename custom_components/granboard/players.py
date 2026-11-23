"""Saved player profiles, lineup, and first-run seeding. Pure Python plus a Store helper."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .colors import parse_color, player_color

STORAGE_KEY = "granboard.players"
STORAGE_VERSION = 1
HELPER_PLAYERS = "input_text.darts_players"
HELPER_COLORS = "input_text.darts_colors"
GUEST_NAMES = frozenset({"guest"})
MAX_PROFILES = 40
MAX_NAME = 32
MAX_INITIALS = 3
MAX_AVATAR = 255


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def make_id() -> str:
    return uuid4().hex


def is_guest_name(name: str) -> bool:
    return name.strip().lower() in GUEST_NAMES


def initials_from_name(name: str) -> str:
    parts = [p for p in name.replace("-", " ").replace("_", " ").split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        word = "".join(c for c in parts[0] if c.isalnum()) or parts[0]
        return word[:2].upper()
    return "".join(p[0] for p in parts[:MAX_INITIALS] if p).upper()


def _clean_name(name: object) -> str:
    text = " ".join(str(name or "").strip().split())
    if not text:
        raise ProfileError("Player name is empty")
    if len(text) > MAX_NAME:
        raise ProfileError(f"Player name must be {MAX_NAME} characters or fewer")
    if is_guest_name(text):
        raise ProfileError("Guest is a one-night slot and cannot be saved as a profile")
    return text


def _clean_initials(value: object, name: str) -> str:
    text = "".join(str(value or "").split())
    if not text:
        return initials_from_name(name)
    if len(text) > MAX_INITIALS:
        raise ProfileError(f"Initials must be {MAX_INITIALS} characters or fewer")
    return text.upper()


def _clean_avatar(value: object) -> str:
    text = str(value or "").strip()
    if len(text) > MAX_AVATAR:
        raise ProfileError("Avatar path is too long")
    return text


def _clean_color(value: object, index: int = 0) -> str:
    if value is None or value == "":
        return player_color(index)
    parsed = parse_color(value)
    if parsed is None:
        raise ProfileError(f"Unknown color {value!r}; use #RRGGBB, [r, g, b] or a name like red")
    return parsed


class ProfileError(ValueError):
    """A profile service was called with options that cannot be saved."""


@dataclass
class Profile:
    id: str
    name: str
    color: str
    initials: str
    avatar: str = ""
    archived: bool = False
    created: str = ""
    updated: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def public(self, stats: dict[str, Any] | None = None) -> dict[str, Any]:
        data = {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "initials": self.initials,
            "avatar": self.avatar or None,
            "archived": self.archived,
        }
        if stats is not None:
            data["stats"] = stats
        return data


@dataclass
class LineupSlot:
    """A throwing-order slot: a saved profile, or a one-night Guest."""

    player_id: str | None = None
    name: str = "Guest"
    color: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {"player_id": self.player_id, "name": self.name, "color": self.color}


class PlayerDirectory:
    """In-memory profiles and lineup, loaded from ``.storage/granboard.players``."""

    def __init__(self) -> None:
        self.profiles: list[Profile] = []
        self.lineup: list[LineupSlot] = []
        self._seeded = False

    # ------------------------------------------------------------ lookup
    def get(self, player_id: str) -> Profile | None:
        for profile in self.profiles:
            if profile.id == player_id:
                return profile
        return None

    def find_name(self, name: str, *, include_archived: bool = False) -> Profile | None:
        needle = name.strip().lower()
        if not needle:
            return None
        for profile in self.profiles:
            if profile.name.lower() == needle and (include_archived or not profile.archived):
                return profile
        return None

    def active(self) -> list[Profile]:
        return [p for p in self.profiles if not p.archived]

    def active_count(self) -> int:
        return len(self.active())

    def require(self, player_id: str) -> Profile:
        profile = self.get(player_id)
        if profile is None:
            raise ProfileError(f"No player profile {player_id}")
        return profile

    # ------------------------------------------------------------ mutate
    def add_player(
        self,
        name: str,
        *,
        color: object = None,
        initials: object = None,
        avatar: object = None,
        player_id: str | None = None,
        created: str | None = None,
    ) -> Profile:
        name = _clean_name(name)
        if self.find_name(name):
            raise ProfileError(f"A player named {name!r} already exists")
        if len(self.active()) >= MAX_PROFILES:
            raise ProfileError(f"At most {MAX_PROFILES} saved players")
        now = utc_now()
        profile = Profile(
            id=player_id or make_id(),
            name=name,
            color=_clean_color(color, len(self.active())),
            initials=_clean_initials(initials, name),
            avatar=_clean_avatar(avatar),
            archived=False,
            created=created or now,
            updated=now,
        )
        if self.get(profile.id):
            raise ProfileError("That player id is already in use")
        self.profiles.append(profile)
        return profile

    def update_player(
        self,
        player_id: str,
        *,
        name: object = None,
        color: object = None,
        initials: object = None,
        avatar: object = None,
        archived: bool | None = None,
    ) -> Profile:
        profile = self.require(player_id)
        if name is not None:
            cleaned = _clean_name(name)
            other = self.find_name(cleaned, include_archived=True)
            if other is not None and other.id != profile.id and not other.archived:
                raise ProfileError(f"A player named {cleaned!r} already exists")
            profile.name = cleaned
        if color is not None and color != "":
            profile.color = _clean_color(color)
        if initials is not None:
            profile.initials = _clean_initials(initials, profile.name)
        if avatar is not None:
            profile.avatar = _clean_avatar(avatar)
        if archived is not None:
            profile.archived = bool(archived)
            if profile.archived:
                self.lineup = [slot for slot in self.lineup if slot.player_id != profile.id]
        profile.updated = utc_now()
        return profile

    def remove_player(self, player_id: str) -> Profile:
        """Archive a profile so past games keep their player id."""
        return self.update_player(player_id, archived=True)

    # ------------------------------------------------------------ lineup
    def set_lineup(self, players: list[object], colors: list[object] | None = None) -> list[LineupSlot]:
        if len(players) > 8:
            raise ProfileError("At most 8 players in a game")
        colors = list(colors or [])
        slots: list[LineupSlot] = []
        for index, raw in enumerate(players):
            given = colors[index] if index < len(colors) else None
            slots.append(self._slot_from(raw, given, index))
        self.lineup = slots
        return slots

    def _slot_from(self, raw: object, given: object, index: int) -> LineupSlot:
        if isinstance(raw, dict):
            player_id = raw.get("player_id") or raw.get("id")
            name = str(raw.get("name") or "").strip()
            color = raw.get("color", given)
            if player_id:
                profile = self.require(str(player_id))
                if profile.archived:
                    raise ProfileError(f"{profile.name} has been removed")
                return LineupSlot(player_id=profile.id, name=profile.name, color=profile.color)
            raw = name or "Guest"
            given = color if color is not None else given
        text = str(raw or "").strip()
        if not text:
            raise ProfileError("Player name is empty")
        profile = self.get(text) or self.find_name(text)
        if profile is not None:
            if profile.archived:
                raise ProfileError(f"{profile.name} has been removed")
            return LineupSlot(player_id=profile.id, name=profile.name, color=profile.color)
        color = _clean_color(given, index) if given not in (None, "") else player_color(index)
        return LineupSlot(player_id=None, name=text, color=color)

    def resolve_players(self, players: list[object] | None, colors: list[object] | None = None) -> list[dict[str, Any]]:
        """Turn profile ids, names, or the saved lineup into ``new_game`` player dicts."""
        if players is None:
            if self.lineup:
                specs = list(self.lineup)
            else:
                specs = [LineupSlot(name="Player 1", color=player_color(0))]
        else:
            if len(players) > 8:
                raise ProfileError("At most 8 players in a game")
            colors = list(colors or [])
            specs = [self._slot_from(raw, colors[i] if i < len(colors) else None, i) for i, raw in enumerate(players)]
            if not specs:
                specs = [LineupSlot(name="Player 1", color=player_color(0))]
        resolved: list[dict[str, Any]] = []
        for index, slot in enumerate(specs):
            if slot.player_id:
                profile = self.get(slot.player_id)
                if profile is None or profile.archived:
                    raise ProfileError("A selected player profile is missing")
                resolved.append({"name": profile.name, "color": profile.color, "profile_id": profile.id})
            else:
                name = slot.name.strip() or "Guest"
                resolved.append({"name": name, "color": slot.color or player_color(index), "profile_id": None})
        return resolved

    def lineup_public(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for index, slot in enumerate(self.lineup):
            if slot.player_id:
                profile = self.get(slot.player_id)
                if profile is not None:
                    rows.append(
                        {
                            "player_id": profile.id,
                            "name": profile.name,
                            "color": profile.color,
                            "initials": profile.initials,
                            "avatar": profile.avatar or None,
                            "guest": False,
                        }
                    )
                    continue
            rows.append(
                {
                    "player_id": None,
                    "name": slot.name or "Guest",
                    "color": slot.color or player_color(index),
                    "initials": initials_from_name(slot.name or "Guest"),
                    "avatar": None,
                    "guest": True,
                }
            )
        return rows

    # ------------------------------------------------------------ seed
    def seed_from_states(self, states: Any) -> bool:
        """Create profiles from ``input_text.darts_players`` on first run. Guest is skipped."""
        if self.profiles or self._seeded:
            return False
        get = getattr(states, "get", None)
        state = get(HELPER_PLAYERS) if callable(get) else None
        if state is None:
            return False
        raw = getattr(state, "state", None)
        if raw in (None, "", "unknown", "unavailable"):
            self._seeded = True
            return False
        names = [p.strip() for p in str(raw).split(",") if p.strip()]
        colors_state = get(HELPER_COLORS) if callable(get) else None
        color_raw = getattr(colors_state, "state", "") if colors_state is not None else ""
        colors = [c.strip() for c in str(color_raw or "").split(",")]
        added = False
        guest_color = None
        for index, name in enumerate(names):
            given = colors[index] if index < len(colors) and colors[index] else None
            if is_guest_name(name):
                guest_color = given
                continue
            try:
                self.add_player(name, color=given)
                added = True
            except ProfileError:
                continue
        self._seeded = True
        if added and not self.lineup:
            lineup: list[object] = [p.id for p in self.active()]
            # Keep a Guest slot at the end when the helper had one, so tonight's lineup still matches.
            if any(is_guest_name(n) for n in names):
                lineup.append({"name": "Guest", "color": guest_color or player_color(len(lineup))})
            try:
                self.set_lineup(lineup)
            except ProfileError:
                pass
        return added

    # ------------------------------------------------------------ persistence
    def dump(self) -> dict[str, Any]:
        return {
            "profiles": [p.as_dict() for p in self.profiles],
            "lineup": [s.as_dict() for s in self.lineup],
            "seeded": self._seeded,
        }

    @classmethod
    def load(cls, data: dict[str, Any] | None) -> PlayerDirectory:
        directory = cls()
        if not data:
            return directory
        try:
            for row in data.get("profiles") or []:
                directory.profiles.append(Profile(**{k: row[k] for k in Profile.__dataclass_fields__ if k in row}))
            for row in data.get("lineup") or []:
                directory.lineup.append(
                    LineupSlot(
                        player_id=row.get("player_id"),
                        name=str(row.get("name") or "Guest"),
                        color=row.get("color"),
                    )
                )
            directory._seeded = bool(data.get("seeded"))
        except (TypeError, ValueError, KeyError):
            return cls()
        return directory


async def async_setup_profile_stores(hass: Any) -> dict[str, Any]:
    """Load the shared profile and career stores once."""
    from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
    from homeassistant.helpers.storage import Store

    from .career import CAREER_STORAGE_KEY, CAREER_STORAGE_VERSION, CareerLog
    from .const import DOMAIN

    data = hass.data.setdefault(DOMAIN, {})
    if "players" in data:
        return data
    players_store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    career_store = Store(hass, CAREER_STORAGE_VERSION, CAREER_STORAGE_KEY)
    data["players_store"] = players_store
    data["career_store"] = career_store
    data["players"] = PlayerDirectory.load(await players_store.async_load())
    data["career"] = CareerLog.load(await career_store.async_load())

    def _seed(_event: Any = None) -> None:
        directory: PlayerDirectory = data["players"]
        if directory.seed_from_states(hass.states):
            players_store.async_delay_save(directory.dump, 1)

    if getattr(hass, "is_running", False):
        _seed()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _seed)
    return data


def get_profile_data(hass: Any) -> dict[str, Any]:
    from .const import DOMAIN

    return hass.data[DOMAIN]
