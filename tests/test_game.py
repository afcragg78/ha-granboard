from __future__ import annotations

import pytest

from custom_components.granboard.game import Game, GameError
from custom_components.granboard.protocol import decode_frame, parse_segment


def throw(game: Game, *segments: str) -> list[str]:
    kinds: list[str] = []
    for seg in segments:
        kinds += [a["type"] for a in game.throw(parse_segment(seg))]
    return kinds


def x01(start=501, players=("A", "B"), double_out=False) -> Game:
    g = Game()
    g.new_game("x01", list(players), start=start, double_out=double_out)
    return g


def test_x01_scoring_and_turns():
    g = x01()
    throw(g, "T20", "T20", "S20")
    assert g.players[0].score == 361
    assert g.turn_complete
    throw(g, "T20")  # ignored until next player
    assert g.players[0].score == 361
    g.next_player()
    assert g.player.name == "B" and g.as_dict()["darts_left"] == 3
    g.next_player()
    assert g.round == 2 and g.current == 0
    assert g.history[0]["darts"] == ["T20", "T20", "S20"] and g.history[0]["score"] == 140


def test_x01_bust_restores_turn_start():
    g = x01(301)
    g.players[0].score = 40
    g.turn_start_score = 40
    kinds = throw(g, "S20", "T20")
    assert "bust" in kinds
    assert g.players[0].score == 40 and g.turn_complete and g.turn_bust
    assert g.players[0].points == 0


def test_double_out_rules():
    g = x01(double_out=True)
    g.players[0].score = g.turn_start_score = 40
    assert "bust" in throw(g, "S20", "S20")  # finished on a single
    g.undo()
    g.undo()
    assert g.players[0].score == 40
    assert "bust" in throw(g, "S20", "S19")  # leaves 1
    g.undo(); g.undo()
    assert throw(g, "D20") == ["checkout", "winner"]
    assert g.status == "finished" and g.winner == "A"


def test_bullseye_counts_as_double_out():
    g = x01(double_out=True)
    g.players[0].score = g.turn_start_score = 50
    assert throw(g, "DB") == ["bullseye", "checkout", "winner"]


def test_single_out_wins_on_any_dart():
    g = x01(301, ["Solo"])
    g.players[0].score = g.turn_start_score = 7
    assert "winner" in throw(g, "S7")


def test_checkout_suggestion():
    g = x01(double_out=True)
    g.players[0].score = g.turn_start_score = 170
    assert g.as_dict()["checkout"] == ["T20", "T20", "Bull"]
    throw(g, "T20")
    assert g.as_dict()["checkout"] == ["T20", "Bull"]
    g.players[0].score = 169
    assert g.as_dict()["checkout"] == []


@pytest.mark.parametrize(
    ("darts", "award"),
    [(("T20", "T20", "T20"), "ton_80"), (("T20", "T20", "S20"), "ton_40"), (("T20", "T20", "T17"), "high_ton"),
     (("T20", "S20", "S20"), "ton"), (("SB", "DB", "SB"), "hat_trick"), (("S5", "S5", "S5"), "three_in_a_bed")],
)
def test_turn_awards(darts, award):
    g = x01(701)
    assert award in throw(g, *darts)


def test_no_ton_below_100_and_on_bust():
    g = x01()
    assert throw(g, "T20", "S19", "S20") == []
    g = x01(301)
    g.players[0].score = g.turn_start_score = 101
    kinds = throw(g, "T20", "T20")
    assert kinds == ["bust"]


def test_bullseye_award_each_bull():
    g = x01()
    assert throw(g, "SB") == ["bullseye"]


def test_undo_through_turn_change_and_win():
    g = x01(301, ["A", "B"])
    throw(g, "T20")
    g.next_player()
    assert g.current == 1
    assert g.undo() and g.current == 0 and len(g.turn) == 1
    assert g.undo() and g.players[0].score == 301
    assert not g.undo()


def test_stats_ppd():
    g = x01()
    throw(g, "T20", "T20", "T20")
    g.next_player()
    stats = g.as_dict()["players"][0]["stats"]
    assert stats["ppd"] == 60.0 and stats["ppr"] == 180.0 and stats["best_turn"] == 180


def test_cricket_marks_points_and_close():
    g = Game()
    g.new_game("cricket", ["A", "B"])
    throw(g, "T20", "T20", "S19")
    a = g.players[0]
    assert a.marks["20"] == 6 and a.score == 60 and a.marks["19"] == 1
    g.next_player()
    throw(g, "T20", "T20")  # B closes 20; A already closed it, so no points
    b = g.players[1]
    assert b.marks["20"] == 6 and b.score == 0 and b.counted_marks == 3
    g.next_player()
    throw(g, "T20")  # closed by both: no points, dead marks
    assert a.score == 60
    assert throw(g, "S1") == []  # off-target dart is a miss in cricket
    assert a.counted_marks == 7


def test_cricket_bull_marks_and_win():
    g = Game()
    g.new_game("cricket", ["A", "B"])
    a = g.players[0]
    a.marks = {k: 3 for k in a.marks}
    a.marks["25"] = 1
    assert throw(g, "DB") == ["bullseye", "winner"]
    assert a.marks["25"] == 3


def test_cricket_no_win_when_behind():
    g = Game()
    g.new_game("cricket", ["A", "B"])
    a, b = g.players
    a.marks = {k: 3 for k in a.marks}
    a.marks["15"] = 2
    b.score = 100
    throw(g, "S15")
    assert g.status == "playing"


def test_white_horse():
    g = Game()
    g.new_game("cricket", ["A", "B"])
    assert "white_horse" in throw(g, "T20", "T19", "T18")
    g.next_player()
    assert "white_horse" not in throw(g, "T20", "T20", "T19")
    g.next_player()
    assert "white_horse" not in throw(g, "T20", "T19", "T14")


def test_cricket_mpr():
    g = Game()
    g.new_game("cricket", ["A", "B"])
    throw(g, "T20", "T19", "S18")
    assert g.as_dict()["players"][0]["stats"]["mpr"] == 7.0


def test_count_up_rounds_and_winner():
    g = Game()
    g.new_game("count_up", ["A", "B"], rounds=2)
    for darts in (("T20",), ("S1",), ("S5",), ("S1",)):
        throw(g, *darts)
        awards = g.next_player()
    assert [a["type"] for a in awards] == ["winner"]
    assert g.winner == "A" and g.players[0].score == 65


def test_around_the_clock():
    g = Game()
    g.new_game("around_the_clock", ["A"])
    throw(g, "S1", "T2", "S5")
    assert g.players[0].target == 3
    p = g.players[0]
    p.target = 20
    g.next_player()
    throw(g, "D20")
    assert p.target == 25
    assert "winner" in throw(g, "SB")


def test_unknown_frames_do_not_score():
    g = x01()
    assert g.throw(decode_frame("99.9@")) == []
    assert g.players[0].darts == 0


def test_miss_counts_as_dart():
    g = x01()
    throw(g, "MISS", "MISS", "MISS")
    assert g.turn_complete and g.players[0].darts == 3


def test_bad_options():
    with pytest.raises(GameError):
        Game().new_game("killer")
    with pytest.raises(GameError):
        Game().new_game("x01", start=401)
    g = Game()
    g.new_game("501")
    assert g.start == 501 and g.players[0].name == "Player 1"


def test_end_game_and_persistence_roundtrip():
    g = x01()
    throw(g, "T20")
    restored = Game.load(g.dump())
    assert restored.as_dict() | {"can_undo": None} == g.as_dict() | {"can_undo": None}
    g.end_game()
    assert g.status == "idle" and g.players == [] and g.winner is None
    assert g.undo() and g.status == "playing" and g.players
    assert Game.load({"garbage": 1, "players": [{"nope": 1}]}).status == "idle"


def test_ton_80_is_not_also_three_in_a_bed():
    assert throw(x01(), "T20", "T20", "T20") == ["ton_80"]
    assert throw(x01(), "T19", "T19", "T19") == ["high_ton", "three_in_a_bed"]
