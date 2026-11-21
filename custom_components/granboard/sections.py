"""WLED Sections: lights placed around the board react where the dart lands. Pure Python.

Angles are degrees clockwise from the top of the board (0 = the 20), so a
number's angle is its place in the dartboard order times 18.

An animation is a plan: a list of Frames (time, light index, action). The
controller in wled_sections.py runs the plan against Home Assistant / WLED.
"""

from __future__ import annotations

import colorsys
from dataclasses import dataclass
from typing import Any

RGB = tuple[int, int, int]

# Dartboard numbers clockwise from the top.
BOARD_ORDER = (20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5)
DEGREES_PER_NUMBER = 360 / 20

PRESETS: dict[str, float] = {
    "top": 0.0,
    "top_right": 45.0,
    "right": 90.0,
    "bottom_right": 135.0,
    "bottom": 180.0,
    "bottom_left": 225.0,
    "left": 270.0,
    "top_left": 315.0,
}
CUSTOM = "custom"
POSITIONS = (*PRESETS, CUSTOM)

MIN_LEVEL = 0.15  # softest glow a neighbouring light gets (fraction of full brightness)
LAP_MS = 1600  # one trip round all the lights
MIN_STEP_MS = 150

SWEEP_AWARDS = {"ton": 1, "ton_40": 1, "high_ton": 1, "ton_80": 2, "hat_trick": 2, "bust": 1, "checkout": 2, "winner": 2}
RAINBOW_AWARDS = {"checkout", "winner"}
RED: RGB = (255, 0, 0)


@dataclass(frozen=True)
class Light:
    entity_id: str
    angle: float
    spread: float = 0.0  # degrees either side it covers; 0 = automatic


@dataclass(frozen=True)
class Frame:
    at_ms: int
    light: int  # index into the lights list
    action: str  # "set" or "restore"
    color: RGB = (0, 0, 0)
    level: float = 1.0  # 0-1 brightness
    transition_ms: int = 0


def number_angle(number: int) -> float:
    return BOARD_ORDER.index(int(number)) * DEGREES_PER_NUMBER


def light_angle(conf: dict[str, Any]) -> float:
    position = conf.get("position") or CUSTOM
    if position in PRESETS:
        return PRESETS[position]
    return float(conf.get("angle") or 0) % 360


def lights_from_options(entries: list[dict[str, Any]]) -> list[Light]:
    out = []
    for conf in entries or []:
        entity_id = conf.get("entity_id")
        if entity_id:
            out.append(Light(entity_id, light_angle(conf), float(conf.get("spread") or 0)))
    return out


def angular_distance(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def _width(light: Light, count: int) -> float:
    if light.spread > 0:
        return light.spread
    return max(30.0, 360 / max(1, count))


def weights(lights: list[Light], angle: float) -> list[float]:
    """0-1 per light for a hit at `angle`. The nearest light is always 1; others fade with distance."""
    if not lights:
        return []
    raw = [max(0.0, 1 - angular_distance(light.angle, angle) / _width(light, len(lights))) for light in lights]
    nearest = min(range(len(lights)), key=lambda i: angular_distance(lights[i].angle, angle))
    top = max(raw)
    if top <= 0:
        raw[nearest] = 1.0
        top = 1.0
    out = [w / top for w in raw]
    out[nearest] = 1.0
    return [round(w, 3) if w <= 0 else round(max(MIN_LEVEL, w), 3) for w in out]


def sweep_order(lights: list[Light], start_angle: float = 0.0) -> list[int]:
    """Light indexes clockwise, starting with the first light at or after start_angle."""
    return sorted(range(len(lights)), key=lambda i: ((lights[i].angle - start_angle) % 360, i))


def hue(fraction: float) -> RGB:
    r, g, b = colorsys.hsv_to_rgb(fraction % 1.0, 1.0, 1.0)
    return round(r * 255), round(g * 255), round(b * 255)


def plan_hit(lights: list[Light], number: int, color: RGB, flash_ms: int) -> list[Frame]:
    w = weights(lights, number_angle(number))
    frames = [Frame(0, i, "set", color, level, 100) for i, level in enumerate(w) if level > 0]
    frames += [Frame(flash_ms, f.light, "restore", transition_ms=min(800, flash_ms)) for f in list(frames)]
    return frames


def plan_pulse(lights: list[Light], color: RGB, flash_ms: int, pulses: int = 1) -> list[Frame]:
    """Every light at once (bull / bullseye)."""
    frames: list[Frame] = []
    half = max(MIN_STEP_MS, flash_ms // 2)
    for p in range(pulses):
        t = p * 2 * half
        frames += [Frame(t, i, "set", color, 1.0, 100) for i in range(len(lights))]
        if p < pulses - 1:
            frames += [Frame(t + half, i, "set", color, MIN_LEVEL, half) for i in range(len(lights))]
    end = (pulses - 1) * 2 * half + flash_ms
    frames += [Frame(end, i, "restore", transition_ms=min(800, flash_ms)) for i in range(len(lights))]
    return frames


def plan_sweep(lights: list[Light], color: RGB | None, laps: int = 1, start_angle: float = 0.0, lap_ms: int = LAP_MS) -> list[Frame]:
    """A light travels round in board order: each light comes on as the previous one fades back.
    color None = rainbow over the whole sweep."""
    if not lights:
        return []
    order = sweep_order(lights, start_angle)
    n = len(order)
    step = max(MIN_STEP_MS, lap_ms // n)
    total = n * max(1, laps)
    frames: list[Frame] = []
    for k in range(total):
        i = order[k % n]
        c = color if color is not None else hue(k / total)
        frames.append(Frame(k * step, i, "set", c, 1.0, step // 2))
        nxt = k + n
        # Fade back as the next light takes over, unless this light comes round again straight away (one light).
        if n > 1 or nxt >= total:
            frames.append(Frame((k + 1) * step, i, "restore", transition_ms=step))
    return sorted(frames, key=lambda f: (f.at_ms, f.action != "restore"))


def plan_throw(lights: list[Light], hit: dict[str, Any], awards: list[dict[str, Any]], color: RGB, flash_ms: int) -> list[Frame]:
    """What the lights do for one dart. An award sweep beats the hit flash."""
    for award in awards:
        kind = award.get("type")
        if kind in SWEEP_AWARDS:
            sweep_color = None if kind in RAINBOW_AWARDS else (RED if kind == "bust" else color)
            return plan_sweep(lights, sweep_color, SWEEP_AWARDS[kind])
    ring = hit.get("ring")
    if ring in ("bull", "bullseye"):
        return plan_pulse(lights, color, flash_ms, 2 if ring == "bullseye" else 1)
    number = int(hit.get("number") or 0)
    if ring in ("single_inner", "single_outer", "double", "treble") and 1 <= number <= 20:
        return plan_hit(lights, number, color, flash_ms)
    return []


def plan_turn(lights: list[Light], color: RGB) -> list[Frame]:
    return plan_sweep(lights, color, 1)
