"""Checkout suggestions for x01. Pure Python.

Fewest darts first, then a weighted mix of the most comfortable finishing
double and the most natural setup darts (big trebles before singles). Bogey numbers
(169, 168, 166, 165, 163, 162, 159) and anything over 170 have none.
"""

from __future__ import annotations

from functools import lru_cache

# Finishing doubles, most preferred first. Bull (DB) after the common doubles.
_DOUBLE_ORDER = [20, 16, 8, 18, 12, 10, 4, 2, 14, 6, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1]

Dart = tuple[str, int]  # (label, score)


def _setup_darts() -> list[Dart]:
    """Setup darts, most natural first: big trebles, then singles, then the rest."""
    darts: list[Dart] = [(f"T{n}", 3 * n) for n in range(20, 14, -1)]
    darts.extend((f"S{n}", n) for n in range(20, 0, -1))
    darts.append(("Bull", 50))
    darts.append(("25", 25))
    darts.extend((f"T{n}", 3 * n) for n in range(14, 0, -1))
    darts.extend((f"D{n}", 2 * n) for n in range(20, 0, -1))
    return darts


def _finishing_darts(double_out: bool) -> list[Dart]:
    finals: list[Dart] = [(f"D{n}", 2 * n) for n in _DOUBLE_ORDER]
    finals.append(("Bull", 50))
    if not double_out:
        finals.extend(d for d in _setup_darts() if d not in finals)
    return finals


_SETUP = _setup_darts()
_SETUP_RANK = {label: i for i, (label, _) in enumerate(_SETUP)}


@lru_cache(maxsize=2048)
def suggest_checkout(remaining: int, darts_left: int = 3, double_out: bool = True) -> tuple[str, ...]:
    """Best route out, e.g. (``'T20'``, ``'T20'``, ``'Bull'``), or () when there is none."""
    if remaining <= 0 or remaining > 170 or darts_left <= 0:
        return ()
    finals = _finishing_darts(double_out)
    final_rank = {label: i for i, (label, _) in enumerate(finals)}
    for count in range(1, min(3, darts_left) + 1):
        best: tuple[int, tuple[str, ...]] | None = None
        for final_label, final_score in finals:
            need = remaining - final_score
            for setup in _setups(need, count - 1):
                # A setup must not leave 1, or 0 before the last dart, which _setups ensures.
                cost = 2 * final_rank[final_label] + sum(_SETUP_RANK[s] for s in setup)
                route = (*setup, final_label)
                if best is None or cost < best[0]:
                    best = (cost, route)
        if best is not None:
            return best[1]
    return ()


@lru_cache(maxsize=4096)
def _setups(total: int, count: int) -> tuple[tuple[str, ...], ...]:
    if count == 0:
        return ((),) if total == 0 else ()
    if total <= 0:
        return ()
    found: list[tuple[str, ...]] = []
    for label, score in _SETUP:
        if score > total:
            continue
        for rest in _setups(total - score, count - 1):
            found.append((label, *rest))
    # Keep the search small: only the best few by rank.
    found.sort(key=lambda route: sum(_SETUP_RANK[s] for s in route))
    return tuple(found[:6])
