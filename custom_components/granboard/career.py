"""Per-throw / per-game career log and aggregate stats. Pure Python."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .checkout import suggest_checkout
from .game import DARTS_PER_TURN, GAME_CRICKET, GAME_X01, STATUS_FINISHED, Game
from .protocol import parse_segment

CAREER_STORAGE_KEY = "granboard.career"
CAREER_STORAGE_VERSION = 1
THROW_LIMIT = 8000
GAME_LIMIT = 400


def _empty_aggregate() -> dict[str, Any]:
    return {
        "darts": 0,
        "points": 0,
        "first9_darts": 0,
        "first9_points": 0,
        "checkout_attempts": 0,
        "checkout_hits": 0,
        "doubles_attempts": 0,
        "doubles_hits": 0,
        "one_eighties": 0,
        "ton_plus": 0,
        "cricket_marks": 0,
        "cricket_darts": 0,
        "games": 0,
        "wins": 0,
        "games_by_mode": {},
        "heatmap": {},
    }


def _pct(hits: int, attempts: int) -> float:
    if not attempts:
        return 0.0
    return round(100.0 * hits / attempts, 1)


def _avg(points: float, darts: int) -> float:
    if not darts:
        return 0.0
    return round(points * DARTS_PER_TURN / darts, 2)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _checkoutable(remaining: int, darts_left: int, double_out: bool) -> bool:
    return bool(suggest_checkout(remaining, darts_left, double_out))


def _is_double_attempt(remaining: int, double_out: bool) -> bool:
    if not double_out or remaining <= 0:
        return False
    if remaining == 50:
        return True
    return remaining <= 40 and remaining % 2 == 0


def _double_hit(remaining: int, segment: str, score: int, ring: str) -> bool:
    if remaining == 50:
        return segment == "DB" or ring == "bullseye"
    return score == remaining and (ring == "double" or segment.startswith("D"))


def _decode(segment: str) -> dict[str, Any]:
    try:
        hit = parse_segment(segment)
    except ValueError:
        return {"segment": segment, "number": 0, "multiplier": 0, "score": 0, "ring": "unknown"}
    return {"segment": hit.segment, "number": hit.number, "multiplier": hit.multiplier, "score": hit.score, "ring": hit.ring}


def _visit_start_score(visit: dict[str, Any], mode: str, start: int | None) -> int | None:
    if mode != GAME_X01:
        return None
    after = visit.get("after")
    score = int(visit.get("score") or 0)
    if after is None:
        return start
    if visit.get("bust"):
        return int(after)
    return int(after) + score


def _finished_visits(game: Game) -> list[dict[str, Any]]:
    visits = [dict(v) for v in game.history]
    if game.turn:
        player = game.player
        if game.game == GAME_CRICKET:
            total = 0 if game.turn_bust else sum(d.get("points", d["score"]) for d in game.turn)
        else:
            total = 0 if game.turn_bust else sum(d["score"] for d in game.turn)
        visits.append(
            {
                "player": player.name,
                "player_id": player.profile_id,
                "round": game.round,
                "darts": [d["segment"] for d in game.turn],
                "score": total,
                "bust": game.turn_bust,
                "after": player.score,
            }
        )
    return visits


def stats_from_aggregate(agg: dict[str, Any] | None) -> dict[str, Any]:
    """Public career stats for a profile (zeros when the player has not played)."""
    row = agg or _empty_aggregate()
    modes = {
        mode: {"played": int(v.get("played") or 0), "wins": int(v.get("wins") or 0)}
        for mode, v in (row.get("games_by_mode") or {}).items()
    }
    games = int(row.get("games") or 0)
    wins = int(row.get("wins") or 0)
    return {
        "three_dart_avg": _avg(int(row.get("points") or 0), int(row.get("darts") or 0)),
        "first_9_avg": _avg(int(row.get("first9_points") or 0), int(row.get("first9_darts") or 0)),
        "checkout_pct": _pct(int(row.get("checkout_hits") or 0), int(row.get("checkout_attempts") or 0)),
        "doubles_hit_rate": _pct(int(row.get("doubles_hits") or 0), int(row.get("doubles_attempts") or 0)),
        "one_eighties": int(row.get("one_eighties") or 0),
        "ton_plus": int(row.get("ton_plus") or 0),
        "cricket_mpr": _avg(int(row.get("cricket_marks") or 0), int(row.get("cricket_darts") or 0)),
        "win_rate": _pct(wins, games),
        "games": games,
        "wins": wins,
        "games_by_mode": modes,
        "heatmap": dict(row.get("heatmap") or {}),
    }


def _empty_delta() -> dict[str, Any]:
    return {
        "darts": 0,
        "points": 0,
        "first9_darts": 0,
        "first9_points": 0,
        "checkout_attempts": 0,
        "checkout_hits": 0,
        "doubles_attempts": 0,
        "doubles_hits": 0,
        "one_eighties": 0,
        "ton_plus": 0,
        "cricket_marks": 0,
        "cricket_darts": 0,
        "games": 0,
        "wins": 0,
        "mode": "",
        "heatmap": {},
    }


def _apply_delta(agg: dict[str, Any], delta: dict[str, Any], sign: int) -> None:
    for key in (
        "darts",
        "points",
        "first9_darts",
        "first9_points",
        "checkout_attempts",
        "checkout_hits",
        "doubles_attempts",
        "doubles_hits",
        "one_eighties",
        "ton_plus",
        "cricket_marks",
        "cricket_darts",
        "games",
        "wins",
    ):
        agg[key] = max(0, int(agg.get(key) or 0) + sign * int(delta.get(key) or 0))
    mode = delta.get("mode") or ""
    if mode and delta.get("games"):
        modes = agg.setdefault("games_by_mode", {})
        row = modes.setdefault(mode, {"played": 0, "wins": 0})
        row["played"] = max(0, int(row.get("played") or 0) + sign * int(delta.get("games") or 0))
        row["wins"] = max(0, int(row.get("wins") or 0) + sign * int(delta.get("wins") or 0))
        if row["played"] == 0 and row["wins"] == 0:
            modes.pop(mode, None)
    heatmap = agg.setdefault("heatmap", {})
    for segment, count in (delta.get("heatmap") or {}).items():
        heatmap[segment] = int(heatmap.get(segment) or 0) + sign * int(count)
        if heatmap[segment] <= 0:
            heatmap.pop(segment, None)


def _visit_metrics(
    visit: dict[str, Any],
    *,
    mode: str,
    start: int | None,
    double_out: bool,
    already: int,
) -> dict[str, int]:
    segments = [str(s) for s in (visit.get("darts") or [])]
    bust = bool(visit.get("bust"))
    score = 0 if bust else int(visit.get("score") or 0)
    remaining = _visit_start_score(visit, mode, start)
    first9_darts = 0
    first9_points = 0
    double_attempts = 0
    double_hits = 0
    prefix = 0
    left = remaining
    for index, segment in enumerate(segments):
        decoded = _decode(segment)
        if mode == GAME_X01 and already + index < 9:
            first9_darts += 1
            if not bust:
                first9_points += int(decoded["score"])
        if left is not None and _is_double_attempt(int(left), double_out):
            double_attempts += 1
            if _double_hit(int(left), decoded["segment"], int(decoded["score"]), str(decoded["ring"])):
                double_hits += 1
        if left is not None and not bust:
            left = int(left) - int(decoded["score"])
        prefix += int(decoded["score"])
    checkout_attempt = 0
    checkout_hit = 0
    if mode == GAME_X01 and remaining is not None and _checkoutable(int(remaining), DARTS_PER_TURN, double_out):
        checkout_attempt = 1
        if not bust and visit.get("after") == 0:
            checkout_hit = 1
    # If a bust visit had first-9 darts, those points do not count.
    if bust:
        first9_points = 0
    return {
        "first9_darts": first9_darts,
        "first9_points": first9_points,
        "doubles_attempts": double_attempts,
        "doubles_hits": double_hits,
        "one_eighties": 1 if not bust and score == 180 else 0,
        "ton_plus": 1 if not bust and score >= 100 else 0,
        "checkout_attempts": checkout_attempt,
        "checkout_hits": checkout_hit,
    }


def _throw_rows(game_id: str, mode: str, start: int | None, double_out: bool, visit: dict[str, Any], recorded_at: str) -> list[dict[str, Any]]:
    rows = []
    for segment in visit.get("darts") or []:
        decoded = _decode(str(segment))
        rows.append(
            {
                "game_id": game_id,
                "player_id": visit.get("player_id"),
                "player": visit.get("player"),
                "mode": mode,
                "start": start,
                "double_out": double_out,
                "segment": decoded["segment"],
                "number": decoded["number"],
                "multiplier": decoded["multiplier"],
                "score": decoded["score"],
                "ring": decoded["ring"],
                "bust": bool(visit.get("bust")),
                "visit_score": visit.get("score"),
                "time": recorded_at,
            }
        )
    return rows


class CareerLog:
    """Rolling throw/game log plus cumulative aggregates that survive trimming."""

    def __init__(self) -> None:
        self.throws: list[dict[str, Any]] = []
        self.games: list[dict[str, Any]] = []
        self.aggregates: dict[str, dict[str, Any]] = {}

    def stats_for(self, player_id: str | None) -> dict[str, Any]:
        if not player_id:
            return stats_from_aggregate(None)
        return stats_from_aggregate(self.aggregates.get(player_id))

    def has_game(self, game_id: str | None) -> bool:
        return bool(game_id) and any(g.get("game_id") == game_id for g in self.games)

    def commit_from_game(self, game: Game) -> bool:
        """Add one finished game to the log. Safe to call more than once."""
        if game.status != STATUS_FINISHED or not game.game_id or self.has_game(game.game_id):
            return False
        mode = game.game or ""
        start = game.start if mode == GAME_X01 else None
        visits = _finished_visits(game)
        recorded_at = _iso_now()
        throws: list[dict[str, Any]] = []
        deltas: dict[str, dict[str, Any]] = {}
        darts_so_far: dict[str, int] = {}
        for visit in visits:
            player_id = visit.get("player_id")
            throws.extend(_throw_rows(game.game_id, mode, start, game.double_out, visit, recorded_at))
            if not player_id:
                continue
            metrics = _visit_metrics(
                visit, mode=mode, start=start, double_out=game.double_out, already=darts_so_far.get(player_id, 0)
            )
            darts_so_far[player_id] = darts_so_far.get(player_id, 0) + len(visit.get("darts") or [])
            delta = deltas.setdefault(player_id, _empty_delta())
            delta["mode"] = mode
            for key, value in metrics.items():
                delta[key] = int(delta.get(key) or 0) + value
            for segment in visit.get("darts") or []:
                heatmap = delta.setdefault("heatmap", {})
                heatmap[str(segment)] = int(heatmap.get(str(segment)) or 0) + 1

        players_out: list[dict[str, Any]] = []
        for player in game.players:
            is_winner = player.name == game.winner
            players_out.append(
                {
                    "player_id": player.profile_id,
                    "name": player.name,
                    "score": player.score,
                    "color": player.color,
                    "win": is_winner,
                }
            )
            if not player.profile_id:
                continue
            delta = deltas.setdefault(player.profile_id, _empty_delta())
            delta["mode"] = mode
            delta["darts"] = player.darts
            delta["points"] = player.points
            delta["games"] = 1
            delta["wins"] = 1 if is_winner else 0
            if mode == GAME_CRICKET:
                delta["cricket_marks"] = player.counted_marks
                delta["cricket_darts"] = player.darts
            agg = self.aggregates.setdefault(player.profile_id, _empty_aggregate())
            _apply_delta(agg, delta, 1)

        winner_id = next((p["player_id"] for p in players_out if p["win"]), None)
        self.throws.extend(throws)
        self.games.append(
            {
                "game_id": game.game_id,
                "mode": mode,
                "start": start,
                "double_out": game.double_out,
                "winner": game.winner,
                "winner_id": winner_id,
                "players": players_out,
                "deltas": deltas,
                "visits": len(visits),
                "time": recorded_at,
            }
        )
        self._trim()
        return True

    def revert_game(self, game_id: str | None) -> bool:
        """Remove a committed game (undo of a finish) and roll back aggregates."""
        if not game_id:
            return False
        row = next((g for g in self.games if g.get("game_id") == game_id), None)
        if row is None:
            return False
        for player_id, delta in (row.get("deltas") or {}).items():
            if player_id in self.aggregates:
                _apply_delta(self.aggregates[player_id], delta, -1)
        self.throws = [t for t in self.throws if t.get("game_id") != game_id]
        self.games = [g for g in self.games if g.get("game_id") != game_id]
        return True

    def _trim(self) -> None:
        if len(self.throws) > THROW_LIMIT:
            del self.throws[: len(self.throws) - THROW_LIMIT]
        if len(self.games) > GAME_LIMIT:
            del self.games[: len(self.games) - GAME_LIMIT]

    def dump(self) -> dict[str, Any]:
        return {
            "throws": list(self.throws),
            "games": list(self.games),
            "aggregates": {key: dict(value) for key, value in self.aggregates.items()},
        }

    @classmethod
    def load(cls, data: dict[str, Any] | None) -> CareerLog:
        log = cls()
        if not data:
            return log
        try:
            log.throws = [dict(row) for row in data.get("throws") or []]
            log.games = [dict(row) for row in data.get("games") or []]
            log.aggregates = {str(key): dict(value) for key, value in (data.get("aggregates") or {}).items()}
            log._trim()
        except (TypeError, ValueError):
            return cls()
        return log
