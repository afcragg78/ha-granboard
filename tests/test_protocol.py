from __future__ import annotations

import pytest

from custom_components.granboard.protocol import (
    FRAME_MAP,
    Button,
    FrameBuffer,
    decode_frame,
    parse_segment,
)


def test_map_is_complete_and_unique():
    beds = {(n, r) for n, r in FRAME_MAP.values()}
    assert len(FRAME_MAP) == 83  # 20 x 4 + bull + bullseye + OUT
    assert len(beds) == 83
    for number in range(1, 21):
        for ring in ("single_inner", "treble", "single_outer", "double"):
            assert (number, ring) in beds


@pytest.mark.parametrize(
    ("raw", "segment", "number", "multiplier", "score", "ring"),
    [
        ("3.4@", "T20", 20, 3, 60, "treble"),
        ("3.6@", "D20", 20, 2, 40, "double"),
        ("3.3@", "S20", 20, 1, 20, "single_inner"),
        ("3.5@", "S20", 20, 1, 20, "single_outer"),
        ("2.3@", "S1", 1, 1, 1, "single_inner"),
        ("11.6@", "D16", 16, 2, 32, "double"),
        ("9.0@", "T2", 2, 3, 6, "treble"),
        ("6.0@", "T19", 19, 3, 57, "treble"),
        ("8.0@", "SB", 25, 1, 25, "bull"),
        ("4.0@", "DB", 25, 2, 50, "bullseye"),
        ("OUT@", "MISS", 0, 0, 0, "miss"),
    ],
)
def test_decode(raw, segment, number, multiplier, score, ring):
    hit = decode_frame(raw)
    assert hit.as_dict() == {
        "segment": segment,
        "number": number,
        "multiplier": multiplier,
        "score": score,
        "ring": ring,
        "raw": raw,
    }


def test_button_and_unknown():
    assert isinstance(decode_frame("BTN@"), Button)
    hit = decode_frame("12.9@")
    assert hit.segment == "unknown" and hit.raw == "12.9@" and not hit.known


def test_buffer_split_and_batched():
    buf = FrameBuffer()
    assert buf.feed(b"3.") == []
    assert buf.feed(b"4@8.") == ["3.4@"]
    assert buf.feed(bytes([48, 64]) + b"BTN@\x00") == ["8.0@", "BTN@"]
    assert buf.feed(bytearray(b"2.3@\r\n")) == ["2.3@"]


def test_buffer_drops_garbage_but_recovers():
    buf = FrameBuffer()
    assert buf.feed(b"x" * 100) == []
    assert buf.feed(b"3.4@") == ["3.4@"]


@pytest.mark.parametrize(
    ("text", "segment", "score"),
    [("T20", "T20", 60), ("d16", "D16", 32), ("5", "S5", 5), ("SB", "SB", 25), ("bull", "SB", 25),
     ("50", "DB", 50), ("miss", "MISS", 0)],
)
def test_parse_segment(text, segment, score):
    hit = parse_segment(text)
    assert (hit.segment, hit.score) == (segment, score)


def test_parse_segment_rejects():
    with pytest.raises(ValueError):
        parse_segment("T21")
