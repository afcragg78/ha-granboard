from __future__ import annotations

from custom_components.granboard import sections as S

FOUR = [S.Light("light.top", 0), S.Light("light.right", 90), S.Light("light.bottom", 180), S.Light("light.left", 270)]


def test_number_angles_follow_the_board():
    assert S.number_angle(20) == 0
    assert S.number_angle(1) == 18
    assert S.number_angle(6) == 90
    assert S.number_angle(3) == 180
    assert S.number_angle(11) == 270
    assert S.number_angle(5) == 342
    assert S.light_angle({"position": "bottom_left"}) == 225
    assert S.light_angle({"position": "custom", "angle": 400}) == 40
    assert S.angular_distance(350, 10) == 20


def test_nearest_light_full_neighbours_soft():
    assert S.weights(FOUR, S.number_angle(20)) == [1.0, 0, 0, 0]
    w = S.weights(FOUR, S.number_angle(18))  # 36 degrees: top full, right a softer glow
    assert w[0] == 1.0 and 0.15 <= w[1] < 1 and w[2] == 0 and w[3] == 0
    w = S.weights(FOUR, 45)  # exactly between: both full
    assert w[0] == w[1] == 1.0
    # A wide spread reaches further; a single light always gets the hit.
    wide = [S.Light("a", 0, 170), S.Light("b", 180, 170)]
    assert S.weights(wide, 90)[0] > 0 and S.weights(wide, 90)[1] > 0
    assert S.weights([S.Light("only", 200)], S.number_angle(20)) == [1.0]


def test_hit_plan_sets_then_restores_only_lit_lights():
    plan = S.plan_hit(FOUR, 18, (0, 0, 255), 700)
    sets = [f for f in plan if f.action == "set"]
    restores = [f for f in plan if f.action == "restore"]
    assert {f.light for f in sets} == {f.light for f in restores} == {0, 1}
    assert all(f.at_ms == 0 and f.color == (0, 0, 255) for f in sets)
    assert all(f.at_ms == 700 for f in restores)


def test_sweep_travels_in_board_order_with_handoff():
    lights = [S.Light("l", 270), S.Light("t", 10), S.Light("b", 180), S.Light("r", 90)]
    assert S.sweep_order(lights) == [1, 3, 2, 0]
    plan = S.plan_sweep(lights, (255, 0, 0), laps=1, lap_ms=1600)
    sets = [f for f in plan if f.action == "set"]
    assert [f.light for f in sets] == [1, 3, 2, 0]
    assert [f.at_ms for f in sets] == [0, 400, 800, 1200]
    # Each light fades back exactly as the next one comes on.
    restores = {f.light: f.at_ms for f in plan if f.action == "restore"}
    assert restores == {1: 400, 3: 800, 2: 1200, 0: 1600}
    rainbow = S.plan_sweep(lights, None, laps=2)
    colors = [f.color for f in rainbow if f.action == "set"]
    assert len(colors) == 8 and len(set(colors)) == 8 and colors[0] == (255, 0, 0)


def test_throw_picks_award_sweep_pulse_or_hit():
    hit = {"ring": "treble", "number": 20}
    win = S.plan_throw(FOUR, hit, [{"type": "winner"}], (0, 255, 0), 700)
    assert len([f for f in win if f.action == "set"]) == 8  # rainbow, two laps
    bust = S.plan_throw(FOUR, hit, [{"type": "bust"}], (0, 255, 0), 700)
    assert {f.color for f in bust if f.action == "set"} == {(255, 0, 0)}
    bull = S.plan_throw(FOUR, {"ring": "bullseye"}, [{"type": "bullseye"}], (0, 255, 0), 700)
    assert {f.light for f in bull if f.action == "set"} == {0, 1, 2, 3}
    assert [f.light for f in S.plan_throw(FOUR, hit, [], (0, 255, 0), 700) if f.action == "set"] == [0]
    assert S.plan_throw(FOUR, {"ring": "miss"}, [], (0, 255, 0), 700) == []
    single = S.plan_sweep([S.Light("one", 0)], (1, 2, 3), laps=2)
    assert [f.action for f in single] == ["set", "set", "restore"]
