from __future__ import annotations

import pytest

from custom_components.granboard.checkout import suggest_checkout

VALUE = {"Bull": 50, "25": 25}


def value(label: str) -> int:
    if label in VALUE:
        return VALUE[label]
    return {"S": 1, "D": 2, "T": 3}[label[0]] * int(label[1:])


@pytest.mark.parametrize(
    ("remaining", "route"),
    [(170, ("T20", "T20", "Bull")), (167, ("T20", "T19", "Bull")), (160, ("T20", "T20", "D20")),
     (100, ("T20", "D20")), (50, ("Bull",)), (40, ("D20",)), (32, ("D16",)), (3, ("S1", "D1"))],
)
def test_standard_routes(remaining, route):
    assert suggest_checkout(remaining) == route


@pytest.mark.parametrize("remaining", [169, 168, 166, 165, 163, 162, 159, 171, 1, 0])
def test_no_checkout(remaining):
    assert suggest_checkout(remaining) == ()


def test_every_route_adds_up_and_ends_on_double():
    for remaining in range(2, 171):
        route = suggest_checkout(remaining)
        if route:
            assert sum(value(x) for x in route) == remaining
            assert route[-1].startswith("D") or route[-1] == "Bull"


def test_darts_left_and_single_out():
    assert suggest_checkout(100, 1) == ()
    assert len(suggest_checkout(100, 2)) == 2
    assert suggest_checkout(7, 3, False) == ("S7",)
