"""LED Ring light effects. Pure Python.

Every effect is a generator of (command, wait ms) steps built only from the
documented ring commands in led.py: whole-ring colour (0x14), whole-ring blink
(0x17), wave (0x11), one-number blink (0x01-0x03), the native rainbow
sweep (0x10, confirmed on a real board; one pass, then re-sent every 2 s) and clear. Waits never go
below led.AMBIENT_MIN_GAP_MS (250 ms, at most 4 writes a second).

The board cannot hold several numbers lit in different colours with a
documented command (number blinks turn themselves off, and the 20-byte number
command has only one confirmed palette colour, orange), so per-number effects
are moving or twinkling blinks, and whole-ring effects carry the palette over
time instead of across the ring.
"""

from __future__ import annotations

import random
from collections.abc import Iterator
from dataclasses import dataclass

from . import led
from . import palettes as pal

RGB = tuple[int, int, int]

SOLID = "Solid"
BLINK = "Blink"
BREATHE = "Breathe"
HEARTBEAT = "Heartbeat"
WAVE = "Wave"
COLOR_CYCLE = "Color Cycle"
PALETTE_STEPS = "Palette Steps"
CHASE = "Chase"
RAINBOW_CHASE = "Rainbow Chase"
CIRCULAR_RAINBOW = "Circular Rainbow"
RAINBOW_SWEEP = "Rainbow Sweep"
BOUNCE = "Bounce"
WIPE = "Circular Wipe"
TWINKLE = "Twinkle"
FIRE_FLICKER = "Fire Flicker"
POLICE = "Police"
LIGHTNING = "Lightning"

EFFECTS: tuple[str, ...] = (
    SOLID, BLINK, BREATHE, HEARTBEAT, WAVE, COLOR_CYCLE, PALETTE_STEPS, CHASE, RAINBOW_CHASE, CIRCULAR_RAINBOW, RAINBOW_SWEEP,
    BOUNCE, WIPE, TWINKLE, FIRE_FLICKER, POLICE, LIGHTNING,
)
# Effects that hold the whole ring in one colour: an unchanged frame is not re-sent.
# (Blinks and waves play and stop by themselves, so a repeat is a new flash.)
# Rainbow Sweep is not here: the same 0x10 command must be re-sent after each pass.
HOLD_EFFECTS = frozenset({SOLID, BREATHE, COLOR_CYCLE, PALETTE_STEPS, FIRE_FLICKER})
# The board's own animation: colour, brightness, palette, speed and intensity do not apply.
NATIVE_EFFECTS = frozenset({RAINBOW_SWEEP})
# Effects that ignore Ring Palette / Speed / Intensity / Color 2 (no restart when those change).
SETTINGS_FREE_EFFECTS = frozenset({SOLID, RAINBOW_SWEEP})
# Palette the effect uses when the Ring Palette is Default.
DEFAULT_PALETTES = {COLOR_CYCLE: pal.RAINBOW, PALETTE_STEPS: pal.RAINBOW, RAINBOW_CHASE: pal.RAINBOW, CIRCULAR_RAINBOW: pal.RAINBOW, FIRE_FLICKER: pal.FIRE}

DEFAULT_SPEED = 128
DEFAULT_INTENSITY = 128


@dataclass(frozen=True)
class RingOptions:
    color: RGB = (255, 255, 255)
    brightness: int = 255
    color2: RGB | None = None  # None: the opposite of color
    palette: str = pal.DEFAULT
    speed: int = DEFAULT_SPEED
    intensity: int = DEFAULT_INTENSITY

    @property
    def second(self) -> RGB:
        return tuple(self.color2) if self.color2 is not None else led.complement(tuple(self.color))  # type: ignore[return-value]


def wait(base_ms: float, speed: int) -> int:
    """Scale a wait by Ring Speed (128 = as designed, 255 = 4x faster, 0 = 4x slower), never under the floor."""
    factor = 2 ** ((DEFAULT_SPEED - max(0, min(255, int(speed)))) / 64)
    return max(led.AMBIENT_MIN_GAP_MS, round(base_ms * factor))


def _palette_name(effect: str, opts: RingOptions) -> str | None:
    if opts.palette != pal.DEFAULT:
        return opts.palette
    return DEFAULT_PALETTES.get(effect)


def _color(effect: str, opts: RingOptions, pos: int) -> RGB:
    """Unscaled colour at a palette position, or Color 1 with no palette."""
    name = _palette_name(effect, opts)
    if name is None:
        return tuple(opts.color)  # type: ignore[return-value]
    return pal.color_at(name, pos, tuple(opts.color), opts.second)  # type: ignore[arg-type]


def _lit(color: RGB, opts: RingOptions, level: float = 1.0) -> RGB:
    return led.scale(color, round(opts.brightness * level))


def _number_pos(i: int) -> int:
    """Palette position of the i-th number clockwise, so the palette spreads around the ring."""
    return round((i % 20) * 256 / 20)


def frames(effect: str, opts: RingOptions, rng: random.Random | None = None) -> Iterator[led.Step]:
    """Steps for an effect. One-shot effects (Solid) end; the rest loop forever."""
    rng = rng or random.Random()
    s, k = opts.speed, opts.intensity
    if effect == BLINK:
        while True:
            yield led.blink_command(_lit(opts.color, opts), 0x14), wait(1200, s)
    elif effect == BREATHE:
        floor = 1 - 0.9 * k / 255  # Intensity: how deep the breath goes
        levels = [floor + (1 - floor) * i / 8 for i in range(9)]
        cycle = levels + levels[-2:0:-1]
        while True:
            for level in cycle:
                yield led.ring_command(_lit(opts.color, opts, level)), wait(350, s)
    elif effect == HEARTBEAT:
        while True:
            lit = _lit(opts.color, opts)
            yield led.blink_command(lit, 0x0A), wait(300, s)
            yield led.blink_command(lit, 0x0A), wait(1400, s)
    elif effect == WAVE:
        step = 0
        while True:
            if _palette_name(effect, opts) is None:
                a, b = opts.color, opts.second
            else:
                a, b = _color(effect, opts, step * 64), _color(effect, opts, step * 64 + 128)
            yield led.wave_command(_lit(a, opts), _lit(b, opts), 0x05), wait(4000, s)
            step += 1
    elif effect == CIRCULAR_RAINBOW:
        # The board's own wave (0x11) animates round the ring by itself; each new wave
        # moves its two colours further along the rainbow, so the colours circle the
        # board continuously. Built from the wave command (about one write a second);
        # the board's native rainbow (0x10) moves up and down instead, see Rainbow Sweep.
        gap = round(43 + 85 * k / 255)  # Intensity: how far apart the two colours are (60-180 degrees)
        step = 0
        while True:
            pos = step * 17  # 15 waves per trip round the rainbow
            a, b = _color(effect, opts, pos), _color(effect, opts, pos + gap)
            yield led.wave_command(_lit(a, opts), _lit(b, opts), 0x04), wait(1200, s)
            step += 1
    elif effect == COLOR_CYCLE:
        step = 0
        while True:  # whole ring glides along the palette, 32 steps per lap
            yield led.ring_command(_lit(_color(effect, opts, step * 8), opts)), wait(500, s)
            step += 1
    elif effect == PALETTE_STEPS:
        count = 4 + round(k / 255 * 12)  # Intensity: how many colours of the palette are shown
        step = 0
        while True:
            yield led.ring_command(_lit(_color(effect, opts, round(step * 256 / count)), opts)), wait(2500, s)
            step = (step + 1) % count
    elif effect in (CHASE, RAINBOW_CHASE):
        step = 0
        while True:
            yield led.hit_command(led.CLOCKWISE_ORDER[step % 20], _lit(_color(effect, opts, _number_pos(step)), opts), 1, 0x14), wait(300, s)
            step += 1
    elif effect == BOUNCE:
        path = list(range(20)) + list(range(18, 0, -1))
        while True:
            for i in path:
                yield led.hit_command(led.CLOCKWISE_ORDER[i], _lit(_color(effect, opts, _number_pos(i)), opts), 1, 0x0A), wait(250, s)
    elif effect == WIPE:
        while True:
            for i in range(20):
                yield led.hit_command(led.CLOCKWISE_ORDER[i], _lit(_color(effect, opts, _number_pos(i)), opts), 1, 0x0A), wait(250, s)
            yield led.clear_command(), wait(1500, s)
    elif effect == TWINKLE:
        base = 900 - 600 * k / 255  # Intensity: more twinkles
        while True:
            i = rng.randrange(20)
            color = _color(effect, opts, rng.randrange(256)) if _palette_name(effect, opts) else opts.color
            yield led.hit_command(led.CLOCKWISE_ORDER[i], _lit(color, opts), rng.choice((1, 1, 2)), 0x14), wait(base * rng.uniform(0.8, 1.4), s)
    elif effect == FIRE_FLICKER:
        depth = 0.6 * k / 255  # Intensity: how much the flame dims
        while True:
            color = _color(effect, opts, rng.randrange(110, 230))
            yield led.ring_command(_lit(color, opts, 1 - depth * rng.random())), wait(rng.uniform(300, 700), s)
    elif effect == POLICE:
        while True:
            yield led.blink_command(_lit(led.RED, opts), 0x0A), wait(400, s)
            yield led.blink_command(_lit(led.BLUE, opts), 0x0A), wait(400, s)
    elif effect == LIGHTNING:
        gap = 6000 - 4500 * k / 255  # Intensity: more strikes
        while True:
            lit = _lit(opts.color, opts)
            for _ in range(rng.choice((1, 2, 2, 3)) - 1):
                yield led.blink_command(lit, 0x05), led.AMBIENT_MIN_GAP_MS
            yield led.blink_command(lit, 0x05), wait(gap * rng.uniform(0.5, 1.5), s)
    elif effect == RAINBOW_SWEEP:
        # Native firmware rainbow, one up / down pass (~2 s). Re-sent so it loops.
        gap = round(led.REPEAT_RAINBOW_SWEEP_S * 1000)
        while True:
            yield led.rainbow_command(), gap
    else:  # Solid and anything unknown: one write, the ring holds it.
        yield led.ring_command(_lit(opts.color, opts)), led.AMBIENT_MIN_GAP_MS
