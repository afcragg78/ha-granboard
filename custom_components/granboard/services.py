"""granboard.new_game / undo / next_player / end_game / throw."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv, device_registry as dr

from .const import DOMAIN
from .coordinator import GranboardCoordinator
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
        vol.Optional("players", default=["Player 1"]): vol.All(cv.ensure_list, [cv.string]),
    }
)
THROW_SCHEMA = vol.Schema({**_BASE, vol.Required("segment"): cv.string})
PLAIN_SCHEMA = vol.Schema(_BASE)


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
                players=call.data["players"],
                start=call.data["start"],
                double_out=call.data["double_out"],
                rounds=call.data.get("rounds"),
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

    handlers: dict[str, tuple[Any, vol.Schema]] = {
        "new_game": (new_game, NEW_GAME_SCHEMA),
        "undo": (undo, PLAIN_SCHEMA),
        "next_player": (next_player, PLAIN_SCHEMA),
        "end_game": (end_game, PLAIN_SCHEMA),
        "throw": (throw, THROW_SCHEMA),
    }
    for name, (handler, schema) in handlers.items():
        if not hass.services.has_service(DOMAIN, name):
            hass.services.async_register(DOMAIN, name, handler, schema=schema)
