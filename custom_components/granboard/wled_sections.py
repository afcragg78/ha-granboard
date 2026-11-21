"""Run WLED Sections plans against real lights.

- Only lights that are on are used when Only Use Lights That Are Already On is
  set (default); a light that was off is never touched.
- Every light is put back exactly as it was: WLED lights through their JSON API
  (the saved /json/state, with a transition), other lights from their saved
  Home Assistant state.
- A new animation interrupts the running one but keeps the original snapshot,
  so the lights always go back to how they were before any effect started.
- No polling: state is read once when an animation starts.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, CONF_HOST, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import sections
from .const import CONF_WLED_ENABLED, CONF_WLED_FLASH_MS, CONF_WLED_LIGHTS, CONF_WLED_ONLY_ON, DEFAULT_WLED_FLASH_MS, DOMAIN

_LOGGER = logging.getLogger(__name__)

HTTP_TIMEOUT_S = 2
SEG_SKIP = {"n", "len"}
COLOR_ATTRS = {
    "rgb": "rgb_color",
    "rgbw": "rgbw_color",
    "rgbww": "rgbww_color",
    "hs": "hs_color",
    "xy": "xy_color",
    "color_temp": "color_temp_kelvin",
}


@dataclass
class Saved:
    """How one light looked before the animation."""

    entity_id: str
    state: str
    attributes: dict[str, Any]
    host: str | None = None
    segment: int | None = None  # WLED segment light, or None for the whole device
    wled_state: dict[str, Any] | None = None
    touched: bool = field(default=False)


class WledSections:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._task: asyncio.Task[None] | None = None
        self._saved: dict[str, Saved] | None = None
        self._lights: list[sections.Light] = []

    # ------------------------------------------------------------ options
    @property
    def lights(self) -> list[sections.Light]:
        return sections.lights_from_options(self.entry.options.get(CONF_WLED_LIGHTS) or [])

    @property
    def enabled(self) -> bool:
        return bool(self.entry.options.get(CONF_WLED_ENABLED, True)) and bool(self.lights)

    @property
    def flash_ms(self) -> int:
        return int(self.entry.options.get(CONF_WLED_FLASH_MS, DEFAULT_WLED_FLASH_MS))

    @property
    def only_on(self) -> bool:
        return bool(self.entry.options.get(CONF_WLED_ONLY_ON, True))

    # ------------------------------------------------------------ triggers
    def throw(self, hit: dict[str, Any], awards: list[dict[str, Any]], color: tuple[int, int, int]) -> None:
        if self.enabled:
            self._play(lambda lights: sections.plan_throw(lights, hit, awards, color, self.flash_ms))

    def turn(self, color: tuple[int, int, int]) -> None:
        if self.enabled:
            self._play(lambda lights: sections.plan_turn(lights, color))

    def _play(self, make_plan: Any) -> None:
        """Interrupt anything running (keeping its snapshot) and start the new plan."""
        if self._task is not None and not self._task.done():
            self._task.cancel()
        self._task = self.entry.async_create_background_task(
            self.hass, self._run(make_plan), name=f"{DOMAIN}-wled-sections"
        )

    async def async_stop(self) -> None:
        task, self._task = self._task, None
        if task is not None and not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        await self._restore_all()

    # ------------------------------------------------------------ running
    async def _run(self, make_plan: Any) -> None:
        try:
            if self._saved is None:
                self._lights = self.lights
                self._saved = await self._snapshot(self._lights)
            lights = self._lights
            usable = [i for i, light in enumerate(lights) if light.entity_id in self._saved]
            if not usable:
                self._saved = None
                return
            # Plan only over usable lights so sweeps and falloff skip lights that are off.
            sub = [lights[i] for i in usable]
            plan = make_plan(sub)
            start = time.monotonic()
            for at_ms, group in _groups(plan):
                delay = at_ms / 1000 - (time.monotonic() - start)
                if delay > 0:
                    await asyncio.sleep(delay)
                await asyncio.gather(*(self._apply(sub[f.light], f) for f in group))
            await self._restore_all()
        except asyncio.CancelledError:
            raise  # the next animation takes over and restores at its end
        except Exception as err:  # noqa: BLE001 - lights must never break hit reading
            _LOGGER.debug("Granboard WLED Sections stopped: %s", err)
            with contextlib.suppress(Exception):
                await self._restore_all()

    async def _snapshot(self, lights: list[sections.Light]) -> dict[str, Saved]:
        saved: dict[str, Saved] = {}
        registry = er.async_get(self.hass)
        for light in lights:
            state = self.hass.states.get(light.entity_id)
            if state is None or state.state in ("unavailable", "unknown"):
                continue
            if self.only_on and state.state != STATE_ON:
                continue  # never touch a light that is off
            item = Saved(light.entity_id, state.state, dict(state.attributes))
            item.host, item.segment = self._wled_target(registry, light.entity_id)
            if item.host:
                item.wled_state = await self._wled_get(item.host)
                if item.wled_state is None:
                    item.host = None  # fall back to Home Assistant for this light
            saved[light.entity_id] = item
        return saved

    def _wled_target(self, registry: er.EntityRegistry, entity_id: str) -> tuple[str | None, int | None]:
        ent = registry.async_get(entity_id)
        if ent is None or ent.platform != "wled" or not ent.config_entry_id:
            return None, None
        config = self.hass.config_entries.async_get_entry(ent.config_entry_id)
        host = config.data.get(CONF_HOST) if config else None
        if not host:
            return None, None
        segment = None
        uid = ent.unique_id or ""
        if "_" in uid and uid.rsplit("_", 1)[1].isdigit():
            segment = int(uid.rsplit("_", 1)[1])
        return host, segment

    # ------------------------------------------------------------ commands
    async def _apply(self, light: sections.Light, frame: sections.Frame) -> None:
        saved = (self._saved or {}).get(light.entity_id)
        if saved is None:
            return
        if frame.action == "restore":
            await self._restore(saved, frame.transition_ms)
            return
        saved.touched = True
        bri = max(1, round(255 * frame.level))
        if saved.host and await self._wled_set(saved, frame.color, bri, frame.transition_ms):
            return
        await self.hass.services.async_call(
            "light",
            "turn_on",
            {ATTR_ENTITY_ID: light.entity_id, "rgb_color": list(frame.color), "brightness": bri, "transition": frame.transition_ms / 1000},
            blocking=False,
        )

    async def _restore_all(self) -> None:
        saved, self._saved = self._saved, None
        if not saved:
            return
        await asyncio.gather(*(self._restore(item, 500) for item in saved.values() if item.touched), return_exceptions=True)

    async def _restore(self, saved: Saved, transition_ms: int) -> None:
        if not saved.touched:
            return
        saved.touched = False
        if saved.host and saved.wled_state is not None and await self._wled_post(saved.host, _restore_body(saved, transition_ms)):
            return
        if saved.state != STATE_ON:
            # Only reachable with Only Use Lights That Are Already On switched off: put it back off.
            await self.hass.services.async_call("light", "turn_off", {ATTR_ENTITY_ID: saved.entity_id}, blocking=False)
            return
        await self.hass.services.async_call("light", "turn_on", _ha_restore_data(saved, transition_ms), blocking=False)

    async def _wled_get(self, host: str) -> dict[str, Any] | None:
        try:
            session = async_get_clientsession(self.hass)
            async with asyncio.timeout(HTTP_TIMEOUT_S):
                resp = await session.get(f"http://{host}/json/state")
                resp.raise_for_status()
                data = await resp.json(content_type=None)
            return data if isinstance(data, dict) else None
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("WLED %s state read failed: %s", host, err)
            return None

    async def _wled_post(self, host: str, body: dict[str, Any]) -> bool:
        try:
            session = async_get_clientsession(self.hass)
            async with asyncio.timeout(HTTP_TIMEOUT_S):
                resp = await session.post(f"http://{host}/json/state", json=body)
                resp.raise_for_status()
            return True
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("WLED %s write failed: %s", host, err)
            return False

    async def _wled_set(self, saved: Saved, color: tuple[int, int, int], bri: int, transition_ms: int) -> bool:
        assert saved.host
        tt = max(0, round(transition_ms / 100))
        col = [list(color)]
        if saved.segment is not None:
            body = {"tt": tt, "seg": [{"id": saved.segment, "on": True, "bri": bri, "col": col, "fx": 0}]}
        else:
            ids = [s.get("id", i) for i, s in enumerate((saved.wled_state or {}).get("seg") or [{}])]
            body = {"on": True, "bri": bri, "tt": tt, "seg": [{"id": i, "col": col, "fx": 0} for i in ids]}
        return await self._wled_post(saved.host, body)


def _groups(plan: list[sections.Frame]) -> list[tuple[int, list[sections.Frame]]]:
    out: list[tuple[int, list[sections.Frame]]] = []
    for frame in sorted(plan, key=lambda f: (f.at_ms, f.action != "restore")):
        if out and out[-1][0] == frame.at_ms:
            out[-1][1].append(frame)
        else:
            out.append((frame.at_ms, [frame]))
    return out


def _clean_seg(seg: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in seg.items() if k not in SEG_SKIP}


def _restore_body(saved: Saved, transition_ms: int) -> dict[str, Any]:
    state = saved.wled_state or {}
    tt = max(0, round(transition_ms / 100))
    segs = [_clean_seg(s) for s in state.get("seg") or [] if isinstance(s, dict)]
    if saved.segment is not None:
        return {"tt": tt, "seg": [s for s in segs if s.get("id") == saved.segment]}
    body: dict[str, Any] = {"tt": tt, "seg": segs}
    for key in ("on", "bri"):
        if key in state:
            body[key] = state[key]
    return body


def _ha_restore_data(saved: Saved, transition_ms: int) -> dict[str, Any]:
    attrs = saved.attributes
    data: dict[str, Any] = {ATTR_ENTITY_ID: saved.entity_id, "transition": transition_ms / 1000}
    if attrs.get("brightness") is not None:
        data["brightness"] = attrs["brightness"]
    key = COLOR_ATTRS.get(str(attrs.get("color_mode")))
    if key and attrs.get(key) is not None:
        value = attrs[key]
        data[key] = list(value) if isinstance(value, (list, tuple)) else value
    effect = attrs.get("effect")
    if effect and effect not in ("None", "none", "Solid") and effect in (attrs.get("effect_list") or []):
        data["effect"] = effect
    return data
