from __future__ import annotations

from custom_components.granboard.career import CareerLog
from custom_components.granboard.game import Game
from custom_components.granboard.protocol import parse_segment


def _throw(game: Game, *segments: str) -> None:
    for segment in segments:
        game.throw(parse_segment(segment))


def _solo(start=501, double_out=False, profile_id="a1") -> Game:
    game = Game()
    game.new_game(
        "x01",
        [{"name": "Andrew", "color": "#ff0000", "profile_id": profile_id}],
        start=start,
        double_out=double_out,
        game_id="game-1",
    )
    return game


def test_commit_stats_heatmap_and_revert():
    game = _solo(701)
    # Nine darts of 140 (T20, T20, S20) — first-9 average 140, then a 180, then a checkout.
    for _ in range(3):
        _throw(game, "T20", "T20", "S20")
        game.next_player()
    _throw(game, "T20", "T20", "T20")  # 180, remaining 81
    game.next_player()
    game.players[0].score = game.turn_start_score = 40
    _throw(game, "D20")
    assert game.status == "finished" and game.winner == "Andrew"

    log = CareerLog()
    assert log.commit_from_game(game) is True
    assert log.commit_from_game(game) is False  # idempotent
    stats = log.stats_for("a1")
    assert stats["games"] == 1 and stats["wins"] == 1 and stats["win_rate"] == 100.0
    assert stats["games_by_mode"]["x01"] == {"played": 1, "wins": 1}
    assert stats["one_eighties"] == 1
    assert stats["ton_plus"] == 4  # three 140s and one 180
    # 140*3 + 180 + 40 = 640 points over 13 darts -> 147.69
    assert stats["three_dart_avg"] == 147.69
    assert stats["first_9_avg"] == 140.0
    assert stats["heatmap"]["T20"] == 9  # 2 per 140 visit * 3 + 3 in the 180, checkout is D20
    assert stats["heatmap"]["S20"] == 3
    assert stats["heatmap"]["D20"] == 1
    # Checkout and doubles: last visit started on 40, double out is off so checkoutable as single-out too.
    # With double_out False, 40 can be checked out, and D20 hits 40.
    assert stats["checkout_pct"] > 0
    guest_stats = log.stats_for(None)
    assert guest_stats["games"] == 0

    assert log.revert_game("game-1") is True
    assert log.stats_for("a1")["games"] == 0
    assert log.stats_for("a1")["heatmap"] == {}
    assert log.has_game("game-1") is False


def test_double_out_checkout_and_doubles_rate():
    game = _solo(301, double_out=True, profile_id="a1")
    game.game_id = "game-2"
    game.players[0].score = game.turn_start_score = 40
    _throw(game, "S20")  # remaining 20, not a finish
    _throw(game, "D10")
    assert game.status == "finished"
    log = CareerLog()
    log.commit_from_game(game)
    stats = log.stats_for("a1")
    assert stats["checkout_pct"] == 100.0
    # First dart at 40 is a double attempt (missed, it was a single); second at 20 is a hit.
    assert stats["doubles_hit_rate"] == 50.0
    assert stats["doubles_hit_rate"] == CareerLog.load(log.dump()).stats_for("a1")["doubles_hit_rate"]


def test_cricket_mpr_and_guest_is_not_logged():
    game = Game()
    game.new_game(
        "cricket",
        [
            {"name": "Andrew", "color": "#ff0000", "profile_id": "a1"},
            {"name": "Guest", "color": "#0000ff", "profile_id": None},
        ],
        rounds=1,
        game_id="game-3",
    )
    _throw(game, "T20", "T19", "T18")  # 9 marks
    game.next_player()
    _throw(game, "S15", "S15", "S15")
    game.next_player()  # round limit, Andrew leads
    assert game.status == "finished" and game.winner == "Andrew"
    log = CareerLog()
    log.commit_from_game(game)
    stats = log.stats_for("a1")
    assert stats["games"] == 1 and stats["cricket_mpr"] == 9.0  # 9 marks in 3 darts
    assert stats["games_by_mode"]["cricket"]["wins"] == 1
    # Guest has no profile id, so no career row and no throws attributed to them as aggregates.
    assert all(row.get("player_id") != None for row in log.throws if row.get("player") == "Andrew")
    assert "Guest" not in {p["name"] for g in log.games for p in g["players"] if p.get("player_id")}
    assert log.aggregates.keys() == {"a1"}


def test_visit_log_recent_games_and_summaries():
    from custom_components.granboard.career import hit_type_counts, summarize_player_visits

    game = _solo(501, double_out=True)
    # First 9: three 140s, then a 180, then leave 41 and check out 40 later — reuse the known pattern on 501.
    # 501 - 140*3 = 81, so the 180 would bust. Use the 701 pattern via a 501 that we force scores on.
    # Play a realistic short 501: 140, 140, 81 remaining after two 140s? 501-280=221. Another 140 -> 81.
    _throw(game, "T20", "T20", "S20")  # 140, 361
    game.next_player()
    _throw(game, "T20", "T20", "S20")  # 140, 221
    game.next_player()
    _throw(game, "T20", "T20", "S20")  # 140, 81
    game.next_player()
    _throw(game, "T19")  # 57, 24
    game.next_player()
    game.players[0].score = game.turn_start_score = 40
    # remaining is now 40 — next_player after T19 already set score to 24. Reset to 40 for a clean checkout.
    _throw(game, "D20")
    assert game.status == "finished"

    log = CareerLog()
    assert log.commit_from_game(game) is True
    stored = log.games[0]
    assert stored["visits"] == len(stored["visit_log"])
    assert stored["visit_log"][0]["dart_count"] == 3
    assert stored["visit_log"][0]["score"] == 140
    assert stored["visit_log"][-1]["after"] == 0
    assert stored["visit_log"][-1]["score"] == 40

    rows = log.recent_games(5)
    assert len(rows) == 1
    andrew = rows[0]["players"][0]
    assert andrew["name"] == "Andrew"
    assert andrew["color"] == "#ff0000"
    assert andrew["win"] is True
    assert andrew["one_eighties"] == 0
    assert andrew["one_forties"] == 3
    assert andrew["ton_plus"] == 3
    assert andrew["best_visit"] == 140
    assert andrew["checkout_hits"] == 1
    assert andrew["checkout_attempts"] >= 1
    assert andrew["three_dart_avg"] > 0
    assert andrew["first_9_avg"] == 140.0
    assert andrew["hit_types"]["triples"] >= 6
    assert andrew["hit_types"]["doubles"] == 1
    assert sum(b["count"] for b in andrew["visit_ranges"]) == andrew["visits"]

    # Same numbers from the helper used by the live game sensor.
    live = summarize_player_visits(
        stored["visit_log"],
        player_id="a1",
        player_name="Andrew",
        mode="x01",
        start=501,
        double_out=True,
    )
    assert live["best_visit"] == 140
    assert live["remaining_after"][-1] == 0
    types = hit_type_counts(stored["visit_log"])
    assert types["doubles"] == 1
    assert types["triples"] == 7  # two T20s per 140 visit x3, plus T19
    assert types["singles"] == 3  # three S20s; checkout is D20


def test_visit_log_trimmed_on_older_games_and_delta_fallback():
    log = CareerLog()
    for i in range(10):
        game = Game()
        game.new_game(
            "x01",
            [{"name": "Andrew", "color": "#ff0000", "profile_id": "a1"}],
            start=501,
            double_out=False,
            game_id=f"game-{i}",
        )
        _throw(game, "T20", "T20", "T20")
        game.next_player()
        game.players[0].score = game.turn_start_score = 40
        _throw(game, "S20", "S20")  # 40, win
        assert game.status == "finished"
        assert log.commit_from_game(game) is True

    assert len(log.games) == 10
    with_log = [g for g in log.games if g.get("visit_log")]
    without = [g for g in log.games if not g.get("visit_log")]
    assert len(with_log) == 8
    assert len(without) == 2
    assert without[0]["game_id"] == "game-0"
    assert "visit_log" not in without[0]
    assert without[0]["visits"] == 2  # still a count
    # Oldest still has deltas so recent_games fallback works if asked beyond the log window
    # recent_games(5) should all have visit_log
    recent = log.recent_games(5)
    assert len(recent) == 5
    assert all(row["visit_log"] for row in recent)
    assert recent[-1]["game_id"] == "game-9"
    assert recent[0]["players"][0]["best_visit"] == 180
    # A window that includes a trimmed game still returns averages from deltas
    older = log.recent_games(10)
    assert older[0]["game_id"] == "game-0"
    assert older[0]["visit_log"] == []
    assert older[0]["players"][0]["three_dart_avg"] > 0
    assert older[0]["players"][0]["best_visit"] == 0  # unknown without the log


def test_career_dump_roundtrip_keeps_visit_log():
    game = _solo()
    _throw(game, "T20", "T20", "S20")
    game.next_player()
    game.players[0].score = game.turn_start_score = 32
    _throw(game, "D16")
    log = CareerLog()
    log.commit_from_game(game)
    restored = CareerLog.load(log.dump())
    assert restored.games[0]["visit_log"][0]["dart_count"] == 3
    assert restored.recent_games(1)[0]["players"][0]["best_visit"] == 140
