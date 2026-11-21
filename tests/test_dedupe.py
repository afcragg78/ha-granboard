from __future__ import annotations

from custom_components.granboard.reconnect import DEBOUNCE_MS, DuplicateFilter


class Clock:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t


def test_default_window_is_500ms():
    assert DEBOUNCE_MS == 500


def test_bounce_burst_counts_once():
    clock = Clock()
    f = DuplicateFilter(clock=clock)
    # T20 seen at :16.681, .828, .901 on real hardware
    assert f.accept("3.4@")
    clock.t += 0.147
    assert not f.accept("3.4@")
    clock.t += 0.073
    assert not f.accept("3.4@")


def test_window_measured_from_last_accepted_frame():
    clock = Clock()
    f = DuplicateFilter(clock=clock)
    assert f.accept("3.6@")
    clock.t += 0.4
    assert not f.accept("3.6@")
    clock.t += 0.2  # 600 ms after the accepted one
    assert f.accept("3.6@")


def test_different_frame_passes_immediately():
    clock = Clock()
    f = DuplicateFilter(clock=clock)
    assert f.accept("3.4@")
    clock.t += 0.01
    assert f.accept("3.6@")
    clock.t += 0.01
    assert f.accept("3.4@")


def test_zero_window_disables():
    clock = Clock()
    f = DuplicateFilter(0, clock=clock)
    assert f.accept("4.0@")
    assert f.accept("4.0@")


def test_reset_forgets_last_frame():
    clock = Clock()
    f = DuplicateFilter(clock=clock)
    assert f.accept("4.0@")
    f.reset()
    assert f.accept("4.0@")


def test_window_can_change_live():
    clock = Clock()
    f = DuplicateFilter(clock=clock)
    assert f.accept("8.0@")
    clock.t += 0.3
    f.set_window_ms(200)
    assert f.accept("8.0@")
