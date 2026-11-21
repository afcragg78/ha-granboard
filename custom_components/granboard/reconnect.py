"""Reconnect timing for the board link. Pure Python."""

from __future__ import annotations

import random
import time

WARMUP_SECONDS = 2.0


def backoff_seconds(attempt: int, *, start: float = 2.0, cap: float = 60.0, jitter: float = 0.2, roll: float | None = None) -> float:
    """Attempt 0 is about 2 s, then it doubles, capped at 60 s, with +/-20 % jitter."""
    base = min(cap, start * (2 ** max(0, int(attempt))))
    fraction = random.random() if roll is None else min(1.0, max(0.0, float(roll)))
    return max(0.05, base * (1.0 + (fraction * 2.0 - 1.0) * jitter))


class WarmupGate:
    """Drop frames for a short time after connecting; the board can replay the last hit."""

    def __init__(self, seconds: float = WARMUP_SECONDS, clock=time.monotonic) -> None:
        self.seconds = seconds
        self._clock = clock
        self._until = 0.0

    def arm(self) -> None:
        self._until = self._clock() + self.seconds

    def open(self) -> bool:
        return self._clock() >= self._until
