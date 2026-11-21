"""Player colours. Pure Python."""

from __future__ import annotations

# Default colour for player 1..8: red, blue, green, yellow, purple, orange, cyan, pink.
PLAYER_PALETTE = ("#ff0000", "#0000ff", "#00ff00", "#ffff00", "#8000ff", "#ff6000", "#00ffff", "#ff0080")

NAMED = {
    "red": "#ff0000", "blue": "#0000ff", "green": "#00ff00", "yellow": "#ffff00",
    "purple": "#8000ff", "orange": "#ff6000", "cyan": "#00ffff", "pink": "#ff0080",
    "white": "#ffffff", "teal": "#00ffc0", "lime": "#80ff00", "gold": "#ffb000",
}


def parse_color(value: object) -> str | None:
    """'#RRGGBB', 'RRGGBB', '#RGB', a colour name, or [r, g, b] -> '#rrggbb'. None if unusable."""
    if isinstance(value, (list, tuple)) and len(value) == 3:
        try:
            r, g, b = (max(0, min(255, int(c))) for c in value)
        except (TypeError, ValueError):
            return None
        return f"#{r:02x}{g:02x}{b:02x}"
    text = str(value or "").strip().lower()
    if text in NAMED:
        return NAMED[text]
    text = text.lstrip("#")
    if len(text) == 3:
        text = "".join(c * 2 for c in text)
    if len(text) == 6 and all(c in "0123456789abcdef" for c in text):
        return "#" + text
    return None


def player_color(index: int, given: object = None) -> str:
    return parse_color(given) or PLAYER_PALETTE[index % len(PLAYER_PALETTE)]


def to_rgb(color: str) -> tuple[int, int, int]:
    c = parse_color(color) or "#ffffff"
    return int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
