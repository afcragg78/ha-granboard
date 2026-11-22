from __future__ import annotations

import pytest

from custom_components.granboard import led
from custom_components.granboard.colors import PLAYER_PALETTE, parse_color, player_color, to_rgb
from custom_components.granboard.game import Game
from custom_components.granboard.protocol import parse_segment


def test_reference_example_double_20_red():
    # keenanlk README: "Light Dart 20 (Double, Red, 20 frames)"
    assert led.hit_command(20, (255, 0, 0), blinks=2).hex() == "02ff00000000000000001900140000" + "00"


def test_wave_example():
    assert led.wave_command((255, 0, 0), (0, 0, 255)).hex() == "11ff00000000ff000000100005000000"


def test_blink_ring_and_clear():
    b = led.blink_command((0, 255, 0), 0x14)
    assert len(b) == 16 and b[0] == 0x17 and b[1:4] == bytes((0, 255, 0)) and b[12] == 0x14 and b[15] == 1
    assert led.ring_command((1, 2, 3))[0] == 0x14
    assert led.clear_command() == bytes(20)


def test_numbers_command():
    c = led.numbers_command([20, 1])
    assert len(c) == 20 and c[19] == 5 and c[0] == 5 and sum(c) == 10
    with pytest.raises(ValueError):
        led.numbers_command([25])


def test_bad_values():
    with pytest.raises(ValueError):
        led.hit_command(21, (0, 0, 0))
    with pytest.raises(ValueError):
        led.hit_command(1, (256, 0, 0))
    with pytest.raises(ValueError):
        led.hit_command(1, (0, 0, 0), blinks=4)


def test_sweep_is_20_steps_plus_blink_and_spaced():
    s = led.sweep()
    assert len(s) == 21 and all(w >= led.MIN_GAP_MS for _, w in s)
    assert s[0][0][1:4] == bytes((255, 0, 0)) and s[19][0][1:4] == bytes((0, 255, 0))


def test_hit_plans_by_ring_and_player_color():
    c = (10, 20, 30)
    single = led.plan_hit(parse_segment("S5").as_dict(), c)
    assert len(single) == 1 and single[0][0][0] == 1 and single[0][0][1:4] == bytes(c)
    assert led.plan_hit(parse_segment("D5").as_dict(), c)[0][0][0] == 2
    assert led.plan_hit(parse_segment("T5").as_dict(), c)[0][0][0] == 3
    t20 = led.plan_hit(parse_segment("T20").as_dict(), c)
    assert len(t20) == 2 and t20[1][0][0] == led.WAVE  # triple 20 gets an extra wave
    outer = led.plan_hit(parse_segment("SB").as_dict(), c)
    inner = led.plan_hit(parse_segment("DB").as_dict(), c)
    assert outer != inner and outer[0][0][0] == led.BLINK
    assert led.plan_hit({"ring": "miss", "number": 0}, c) == []


def test_bull_award_replaces_plain_bull_blink():
    hit = parse_segment("DB").as_dict()
    plan = led.plan_throw(hit, [{"type": "bullseye", "score": 50}], (1, 2, 3))
    assert plan == led.plan_award({"type": "bullseye", "score": 50}, (1, 2, 3))


@pytest.mark.parametrize("kind", ["bullseye", "bust", "ton", "ton_40", "high_ton", "ton_80", "hat_trick",
                                  "three_in_a_bed", "white_horse", "checkout", "winner"])
def test_every_award_has_an_effect(kind):
    assert led.plan_award({"type": kind, "segment": "T19", "score": 57}, (0, 0, 255))


def test_colors():
    assert parse_color("#ABC") == "#aabbcc" and parse_color("Blue") == "#0000ff"
    assert parse_color([255, 0, 1]) == "#ff0001" and parse_color("nope") is None
    assert player_color(1) == PLAYER_PALETTE[1] and player_color(0, "00ff00") == "#00ff00"
    assert to_rgb("#0000ff") == (0, 0, 255)


def test_game_player_colors_and_checkout_award():
    g = Game()
    g.new_game("301", ["A", "B", "C"], colors=["green", None])
    attrs = g.as_dict()
    assert attrs["current_player_color"] == "#00ff00" and attrs["players"][1]["color"] == PLAYER_PALETTE[1]
    assert [p.color for p in g.players] == ["#00ff00", PLAYER_PALETTE[1], PLAYER_PALETTE[2]]
    restored = Game.load(g.dump())
    assert restored.players[0].color == "#00ff00"
    old = g.dump()
    for p in old["players"]:
        p.pop("color")
    assert Game.load(old).color_of(2) == PLAYER_PALETTE[2]
    g.players[0].score = 40
    g.turn_start_score = 40
    awards = g.throw(parse_segment("D20"))
    co = [a for a in awards if a["type"] == "checkout"][0]
    assert co["score"] == 40 and co["double"] is True and co["color"] == "#00ff00"
    del attrs


def test_turn_wipe_goes_round_clockwise_in_player_color():
    w = led.plan_next_player((1, 2, 3))
    assert len(w) == 21 and w[-1][0] == led.clear_command()
    assert [c[10] for c, _ in w[:-1]] == sorted(led.LED_POSITIONS[1:])
    assert all(c[1:4] == bytes((1, 2, 3)) for c, _ in w[:-1])


def test_ambient_scale_and_hue():
    from custom_components.granboard import led as L

    assert L.scale((255, 128, 0), 255) == (255, 128, 0)
    assert L.scale((255, 128, 0), 128) == (128, 64, 0)
    assert L.scale((255, 1, 0), 10) == (10, 1, 0)  # lit channel never drops to 0
    assert L.scale((255, 0, 0), 0) == (0, 0, 0)
    assert L.hue(0) == (255, 0, 0) and L.hue(120) == (0, 255, 0) and L.hue(240) == (0, 0, 255)
    assert L.complement((255, 0, 0)) == (0, 255, 255)
    assert L.complement((255, 255, 255)) == (0, 0, 0)


def test_parse_raw_frames():
    import pytest as _pytest

    spin = led.parse_raw("10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
    assert spin == bytes([0x10]) + bytes(15)
    assert led.parse_raw("0x" + led.ring_command((255, 0, 0)).hex()) == led.ring_command((255, 0, 0))
    assert led.parse_raw("00" * 20) == led.clear_command()
    assert led.parse_raw(led.numbers_command([20]).hex()) == led.numbers_command([20])
    assert led.parse_raw("11:FF:00:00:00:00:FF:00:00:00:10:00:05:00:00:00")[0] == led.WAVE
    for bad in ("", "10", "1", "zz" * 16, "20" + "00" * 15, "10" * 17, "08" + "00" * 19, "00" * 21):
        with _pytest.raises(ValueError):
            led.parse_raw(bad)
