"""Darts game engine: x01, Cricket, Count-Up, Around the Clock. Pure Python.

The integration owns one :class:`Game` per board. The dashboard only reads
``Game.as_dict()`` (the ``game`` sensor attributes) and calls services.

Turns are three darts. After the third dart, a bust, or a win, the turn is
complete and further darts are ignored until ``next_player``. ``undo``
restores the state before the last dart or turn change, any number of times.
"""

from __future__ import annotations

import copy
from uuid import uuid4
from dataclasses import dataclass, field
from typing import Any

from .colors import player_color
from .checkout import suggest_checkout
from .protocol import Hit

GAME_X01 = "x01"
GAME_CRICKET = "cricket"
GAME_COUNT_UP = "count_up"
GAME_AROUND_THE_CLOCK = "around_the_clock"
GAMES = (GAME_X01, GAME_CRICKET, GAME_COUNT_UP, GAME_AROUND_THE_CLOCK)
X01_STARTS = (301, 501, 701)

STATUS_IDLE = "idle"
STATUS_PLAYING = "playing"
STATUS_FINISHED = "finished"

CRICKET_NUMBERS = (20, 19, 18, 17, 16, 15, 25)
DARTS_PER_TURN = 3
HISTORY_LIMIT = 120
UNDO_LIMIT = 300
DEFAULT_COUNT_UP_ROUNDS = 8

AWARD_BULLSEYE = "bullseye"
AWARD_TON = "ton"
AWARD_TON_40 = "ton_40"
AWARD_HIGH_TON = "high_ton"
AWARD_TON_80 = "ton_80"
AWARD_HAT_TRICK = "hat_trick"
AWARD_THREE_IN_A_BED = "three_in_a_bed"
AWARD_WHITE_HORSE = "white_horse"
AWARD_BUST = "bust"
AWARD_WINNER = "winner"
AWARD_CHECKOUT = "checkout"
AWARDS = (
    AWARD_BULLSEYE,
    AWARD_TON,
    AWARD_TON_40,
    AWARD_HIGH_TON,
    AWARD_TON_80,
    AWARD_HAT_TRICK,
    AWARD_THREE_IN_A_BED,
    AWARD_WHITE_HORSE,
    AWARD_BUST,
    AWARD_WINNER,
)


def _dart(hit: Hit) -> dict[str, Any]:
    return {
        "segment": hit.segment,
        "number": hit.number,
        "multiplier": hit.multiplier,
        "score": hit.score,
        "ring": hit.ring,
    }


@dataclass
class Player:
    name: str
    score: int = 0
    marks: dict[str, int] = field(default_factory=dict)
    target: int = 1  # around the clock
    darts: int = 0
    points: int = 0  # points that counted (x01: excluding busts)
    counted_marks: int = 0  # cricket marks that closed or scored
    turns: int = 0
    best_turn: int = 0
    hits: int = 0  # around the clock targets hit
    finished_rank: int | None = None
    color: str = ""
    profile_id: str | None = None

    def stats(self, game: str) -> dict[str, Any]:
        darts = self.darts
        ppd = round(self.points / darts, 2) if darts else 0.0
        stats: dict[str, Any] = {
            "darts": darts,
            "turns": self.turns,
            "ppd": ppd,
            "ppr": round(ppd * DARTS_PER_TURN, 2),
            "best_turn": self.best_turn,
        }
        if game == GAME_CRICKET:
            stats["mpr"] = round(self.counted_marks * DARTS_PER_TURN / darts, 2) if darts else 0.0
            stats["marks"] = self.counted_marks
        if game == GAME_AROUND_THE_CLOCK:
            stats["hit_rate"] = round(self.hits / darts, 2) if darts else 0.0
        return stats



def _player_specs(players: list[object] | None, colors: list[object] | None) -> list[dict[str, Any]]:
    """Accept a list of names or dicts with name / color / profile_id."""
    colors = list(colors or [])
    specs: list[dict[str, Any]] = []
    for index, raw in enumerate(players or []):
        if isinstance(raw, dict):
            name = str(raw.get("name") or "").strip()
            color = player_color(index, raw["color"] if raw.get("color") not in (None, "") else (colors[index] if index < len(colors) else None))
            profile_id = raw.get("profile_id") or None
        else:
            name = str(raw).strip()
            color = player_color(index, colors[index] if index < len(colors) else None)
            profile_id = None
        if not name:
            continue
        specs.append({"name": name, "color": color, "profile_id": profile_id})
    return specs or [{"name": "Player 1", "color": player_color(0), "profile_id": None}]



def build_visit(
    player: Player,
    *,
    game: str | None,
    round_no: int,
    turn: list[dict[str, Any]],
    score: int,
    bust: bool,
    after: int,
) -> dict[str, Any]:
    """One completed (or just-finished) visit, as stored in ``history`` and the career log."""
    entry: dict[str, Any] = {
        "player": player.name,
        "player_id": player.profile_id,
        "round": round_no,
        "darts": [d["segment"] for d in turn],
        "score": score,
        "bust": bust,
        "after": after,
        "dart_count": len(turn),
    }
    if game == GAME_CRICKET:
        entry["marks"] = sum(int(d.get("marks") or 0) for d in turn)
        entry["marks_after"] = dict(player.marks)
    return entry


class GameError(ValueError):
    """A service was called with options the engine cannot play."""


class Game:
    """One game at a time. ``throw`` returns the awards it caused."""

    def __init__(self) -> None:
        self.status = STATUS_IDLE
        self.game: str | None = None
        self.start = 501
        self.double_out = False
        self.max_rounds = 0
        self.players: list[Player] = []
        self.current = 0
        self.round = 1
        self.turn: list[dict[str, Any]] = []
        self.turn_start_score = 0
        self.turn_complete = False
        self.turn_bust = False
        self.history: list[dict[str, Any]] = []
        self.winner: str | None = None
        self.game_id: str | None = None
        self.last_awards: list[dict[str, Any]] = []
        self._undo: list[dict[str, Any]] = []

    # ------------------------------------------------------------ setup
    def new_game(
        self,
        game: str,
        players: list[str] | list[dict[str, Any]] | None = None,
        *,
        start: int = 501,
        double_out: bool = False,
        rounds: int | None = None,
        colors: list[object] | None = None,
        game_id: str | None = None,
    ) -> None:
        game = str(game).strip().lower().replace("-", "_").replace(" ", "_")
        if game in ("301", "501", "701"):
            start, game = int(game), GAME_X01
        if game not in GAMES:
            raise GameError(f"Unknown game {game!r}; use one of {', '.join(GAMES)}")
        if game == GAME_X01 and int(start) not in X01_STARTS:
            raise GameError(f"x01 start must be one of {X01_STARTS}")
        specs = _player_specs(players, colors)
        if len(specs) > 8:
            raise GameError("At most 8 players")
        self.__init__()  # type: ignore[misc]
        self.game = game
        self.game_id = game_id or uuid4().hex
        self.start = int(start)
        self.double_out = bool(double_out) if game == GAME_X01 else False
        if rounds is None:
            rounds = DEFAULT_COUNT_UP_ROUNDS if game == GAME_COUNT_UP else 0
        self.max_rounds = max(0, int(rounds))
        if game == GAME_COUNT_UP and self.max_rounds == 0:
            self.max_rounds = DEFAULT_COUNT_UP_ROUNDS
        for index, spec in enumerate(specs):
            player = Player(name=spec["name"], color=spec["color"], profile_id=spec.get("profile_id"))
            if game == GAME_X01:
                player.score = self.start
            if game == GAME_CRICKET:
                player.marks = {str(n): 0 for n in CRICKET_NUMBERS}
            self.players.append(player)
        self.status = STATUS_PLAYING
        self.turn_start_score = self.players[0].score

    def end_game(self) -> None:
        """Clear the game (playing or finished) back to a blank idle board.

        The cleared game stays on the undo stack, so Undo brings it back.
        """
        if self.status == STATUS_IDLE and not self.players:
            return
        self._snapshot()
        undo = self._undo
        self.__init__()
        self._undo = undo

    # ------------------------------------------------------------- undo
    def _snapshot(self) -> None:
        state = {k: copy.deepcopy(v) for k, v in self.__dict__.items() if k != "_undo"}
        self._undo.append(state)
        if len(self._undo) > UNDO_LIMIT:
            del self._undo[0]

    def undo(self) -> bool:
        if not self._undo:
            return False
        state = self._undo.pop()
        undo = self._undo
        self.__dict__.update(state)
        self._undo = undo
        self.last_awards = []
        return True

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    # ------------------------------------------------------------ throws
    @property
    def player(self) -> Player:
        return self.players[self.current]

    def throw(self, hit: Hit) -> list[dict[str, Any]]:
        """Score one dart. Returns award dicts (``type``, ``player``, ...)."""
        self.last_awards = []
        if self.status != STATUS_PLAYING or self.turn_complete or not hit.known:
            return []
        self._snapshot()
        player = self.player
        player.darts += 1
        dart = _dart(hit)
        awards: list[dict[str, Any]] = []
        if hit.is_bull:
            awards.append(self._award(AWARD_BULLSEYE, segment=hit.segment, score=hit.score))
        if self.game == GAME_X01:
            self._throw_x01(hit, dart, awards)
        elif self.game == GAME_CRICKET:
            self._throw_cricket(hit, dart, awards)
        elif self.game == GAME_COUNT_UP:
            player.score += hit.score
            player.points += hit.score
        elif self.game == GAME_AROUND_THE_CLOCK:
            if hit.number == player.target and hit.number:
                player.hits += 1
                dart["advanced"] = True
                player.target = 25 if player.target == 20 else (0 if player.target == 25 else player.target + 1)
                player.score += 1
                if player.target == 0:
                    self._win(player, awards)
        self.turn.append(dart)
        if len(self.turn) >= DARTS_PER_TURN or self.status == STATUS_FINISHED:
            self.turn_complete = True
        if self.turn_complete and not self.turn_bust:
            awards.extend(self._turn_awards())
        if self.status == STATUS_FINISHED:
            # Turn awards before the winner banner.
            awards.sort(key=lambda a: a["type"] == AWARD_WINNER)
        self.last_awards = awards
        return awards

    def _throw_x01(self, hit: Hit, dart: dict[str, Any], awards: list[dict[str, Any]]) -> None:
        player = self.player
        after = player.score - hit.score
        bust = after < 0 or (self.double_out and (after == 1 or (after == 0 and hit.multiplier != 2)))
        if bust:
            dart["bust"] = True
            player.score = self.turn_start_score
            # Points from this turn's earlier darts no longer count.
            player.points -= sum(d["score"] for d in self.turn)
            self.turn_bust = True
            self.turn_complete = True
            awards.append(self._award(AWARD_BUST, score=self.turn_start_score))
            return
        player.score = after
        player.points += hit.score
        if after == 0:
            awards.append(self._award(AWARD_CHECKOUT, score=self.turn_start_score, segment=hit.segment, double=hit.multiplier == 2))
            self._win(player, awards)

    def _throw_cricket(self, hit: Hit, dart: dict[str, Any], awards: list[dict[str, Any]]) -> None:
        key = str(hit.number)
        player = self.player
        if key not in player.marks:
            dart["marks"] = 0
            dart["points"] = 0
            return
        before = player.marks[key]
        marks = hit.multiplier
        closing = max(0, min(marks, 3 - before))
        extra = marks - closing
        open_elsewhere = any(p.marks[key] < 3 for p in self.players if p is not player)
        points = hit.number * extra if open_elsewhere else 0
        player.marks[key] = before + marks
        player.score += points
        player.points += points
        counted = closing + (extra if open_elsewhere else 0)
        player.counted_marks += counted
        dart["marks"] = counted
        dart["points"] = points
        if self._cricket_won(player):
            self._win(player, awards)

    def _cricket_won(self, player: Player) -> bool:
        if any(v < 3 for v in player.marks.values()):
            return False
        return all(player.score >= p.score for p in self.players if p is not player)

    def _turn_awards(self) -> list[dict[str, Any]]:
        darts = self.turn
        awards: list[dict[str, Any]] = []
        total = sum(d["score"] for d in darts)
        if self.game in (GAME_X01, GAME_COUNT_UP):
            if total >= 180:
                awards.append(self._award(AWARD_TON_80, score=total))
            elif total >= 151:
                awards.append(self._award(AWARD_HIGH_TON, score=total))
            elif total >= 140:
                awards.append(self._award(AWARD_TON_40, score=total))
            elif total >= 100:
                awards.append(self._award(AWARD_TON, score=total))
        if len(darts) == DARTS_PER_TURN:
            if all(d["number"] == 25 for d in darts):
                awards.append(self._award(AWARD_HAT_TRICK, score=total))
            elif total < 180 and darts[0]["number"] and all(
                (d["number"], d["multiplier"]) == (darts[0]["number"], darts[0]["multiplier"]) for d in darts
            ):
                # Three T20 is a Ton 80 only.
                awards.append(self._award(AWARD_THREE_IN_A_BED, segment=darts[0]["segment"], score=total))
            if (
                self.game == GAME_CRICKET
                and all(d["multiplier"] == 3 and d["number"] in CRICKET_NUMBERS for d in darts)
                and len({d["number"] for d in darts}) == 3
            ):
                awards.append(self._award(AWARD_WHITE_HORSE, score=total))
        return awards

    def _award(self, kind: str, **extra: Any) -> dict[str, Any]:
        return {
            "type": kind,
            "player": self.player.name,
            "player_index": self.current,
            "player_id": self.player.profile_id,
            "color": self.color_of(self.current),
            **extra,
        }

    def color_of(self, index: int | None) -> str:
        if index is None or not self.players:
            return player_color(0)
        return self.players[index].color or player_color(index)

    def _win(self, player: Player, awards: list[dict[str, Any]]) -> None:
        self.winner = player.name
        self.status = STATUS_FINISHED
        self.turn_complete = True
        awards.append(self._award(AWARD_WINNER))

    # ------------------------------------------------------------ turns
    def next_player(self) -> list[dict[str, Any]]:
        """Close the turn (even with darts left) and move on."""
        self.last_awards = []
        if self.status != STATUS_PLAYING:
            return []
        self._snapshot()
        player = self.player
        total = self.turn_total()
        player.turns += 1
        player.best_turn = max(player.best_turn, total)
        self.history.append(
            build_visit(
                player,
                game=self.game,
                round_no=self.round,
                turn=self.turn,
                score=total,
                bust=self.turn_bust,
                after=player.score,
            )
        )
        if len(self.history) > HISTORY_LIMIT:
            del self.history[0]
        self.current = (self.current + 1) % len(self.players)
        if self.current == 0:
            self.round += 1
        self.turn = []
        self.turn_complete = False
        self.turn_bust = False
        self.turn_start_score = self.player.score
        awards: list[dict[str, Any]] = []
        if self.max_rounds and self.round > self.max_rounds:
            self.round = self.max_rounds
            leader = self._leader()
            self.current = self.players.index(leader)
            self._win(leader, awards)
        self.last_awards = awards
        return awards


    def turn_total(self) -> int:
        """Points this visit counts, or 0 on a bust."""
        if self.turn_bust:
            return 0
        if self.game == GAME_CRICKET:
            return sum(d.get("points", d["score"]) for d in self.turn)
        return sum(d["score"] for d in self.turn)

    def open_visit_dict(self) -> dict[str, Any] | None:
        """The in-progress or just-finished turn, before it is written to history."""
        if not self.turn:
            return None
        last = self.turn[-1]
        entry = build_visit(
            self.player,
            game=self.game,
            round_no=self.round,
            turn=self.turn,
            score=self.turn_total(),
            bust=self.turn_bust,
            after=self.player.score,
        )
        entry["last_dart_score"] = int(last.get("score") or 0)
        entry["last_dart_segment"] = last.get("segment")
        return entry

    def last_history_visit_dict(self) -> dict[str, Any] | None:
        """The visit that was just appended by ``next_player``."""
        if not self.history:
            return None
        last = self.history[-1]
        darts = [str(s) for s in (last.get("darts") or [])]
        last_score = 0
        last_segment = None
        if darts:
            from .protocol import parse_segment

            try:
                hit = parse_segment(darts[-1])
                last_score = hit.score
                last_segment = hit.segment
            except ValueError:
                last_segment = darts[-1]
        return {
            "player": last.get("player"),
            "player_id": last.get("player_id"),
            "round": last.get("round"),
            "score": int(last.get("score") or 0),
            "bust": bool(last.get("bust")),
            "darts": darts,
            "dart_count": len(darts),
            "last_dart_score": last_score,
            "last_dart_segment": last_segment,
        }

    def _leader(self) -> Player:
        if self.game == GAME_X01:
            return min(self.players, key=lambda p: p.score)
        if self.game == GAME_CRICKET:
            return max(self.players, key=lambda p: (p.score, p.counted_marks))
        return max(self.players, key=lambda p: p.score)

    # ------------------------------------------------------------ state
    def checkout(self) -> list[str]:
        if self.game != GAME_X01 or self.status != STATUS_PLAYING or self.turn_complete:
            return []
        return list(suggest_checkout(self.player.score, DARTS_PER_TURN - len(self.turn), self.double_out))

    def as_dict(self) -> dict[str, Any]:
        playing = self.status != STATUS_IDLE or bool(self.players)
        return {
            "game": self.game,
            "start": self.start if self.game == GAME_X01 else None,
            "double_out": self.double_out,
            "rounds": self.max_rounds or None,
            "round": self.round if playing else None,
            "current_player": self.current if playing else None,
            "current_player_name": self.player.name if self.players else None,
            "current_player_color": self.color_of(self.current) if self.players else None,
            "darts": list(self.turn),
            "darts_left": DARTS_PER_TURN - len(self.turn),
            "turn_score": self.turn_total(),
            "turn_complete": self.turn_complete,
            "bust": self.turn_bust,
            "winner": self.winner,
            "checkout": self.checkout(),
            "game_id": self.game_id,
            "players": [
                {
                    "name": p.name,
                    "profile_id": p.profile_id,
                    "color": p.color or player_color(i),
                    "score": p.score,
                    **({"marks": dict(p.marks)} if self.game == GAME_CRICKET else {}),
                    **({"target": "Bull" if p.target == 25 else p.target} if self.game == GAME_AROUND_THE_CLOCK else {}),
                    "stats": p.stats(self.game or ""),
                }
                for i, p in enumerate(self.players)
            ],
            "history": list(self.history),
            "last_awards": list(self.last_awards),
            "can_undo": self.can_undo,
        }

    # ------------------------------------------------------- persistence
    def dump(self) -> dict[str, Any]:
        """JSON-safe state for Home Assistant storage (no undo stack)."""
        data = {k: copy.deepcopy(v) for k, v in self.__dict__.items() if k not in ("_undo", "players")}
        data["players"] = [p.__dict__.copy() for p in self.players]
        return data

    @classmethod
    def load(cls, data: dict[str, Any] | None) -> Game:
        game = cls()
        if not data:
            return game
        try:
            players = [Player(**p) for p in data.get("players", [])]
            for key, value in data.items():
                if key != "players" and key in game.__dict__:
                    setattr(game, key, value)
            game.players = players
            if game.status != STATUS_IDLE and not players:
                game.status = STATUS_IDLE
        except (TypeError, ValueError):
            return cls()
        return game
