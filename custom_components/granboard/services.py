"""granboard.new_game / undo / next_player / end_game / throw / led / player profiles."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv, device_registry as dr

from .const import DOMAIN
from .coordinator import GranboardCoordinator
from . import led
from .colors import parse_color, to_rgb
from .game import GAMES, GameError, X01_STARTS
from .protocol import parse_segment

ATTR_DEVICE_ID = "device_id"

_BASE = {vol.Optional(ATTR_DEVICE_ID): vol.Any(cv.string, [cv.string])}

NEW_GAME_SCHEMA = vol.Schema(
    {
        **_BASE,
        vol.Required("game"): vol.In([*GAMES, "301", "501", "701"]),
        vol.Optional("start", default=501): vol.All(vol.Coerce(int), vol.In(X01_STARTS)),
        vol.Optional("double_out", default=False): cv.boolean,
        vol.Optional("rounds"): vol.All(vol.Coerce(int), vol.Range(min=0, max=99)),
        vol.Optional("players"): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional("colors"): vol.All(cv.ensure_list, [vol.Any(cv.string, [vol.Coerce(int)])]),
    }
)

LED_EFFECTS = ["segment", "blink", "wave", "ring", "numbers", "clear", "sweep", "wipe", "award", "raw", "rainbow"]
LED_SCHEMA = vol.Schema(
    {
        **_BASE,
        vol.Required("effect"): vol.In(LED_EFFECTS),
        vol.Optional("segment"): cv.string,
        vol.Optional("color"): vol.Any(cv.string, [vol.Coerce(int)]),
        vol.Optional("color2"): vol.Any(cv.string, [vol.Coerce(int)]),
        vol.Optional("blinks", default=1): vol.All(vol.Coerce(int), vol.In([1, 2, 3])),
        vol.Optional("duration"): vol.All(vol.Coerce(int), vol.Range(min=1, max=255)),
        vol.Optional("numbers"): vol.All(cv.ensure_list, [vol.All(vol.Coerce(int), vol.Range(min=1, max=20))]),
        vol.Optional("award"): cv.string,
        vol.Optional("raw"): cv.string,
    }
)


def _rgb(value: Any, default: tuple[int, int, int]) -> tuple[int, int, int]:
    if value is None:
        return default
    parsed = parse_color(value)
    if parsed is None:
        raise ServiceValidationError(f"Unknown color {value!r}; use #RRGGBB, [r, g, b] or a name like red")
    return to_rgb(parsed)


def led_steps(data: dict[str, Any], player_rgb: tuple[int, int, int]) -> list[led.Step]:
    """Turn granboard.led service data into LED commands."""
    effect = data["effect"]
    color = _rgb(data.get("color"), player_rgb)
    color2 = _rgb(data.get("color2"), led.WHITE)
    duration = data.get("duration")
    try:
        if effect == "segment":
            hit = parse_segment(data.get("segment") or "")
            if data.get("color") is None and data.get("blinks", 1) == 1:
                return led.plan_hit(hit.as_dict(), color)
            if not 1 <= hit.number <= 20:
                return [(led.blink_command(color, duration or 0x14), led.MIN_GAP_MS)]
            return [(led.hit_command(hit.number, color, data.get("blinks", 1), duration or 0x14), led.MIN_GAP_MS)]
        if effect == "blink":
            return [(led.blink_command(color, duration or 0x1E), led.MIN_GAP_MS)]
        if effect == "wave":
            return [(led.wave_command(color, color2, duration or 0x05), led.MIN_GAP_MS)]
        if effect == "ring":
            return [(led.ring_command(color), led.MIN_GAP_MS)]
        if effect == "numbers":
            return [(led.numbers_command(data.get("numbers") or []), led.MIN_GAP_MS)]
        if effect == "clear":
            return [(led.clear_command(), led.MIN_GAP_MS)]
        if effect == "sweep":
            return led.sweep(color, color2 if data.get("color2") is not None else led.GREEN)
        if effect == "wipe":
            return led.turn_wipe(color)
        if effect == "rainbow":
            return [(led.rainbow_command(), led.MIN_GAP_MS)]
        if effect == "raw":
            return [(led.parse_raw(data.get("raw")), led.MIN_GAP_MS)]
        if effect == "award":
            return led.plan_award({"type": data.get("award"), "segment": data.get("segment"), "score": 50}, color)
    except ValueError as err:
        raise ServiceValidationError(str(err)) from err
    return []
THROW_SCHEMA = vol.Schema({**_BASE, vol.Required("segment"): cv.string})
PLAIN_SCHEMA = vol.Schema(_BASE)
PLAYER_NAME_SCHEMA = vol.Schema(
    {
        **_BASE,
        vol.Required("name"): cv.string,
        vol.Optional("color"): vol.Any(cv.string, [vol.Coerce(int)]),
        vol.Optional("initials"): cv.string,
        vol.Optional("avatar"): cv.string,
    }
)
PLAYER_UPDATE_SCHEMA = vol.Schema(
    {
        **_BASE,
        vol.Required("player_id"): cv.string,
        vol.Optional("name"): cv.string,
        vol.Optional("color"): vol.Any(cv.string, [vol.Coerce(int)]),
        vol.Optional("initials"): cv.string,
        vol.Optional("avatar"): cv.string,
    }
)
PLAYER_REMOVE_SCHEMA = vol.Schema({**_BASE, vol.Required("player_id"): cv.string})
LINEUP_SCHEMA = vol.Schema(
    {
        **_BASE,
        vol.Required("players"): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional("colors"): vol.All(cv.ensure_list, [vol.Any(cv.string, [vol.Coerce(int)])]),
    }
)


def _coordinator(hass: HomeAssistant, call: ServiceCall) -> GranboardCoordinator:
    entries = [e for e in hass.config_entries.async_entries(DOMAIN) if e.state is ConfigEntryState.LOADED]
    device_id = call.data.get(ATTR_DEVICE_ID)
    if isinstance(device_id, list):
        device_id = device_id[0] if device_id else None
    if device_id:
        device = dr.async_get(hass).async_get(device_id)
        entries = [e for e in entries if device and e.entry_id in device.config_entries]
    if not entries:
        raise ServiceValidationError("No Granboard is set up and loaded")
    return entries[0].runtime_data


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    async def new_game(call: ServiceCall) -> None:
        coordinator = _coordinator(hass, call)
        try:
            coordinator.new_game(
                game=call.data["game"],
                players=call.data.get("players"),
                start=call.data["start"],
                double_out=call.data["double_out"],
                rounds=call.data.get("rounds"),
                colors=call.data.get("colors"),
            )
        except GameError as err:
            raise ServiceValidationError(str(err)) from err

    async def undo(call: ServiceCall) -> None:
        _coordinator(hass, call).undo()

    async def next_player(call: ServiceCall) -> None:
        _coordinator(hass, call).next_player()

    async def end_game(call: ServiceCall) -> None:
        _coordinator(hass, call).end_game()

    async def throw(call: ServiceCall) -> None:
        try:
            hit = parse_segment(call.data["segment"])
        except ValueError as err:
            raise ServiceValidationError(str(err)) from err
        _coordinator(hass, call).record_hit(hit)

    async def led_service(call: ServiceCall) -> None:
        coordinator = _coordinator(hass, call)
        if not coordinator.can_write:
            raise ServiceValidationError("The Granboard is not connected, so its lights cannot be changed")
        game = coordinator.game
        rgb = to_rgb(game.color_of(game.current if game.status == "playing" else None))
        steps = led_steps(dict(call.data), rgb)
        # A raw test frame or looping rainbow stays on show: the LED Ring light pauses
        # until a clear, another board light action, or the light is turned on again.
        held = call.data["effect"] in ("raw", "rainbow")
        coordinator.led_hold = held and any(steps[0][0]) if steps else False
        if call.data["effect"] == "rainbow":
            coordinator.start_rainbow_sweep(hold=True)
        else:
            coordinator.led_play(steps)

    def _save_profiles(coordinator: GranboardCoordinator) -> None:
        coordinator._save_players()
        coordinator.async_update_listeners()

    async def add_player(call: ServiceCall) -> None:
        from .players import ProfileError

        coordinator = _coordinator(hass, call)
        try:
            coordinator.directory.add_player(
                call.data["name"],
                color=call.data.get("color"),
                initials=call.data.get("initials"),
                avatar=call.data.get("avatar"),
            )
        except ProfileError as err:
            raise ServiceValidationError(str(err)) from err
        _save_profiles(coordinator)

    async def update_player(call: ServiceCall) -> None:
        from .players import ProfileError

        coordinator = _coordinator(hass, call)
        try:
            coordinator.directory.update_player(
                call.data["player_id"],
                name=call.data.get("name"),
                color=call.data.get("color"),
                initials=call.data.get("initials"),
                avatar=call.data.get("avatar"),
            )
        except ProfileError as err:
            raise ServiceValidationError(str(err)) from err
        _save_profiles(coordinator)

    async def remove_player(call: ServiceCall) -> None:
        from .players import ProfileError

        coordinator = _coordinator(hass, call)
        try:
            coordinator.directory.remove_player(call.data["player_id"])
        except ProfileError as err:
            raise ServiceValidationError(str(err)) from err
        _save_profiles(coordinator)

    async def set_lineup(call: ServiceCall) -> None:
        from .players import ProfileError

        coordinator = _coordinator(hass, call)
        try:
            coordinator.directory.set_lineup(call.data["players"], call.data.get("colors"))
        except ProfileError as err:
            raise ServiceValidationError(str(err)) from err
        _save_profiles(coordinator)

    handlers: dict[str, tuple[Any, vol.Schema]] = {
        "new_game": (new_game, NEW_GAME_SCHEMA),
        "undo": (undo, PLAIN_SCHEMA),
        "next_player": (next_player, PLAIN_SCHEMA),
        "end_game": (end_game, PLAIN_SCHEMA),
        "throw": (throw, THROW_SCHEMA),
        "led": (led_service, LED_SCHEMA),
        "add_player": (add_player, PLAYER_NAME_SCHEMA),
        "update_player": (update_player, PLAYER_UPDATE_SCHEMA),
        "remove_player": (remove_player, PLAYER_REMOVE_SCHEMA),
        "set_lineup": (set_lineup, LINEUP_SCHEMA),
    }
    for name, (handler, schema) in handlers.items():
        if not hass.services.has_service(DOMAIN, name):
            hass.services.async_register(DOMAIN, name, handler, schema=schema)
