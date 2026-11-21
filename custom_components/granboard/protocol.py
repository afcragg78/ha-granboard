"""Granboard BLE frames: buffering, decoding, and segment names.

Pure Python. No Home Assistant imports, so the tests run without it.

The board sends 4-5 ASCII bytes per event ending in ``@``, for example
``3.4@`` (treble 20). ``BTN@`` is the board button and ``OUT@`` a miss.
Frames can arrive split across notifications or several in one, so
:class:`FrameBuffer` collects bytes until each ``@``.

Frame map from keenanlk/granboard-ble-codes (byte table, read as digits),
cross-checked against HomeDarts / gran-app. It has not yet been verified
against Andrew's board; unknown frames are reported, not dropped.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re

SERVICE_UUID = "442f1570-8a00-9a28-cbe1-e1d4212d53eb"
NOTIFY_UUID = "442f1571-8a00-9a28-cbe1-e1d4212d53eb"
WRITE_UUID = "442f1572-8a00-9a28-cbe1-e1d4212d53eb"
BOARD_NAME = "GRANBOARD"

TERMINATOR = "@"
BUTTON_FRAME = "BTN"
MISS_FRAME = "OUT"
MAX_FRAME_LEN = 16

RING_INNER = "single_inner"
RING_TREBLE = "treble"
RING_OUTER = "single_outer"
RING_DOUBLE = "double"
RING_BULL = "bull"
RING_BULLSEYE = "bullseye"
RING_MISS = "miss"
RING_UNKNOWN = "unknown"

RING_MULTIPLIER = {
    RING_INNER: 1,
    RING_TREBLE: 3,
    RING_OUTER: 1,
    RING_DOUBLE: 2,
    RING_BULL: 1,
    RING_BULLSEYE: 2,
    RING_MISS: 0,
}

# number: (inner single, treble, outer single, double)
_BEDS: dict[int, tuple[str, str, str, str]] = {
    1: ("2.3", "2.4", "2.5", "2.6"),
    2: ("9.1", "9.0", "9.2", "8.2"),
    3: ("7.1", "7.0", "7.2", "8.4"),
    4: ("0.1", "0.3", "0.5", "0.6"),
    5: ("5.1", "5.2", "5.4", "4.6"),
    6: ("1.0", "1.1", "1.3", "4.4"),
    7: ("11.1", "11.2", "11.4", "8.6"),
    8: ("6.2", "6.4", "6.5", "6.6"),
    9: ("9.3", "9.4", "9.5", "9.6"),
    10: ("2.0", "2.1", "2.2", "4.3"),
    11: ("7.3", "7.4", "7.5", "7.6"),
    12: ("5.0", "5.3", "5.5", "5.6"),
    13: ("0.0", "0.2", "0.4", "4.5"),
    14: ("10.3", "10.4", "10.5", "10.6"),
    15: ("3.0", "3.1", "3.2", "4.2"),
    16: ("11.0", "11.3", "11.5", "11.6"),
    17: ("10.1", "10.0", "10.2", "8.3"),
    18: ("1.2", "1.4", "1.5", "1.6"),
    19: ("6.1", "6.0", "6.3", "8.5"),
    20: ("3.3", "3.4", "3.5", "3.6"),
}

FRAME_MAP: dict[str, tuple[int, str]] = {}
for _number, _codes in _BEDS.items():
    for _code, _ring in zip(_codes, (RING_INNER, RING_TREBLE, RING_OUTER, RING_DOUBLE)):
        FRAME_MAP[_code] = (_number, _ring)
FRAME_MAP["8.0"] = (25, RING_BULL)
FRAME_MAP["4.0"] = (25, RING_BULLSEYE)
FRAME_MAP[MISS_FRAME] = (0, RING_MISS)


@dataclass(frozen=True)
class Hit:
    """One dart, as fired in the ``granboard_hit`` event."""

    segment: str
    number: int
    multiplier: int
    score: int
    ring: str
    raw: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    @property
    def is_bull(self) -> bool:
        return self.number == 25

    @property
    def known(self) -> bool:
        return self.ring != RING_UNKNOWN


@dataclass(frozen=True)
class Button:
    """The board's physical button."""

    raw: str


def segment_name(number: int, multiplier: int) -> str:
    """S20 / D20 / T20, SB (25) / DB (50), MISS."""
    if number <= 0 or multiplier <= 0:
        return "MISS"
    if number == 25:
        return "DB" if multiplier == 2 else "SB"
    return {1: "S", 2: "D", 3: "T"}[multiplier] + str(number)


def make_hit(number: int, ring: str, raw: str = "") -> Hit:
    """Build a hit from a number and a ring."""
    multiplier = RING_MULTIPLIER[ring]
    if ring == RING_MISS:
        number = 0
    return Hit(
        segment=segment_name(number, multiplier),
        number=number,
        multiplier=multiplier,
        score=number * multiplier,
        ring=ring,
        raw=raw,
    )


def unknown_hit(raw: str) -> Hit:
    return Hit(segment="unknown", number=0, multiplier=0, score=0, ring=RING_UNKNOWN, raw=raw)


def decode_frame(frame: str) -> Hit | Button:
    """Decode one complete frame (with or without the trailing ``@``)."""
    raw = frame if frame.endswith(TERMINATOR) else frame + TERMINATOR
    body = frame.strip().rstrip(TERMINATOR).strip()
    if body.upper() == BUTTON_FRAME:
        return Button(raw=raw)
    if body.upper() == MISS_FRAME:
        return make_hit(0, RING_MISS, raw)
    entry = FRAME_MAP.get(body)
    if entry is None:
        # Right after connecting, the board can glue its banner (e.g. "GB7;101")
        # onto the first hit. Keep the hit by matching the frame at the end.
        for i in range(1, len(body)):
            tail = body[i:]
            if tail.upper() == BUTTON_FRAME:
                return Button(raw=raw)
            if tail in FRAME_MAP:
                entry = FRAME_MAP[tail]
                break
        else:
            return unknown_hit(raw)
    return make_hit(entry[0], entry[1], raw)


class FrameBuffer:
    """Collect notification bytes and yield complete ``...@`` frames."""

    def __init__(self) -> None:
        self._pending = ""

    def clear(self) -> None:
        self._pending = ""

    def feed(self, data: bytes | bytearray | str) -> list[str]:
        if isinstance(data, (bytes, bytearray)):
            text = bytes(data).decode("ascii", errors="replace")
        else:
            text = data
        # Some firmwares pad with NUL or line breaks.
        text = text.replace("\x00", "").replace("\r", "").replace("\n", "")
        self._pending += text
        frames: list[str] = []
        while TERMINATOR in self._pending:
            frame, self._pending = self._pending.split(TERMINATOR, 1)
            frame = frame.strip()
            if frame:
                frames.append(frame + TERMINATOR)
        if len(self._pending) > MAX_FRAME_LEN:
            # Real frames are a few bytes; drop runaway garbage so the next frame decodes.
            self._pending = ""
        return frames


_SEGMENT_RE = re.compile(r"^(?P<prefix>[SDTIO]?)(?P<number>\d{1,2})$")


def parse_segment(text: str) -> Hit:
    """Turn 'T20', 'D16', 'S5', '20', 'SB'/'25'/'BULL', 'DB'/'50'/'BULLSEYE', 'MISS' into a hit.

    Used by the ``granboard.throw`` service to play without the board.
    Plain singles are reported as the outer single.
    """
    value = str(text).strip().upper().replace(" ", "")
    if value in ("MISS", "OUT", "M", "0", "S0"):
        return make_hit(0, RING_MISS, "manual")
    if value in ("SB", "25", "BULL", "S25", "OB", "OUTERBULL"):
        return make_hit(25, RING_BULL, "manual")
    if value in ("DB", "50", "BULLSEYE", "D25", "IB", "INNERBULL"):
        return make_hit(25, RING_BULLSEYE, "manual")
    match = _SEGMENT_RE.match(value)
    if match:
        number = int(match.group("number"))
        prefix = match.group("prefix") or "S"
        if 1 <= number <= 20:
            ring = {"S": RING_OUTER, "O": RING_OUTER, "I": RING_INNER, "D": RING_DOUBLE, "T": RING_TREBLE}[prefix]
            return make_hit(number, ring, "manual")
    raise ValueError(f"Not a dartboard segment: {text!r}")
