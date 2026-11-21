from __future__ import annotations

import itertools
import random

from custom_components.granboard import effects as E
from custom_components.granboard import led
from custom_components.granboard import palettes as P

DOCUMENTED = {led.LIGHT_RING, led.BLINK, led.WAVE, led.HIT_SINGLE, led.HIT_DOUBLE, led.HIT_TRIPLE}


def _take(effect, n=120, **kw):
    return list(itertools.islice(E.frames(effect, E.RingOptions(**kw), random.Random(1)), n))


def test_every_effect_uses_documented_commands_and_gentle_timing():
    for effect in E.EFFECTS:
        for palette in (P.DEFAULT, "Ocean", P.COLORS_1_2):
            for speed in (0, 128, 255):
                steps = _take(effect, color=(0, 0, 255), palette=palette, speed=speed, intensity=255)
                assert steps, effect
                for cmd, wait in steps:
                    assert wait >= led.AMBIENT_MIN_GAP_MS >= 250  # at most 4 writes a second
                    assert cmd == led.clear_command() or (len(cmd) == 16 and cmd[0] in DOCUMENTED), effect


def test_solid_is_one_write_scaled():
    assert _take(E.SOLID, color=(255, 0, 0), brightness=128) == [(led.ring_command((128, 0, 0)), 250)]


def test_speed_scales_but_never_under_floor():
    assert E.wait(1000, 128) == 1000
    assert E.wait(1000, 0) == 4000
    assert E.wait(1000, 255) == 253
    assert E.wait(300, 255) == 250


def test_palette_drives_colors():
    # Chase with Color 1 and no palette: every number in the light colour.
    plain = _take(E.CHASE, 20, color=(0, 255, 0))
    assert {c[1:4] for c, _ in plain} == {bytes((0, 255, 0))}
    assert [c[10] for c, _ in plain] == [led.LED_POSITIONS[n] for n in led.CLOCKWISE_ORDER]
    # With a palette the numbers take palette colours around the ring.
    ocean = _take(E.CHASE, 20, color=(0, 255, 0), palette="Ocean")
    assert [c[1:4] for c, _ in ocean] == [bytes(P.color_at("Ocean", round(i * 256 / 20), (0, 255, 0), (0, 0, 0))) for i in range(20)]
    # Color Cycle defaults to the rainbow, and follows a chosen palette.
    assert _take(E.COLOR_CYCLE, 1)[0][0][1:4] == bytes((255, 0, 0))
    lava = {c[1:4] for c, _ in _take(E.COLOR_CYCLE, 32, palette="Lava")}
    assert len(lava) > 3 and all(c[0] >= c[2] for c in lava)


def test_wave_uses_color_2_or_opposite():
    wave = _take(E.WAVE, 1, color=(255, 0, 0))[0][0]
    assert wave[0] == led.WAVE and wave[4:7] == bytes((0, 255, 255))
    wave = _take(E.WAVE, 1, color=(255, 0, 0), color2=(0, 0, 255))[0][0]
    assert wave[4:7] == bytes((0, 0, 255))


def test_breathe_and_fire_hold_ring_and_police_alternates():
    breathe = [c[1] for c, _ in _take(E.BREATHE, 16, color=(255, 0, 0), intensity=255)]
    assert max(breathe) == 255 and min(breathe) < 40
    assert all(c[0] == led.LIGHT_RING for c, _ in _take(E.FIRE_FLICKER, 20))
    police = _take(E.POLICE, 4)
    assert [c[1:4] for c, _ in police] == [bytes(led.RED), bytes(led.BLUE)] * 2
    wipe = _take(E.WIPE, 21, color=(0, 255, 0))
    assert wipe[20][0] == led.clear_command() and wipe[20][1] == 1500


def test_palettes_list_and_sampling():
    for name in ("Default", "Color 1", "Colors 1&2", "Color Gradient", "Rainbow", "Rainbow Bands", "Party", "Ocean",
                 "Forest", "Lava", "Heat", "Sunset", "Pastel", "Sakura", "Aurora", "Fire", "Ice", "Beach", "Autumn",
                 "Magenta", "Orange & Teal", "Tiamat", "April Night", "Candy", "Toxy Reaf", "Fairy Reaf",
                 "Semi Blue", "Pink Candy", "Red & Blue", "Temperature", "Yelblu", "Atlantica"):
        assert name in P.PALETTES
    assert len(P.PALETTES) == len(set(P.PALETTES))
    for stops in P.GRADIENTS.values():
        positions = [p for p, _ in stops]
        assert positions == sorted(positions) and positions[0] == 0 and positions[-1] == 255
        assert all(0 <= c <= 255 for _, rgb in stops for c in rgb)
    assert P.color_at("Heat", 85, (0, 0, 0), (0, 0, 0)) == (255, 0, 0)
    assert P.color_at("Toxy Reaf", 128, (0, 0, 0), (0, 0, 0)) == (37, 112, 116)
    assert P.color_at(P.COLOR_1, 77, (1, 2, 3), (4, 5, 6)) == (1, 2, 3)
    assert P.color_at(P.COLORS_1_2, 200, (1, 2, 3), (4, 5, 6)) == (4, 5, 6)
    assert P.color_at(P.COLOR_GRADIENT, 128, (0, 0, 0), (200, 100, 0)) == (200, 100, 0)
    assert P.css_gradient("Heat").startswith("linear-gradient(90deg, #000000 0%")
