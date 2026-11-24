from __future__ import annotations

from custom_components.granboard.career import CareerLog
from custom_components.granboard.game import Game
from custom_components.granboard.player_stats import (
    LAST_DART_KEY,
    LAST_VISIT_KEY,
    PLAYER_STATS,
    board_entity_id,
    player_entity_id,
)
from custom_components.granboard.protocol import parse_segment


def _throw(game: Game, *segments: str) -> None:
    for segment in segments:
        game.throw(parse_segment(segment))


def test_andrew_entity_ids_on_game_room_board():
    board = "game_room_granboard_3s"
    expected = {
        "three_dart_avg": "sensor.game_room_granboard_3s_andrew_3_dart_average",
        "first_9_avg": "sensor.game_room_granboard_3s_andrew_first_9_average",
        "checkout_pct": "sensor.game_room_granboard_3s_andrew_checkout_percent",
        "one_eighties": "sensor.game_room_granboard_3s_andrew_180s",
        "ton_plus": "sensor.game_room_granboard_3s_andrew_ton_plus",
        "games": "sensor.game_room_granboard_3s_andrew_games_played",
        "wins": "sensor.game_room_granboard_3s_andrew_games_won",
        "cricket_mpr": "sensor.game_room_granboard_3s_andrew_cricket_mpr",
        "highest_checkout": "sensor.game_room_granboard_3s_andrew_highest_checkout",
    }
    assert {stat.key for stat in PLAYER_STATS} == set(expected)
    for stat in PLAYER_STATS:
        assert player_entity_id(board, "Andrew", stat.suffix) == expected[stat.key]
    assert board_entity_id(board, LAST_VISIT_KEY) == "sensor.game_room_granboard_3s_last_visit_score"
    assert board_entity_id(board, LAST_DART_KEY) == "sensor.game_room_granboard_3s_last_dart_score"


def test_player_stats_cover_influx_fields():
    classes = {stat.key: stat.state_class for stat in PLAYER_STATS}
    assert classes["three_dart_avg"] == "measurement"
    assert classes["first_9_avg"] == "measurement"
    assert classes["checkout_pct"] == "measurement"
    assert classes["cricket_mpr"] == "measurement"
    assert classes["highest_checkout"] == "measurement"
    assert classes["one_eighties"] == "total"
    assert classes["ton_plus"] == "total"
    assert classes["games"] == "total"
    assert classes["wins"] == "total"
    units = {stat.key: stat.unit for stat in PLAYER_STATS}
    assert units["checkout_pct"] == "percent"
    assert units["three_dart_avg"] is None


def test_highest_checkout_tracks_max_and_recomputes_on_revert():
    def checkout_game(game_id: str, remaining: int) -> Game:
        game = Game()
        game.new_game(
            "x01",
            [{"name": "Andrew", "color": "#00ff00", "profile_id": "a1"}],
            start=301,
            double_out=False,
            game_id=game_id,
        )
        game.players[0].score = game.turn_start_score = remaining
        if remaining == 40:
            _throw(game, "D20")
        elif remaining == 80:
            _throw(game, "T20", "D10")
        else:
            raise AssertionError(remaining)
        assert game.status == "finished"
        return game

    log = CareerLog()
    first = checkout_game("game-40", 40)
    assert log.commit_from_game(first) is True
    assert log.stats_for("a1")["highest_checkout"] == 40
    assert log.stats_for("a1")["checkout_pct"] == 100.0

    second = checkout_game("game-80", 80)
    assert log.commit_from_game(second) is True
    assert log.stats_for("a1")["highest_checkout"] == 80
    assert log.stats_for("a1")["games"] == 2

    assert log.revert_game("game-80") is True
    assert log.stats_for("a1")["highest_checkout"] == 40
    assert log.stats_for("a1")["games"] == 1

    assert log.revert_game("game-40") is True
    assert log.stats_for("a1")["highest_checkout"] == 0
    assert log.stats_for("a1")["games"] == 0


def test_open_visit_and_history_snapshots():
    game = Game()
    game.new_game(
        "x01",
        [{"name": "Andrew", "color": "#00ff00", "profile_id": "a1"}],
        start=501,
        game_id="visit-1",
    )
    _throw(game, "T20", "T20", "S20")
    open_visit = game.open_visit_dict()
    assert open_visit is not None
    assert open_visit["score"] == 140
    assert open_visit["last_dart_score"] == 20
    assert open_visit["last_dart_segment"] == "S20"
    assert open_visit["player"] == "Andrew"
    assert open_visit["player_id"] == "a1"
    assert open_visit["dart_count"] == 3
    assert open_visit["bust"] is False

    game.next_player()
    assert game.open_visit_dict() is None
    hist = game.last_history_visit_dict()
    assert hist is not None
    assert hist["score"] == 140
    assert hist["last_dart_score"] == 20
    assert hist["last_dart_segment"] == "S20"
    assert hist["player_id"] == "a1"


def test_bust_visit_score_is_zero():
    game = Game()
    game.new_game(
        "x01",
        [{"name": "Andrew", "color": "#00ff00", "profile_id": "a1"}],
        start=501,
        game_id="bust-1",
    )
    game.players[0].score = game.turn_start_score = 10
    _throw(game, "S20")
    visit = game.open_visit_dict()
    assert visit is not None
    assert visit["bust"] is True
    assert visit["score"] == 0
    assert visit["last_dart_score"] == 20


def test_checkout_visit_snapshot_on_finish():
    game = Game()
    game.new_game(
        "x01",
        [{"name": "Andrew", "color": "#00ff00", "profile_id": "a1"}],
        start=501,
        double_out=False,
        game_id="out-1",
    )
    game.players[0].score = game.turn_start_score = 40
    _throw(game, "D20")
    assert game.status == "finished"
    visit = game.open_visit_dict()
    assert visit is not None
    assert visit["score"] == 40
    assert visit["last_dart_score"] == 40
    assert visit["last_dart_segment"] == "D20"
