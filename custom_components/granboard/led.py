"""Granboard LED ring commands and effect plans. Pure Python.

Format from keenanlk/granboard-ble-codes (reverse engineered, tested on a
GranBoard 3s). Commands go to the write characteristic 442f1572-...:

16-byte effect command
  [0] type: 0x01/0x02/0x03 hit blink (1-3 blinks), 0x11 wave, 0x14 light ring, 0x17 blink ring
  [1..3] RGB, [4..6] second RGB (wave), [10] LED cell 0-59 or 0x10 full ring,
  [12] duration / speed in board frames, [15] 0x01 persistent
20-byte command: byte n-1 is a palette colour for dart number n (0 = off,
  0x05 = orange is the only confirmed one). All zeros clears the ring.

The board can drop commands sent back to back; space them ~60 ms apart.
"""

from __future__ import annotations

from collections.abc import Iterable

RGB = tuple[int, int, int]
Step = tuple[bytes, int]  # command, milliseconds to wait after it

MIN_GAP_MS = 60

HIT_SINGLE, HIT_DOUBLE, HIT_TRIPLE = 0x01, 0x02, 0x03
WAVE, LIGHT_RING, BLINK = 0x11, 0x14, 0x17
FULL_RING = 0x10
PALETTE_ORANGE = 0x05

# LED ring cell for each dart number; index 0 is bull.
LED_POSITIONS = (0, 28, 49, 55, 34, 22, 40, 1, 7, 16, 43, 10, 19, 37, 13, 46, 4, 52, 31, 58, 25)
CLOCKWISE_ORDER = (7, 16, 8, 11, 14, 9, 12, 5, 20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19)

RED: RGB = (255, 0, 0)
GREEN: RGB = (0, 255, 0)
BLUE: RGB = (0, 0, 255)
WHITE: RGB = (255, 255, 255)
YELLOW: RGB = (255, 200, 0)
ORANGE: RGB = (255, 80, 0)
LIGHT_BLUE: RGB = (0, 200, 255)
PURPLE: RGB = (170, 0, 255)

# Colour by bed, as suggested by the protocol reference.
RING_COLORS: dict[str, RGB] = {
    "single_inner": RED,
    "single_outer": RED,
    "double": GREEN,
    "treble": YELLOW,
    "bull": LIGHT_BLUE,
    "bullseye": RED,
}


def _b(value: int, name: str) -> int:
    value = int(value)
    if not 0 <= value <= 255:
        raise ValueError(f"{name} must be 0-255, got {value}")
    return value


def _rgb(cmd: bytearray, offset: int, color: Iterable[int]) -> None:
    r, g, b = (int(c) for c in color)
    cmd[offset : offset + 3] = bytes((_b(r, "red"), _b(g, "green"), _b(b, "blue")))


def _number(n: int) -> int:
    n = int(n)
    if not 1 <= n <= 20:
        raise ValueError(f"dart number must be 1-20, got {n}")
    return n


def hit_command(number: int, color: RGB, blinks: int = 1, duration: int = 0x14) -> bytes:
    """Blink one number's segment on the ring 1-3 times."""
    if blinks not in (1, 2, 3):
        raise ValueError("blinks must be 1, 2 or 3")
    cmd = bytearray(16)
    cmd[0] = blinks
    _rgb(cmd, 1, color)
    cmd[10] = LED_POSITIONS[_number(number)]
    cmd[12] = _b(duration, "duration")
    return bytes(cmd)


def blink_command(color: RGB, duration: int = 0x1E) -> bytes:
    """Flash the whole ring, then it turns itself off."""
    cmd = bytearray(16)
    cmd[0] = BLINK
    _rgb(cmd, 1, color)
    cmd[12] = _b(duration, "duration")
    cmd[15] = 0x01
    return bytes(cmd)


def wave_command(color_up: RGB, color_down: RGB, speed: int = 0x05) -> bytes:
    cmd = bytearray(16)
    cmd[0] = WAVE
    _rgb(cmd, 1, color_up)
    _rgb(cmd, 4, color_down)
    cmd[10] = FULL_RING
    cmd[12] = _b(speed, "speed")
    return bytes(cmd)


def ring_command(color: RGB) -> bytes:
    """Whole ring solid until the next command."""
    cmd = bytearray(16)
    cmd[0] = LIGHT_RING
    _rgb(cmd, 1, color)
    cmd[12] = 0x14
    cmd[15] = 0x01
    return bytes(cmd)


def numbers_command(numbers: Iterable[int], palette: int = PALETTE_ORANGE) -> bytes:
    """Keep these numbers lit (board palette colour). Bull cannot be lit this way."""
    cmd = bytearray(20)
    for n in numbers:
        cmd[_number(n) - 1] = _b(palette, "palette")
    return bytes(cmd)


def clear_command() -> bytes:
    return bytes(20)


def _lerp(a: RGB, b: RGB, t: float) -> RGB:
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))  # type: ignore[return-value]


def sweep(start: RGB = RED, end: RGB = GREEN, gap_ms: int = MIN_GAP_MS) -> list[Step]:
    """Each number in clockwise order, red to green, then a green blink."""
    steps: list[Step] = [
        (hit_command(n, _lerp(start, end, i / 19)), gap_ms) for i, n in enumerate(CLOCKWISE_ORDER)
    ]
    steps.append((blink_command(end, 0x14), MIN_GAP_MS))
    return steps


# ------------------------------------------------------------------ plans
# `color` is the throwing player's colour, so each player's darts light in their own colour.


def _seg_number(segment: object) -> int:
    digits = "".join(c for c in str(segment or "") if c.isdigit())
    return int(digits) if digits and 1 <= int(digits) <= 20 else 0


def plan_hit(hit: dict, color: RGB = RED) -> list[Step]:
    """One dart. Segment blinks once / twice / three times for single / double / treble.
    Triple 20 adds a wave, outer bull a short ring flash, bullseye a red wave and flash."""
    ring = hit.get("ring")
    number = int(hit.get("number") or 0)
    if ring == "bull":
        return [(blink_command(color, 0x0A), MIN_GAP_MS)]
    if ring == "bullseye":
        return [(wave_command(RED, color, 0x02), 300), (blink_command(RED, 0x14), MIN_GAP_MS)]
    if ring not in ("single_inner", "single_outer", "double", "treble") or not 1 <= number <= 20:
        return []  # miss / unknown: leave the ring alone
    blinks = {"double": 2, "treble": 3}.get(ring, 1)
    steps: list[Step] = [(hit_command(number, color, blinks), MIN_GAP_MS)]
    if ring == "treble" and number == 20:
        steps.append((wave_command(color, WHITE, 0x03), 300))
    return steps


def plan_award(award: dict, color: RGB | None = None) -> list[Step]:
    kind = award.get("type")
    if color is None:
        color = _hex_rgb(award.get("color")) or WHITE
    if kind == "bullseye":
        if award.get("score") == 50:  # inner bull
            return [(wave_command(RED, color, 0x02), 400), (blink_command(RED, 0x1E), 400)]
        return [(blink_command(LIGHT_BLUE, 0x14), 200), (blink_command(color, 0x14), 300)]
    if kind == "bust":
        return [(blink_command(RED, 0x0A), 300), (blink_command(RED, 0x0A), 300)]
    if kind in ("ton", "ton_40"):
        return [(wave_command(color, YELLOW, 0x05), 800)]
    if kind == "high_ton":
        return [(wave_command(color, ORANGE, 0x04), 800)]
    if kind == "ton_80":
        return [(wave_command(RED, YELLOW, 0x03), 900), (wave_command(color, WHITE, 0x02), 600), (blink_command(WHITE, 0x1E), 400)]
    if kind == "hat_trick":
        return [(wave_command(RED, LIGHT_BLUE, 0x03), 900), (blink_command(color, 0x1E), 400)]
    if kind == "three_in_a_bed":
        n = _seg_number(award.get("segment"))
        if n:
            return [(hit_command(n, PURPLE, 3, 0x1E), 700), (hit_command(n, color, 3, 0x1E), 700)]
        return [(blink_command(PURPLE, 0x1E), 400)]
    if kind == "white_horse":
        return [(wave_command(WHITE, color, 0x03), 900)]
    if kind == "checkout":
        n = _seg_number(award.get("segment"))
        steps: list[Step] = [(hit_command(n, GREEN, 3, 0x1E), 700)] if n else []
        return [*steps, (wave_command(GREEN, color, 0x03), 800)]
    if kind == "winner":
        return [*sweep(color, GREEN), (wave_command(color, YELLOW, 0x03), 900), (blink_command(color, 0x1E), 400)]
    return []


def _hex_rgb(value: object) -> RGB | None:
    text = str(value or "").lstrip("#")
    if len(text) != 6:
        return None
    try:
        return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)
    except ValueError:
        return None


def plan_throw(hit: dict, awards: Iterable[dict], color: RGB = RED) -> list[Step]:
    """The hit, then each award. A bull award replaces the plain bull flash."""
    awards = list(awards)
    steps: list[Step] = []
    if not any(a.get("type") == "bullseye" for a in awards):
        steps += plan_hit(hit, color)
    for award in awards:
        steps += plan_award(award, color)
    return steps


def plan_new_game(color: RGB = GREEN) -> list[Step]:
    return [(clear_command(), MIN_GAP_MS), *sweep(RED, color)]


def turn_wipe(color: RGB, gap_ms: int = MIN_GAP_MS) -> list[Step]:
    """Circular wipe like the official app plays when the turn is cleared:
    each number lights in turn, clockwise all the way round, then the ring clears."""
    steps: list[Step] = [(hit_command(n, color, 1, 0x0A), gap_ms) for n in CLOCKWISE_ORDER]
    steps.append((clear_command(), MIN_GAP_MS))
    return steps


def plan_next_player(color: RGB = RED) -> list[Step]:
    """End of turn / darts pulled: circular wipe in the next player's colour."""
    return turn_wipe(color)


# ------------------------------------------------------------ ambient light
# The LED Ring light entity uses only the documented commands above (ring,
# blink, wave, segment blink, clear). Loop effects are slow: at least
# AMBIENT_MIN_GAP_MS between writes (4 per second at most), never bursts.

AMBIENT_MIN_GAP_MS = 250

def scale(color: Iterable[int], brightness: int) -> RGB:
    """Apply a 0-255 brightness to a colour (the board has no brightness byte).
    A lit channel never rounds down to 0 while brightness is above 0."""
    level = max(0, min(255, int(brightness)))
    out = []
    for c in color:
        c = max(0, min(255, int(c)))
        v = round(c * level / 255)
        out.append(1 if v == 0 and c > 0 and level > 0 else v)
    return tuple(out)  # type: ignore[return-value]


def hue(degrees: float, brightness: int = 255) -> RGB:
    """Fully saturated colour on the colour wheel."""
    import colorsys

    r, g, b = colorsys.hsv_to_rgb((degrees % 360) / 360, 1.0, 1.0)
    return scale((round(r * 255), round(g * 255), round(b * 255)), brightness)


def complement(color: RGB) -> RGB:
    import colorsys

    r, g, b = (c / 255 for c in color)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    if s == 0:  # white / grey: pair it with the off colour of the wave
        return (0, 0, 0)
    r, g, b = colorsys.hsv_to_rgb((h + 0.5) % 1.0, s, v)
    return round(r * 255), round(g * 255), round(b * 255)
