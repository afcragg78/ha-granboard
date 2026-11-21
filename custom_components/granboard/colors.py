"""Player colours. Pure Python."""

from __future__ import annotations

# Default colour for player 1..8: red, blue, green, yellow, purple, orange, cyan, pink.
PLAYER_PALETTE = ("#ff3b30", "#0a84ff", "#30d158", "#ffd60a", "#bf5af2", "#ff9f0a", "#64d2ff", "#ff375f")

NAMED = {
    "red": "#ff3b30", "blue": "#0a84ff", "green": "#30d158", "yellow": "#ffd60a",
    "purple": "#bf5af2", "orange": "#ff9f0a", "cyan": "#64d2ff", "pink": "#ff375f",
    "white": "#ffffff", "teal": "#40c8e0", "lime": "#a3e635", "gold": "#ffc300",
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
