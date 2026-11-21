"""Constants for the Granboard integration."""

from __future__ import annotations

from .protocol import BOARD_NAME, NOTIFY_UUID, SERVICE_UUID, WRITE_UUID  # noqa: F401

DOMAIN = "granboard"
MANUFACTURER = "Granboard"
MODEL = "Granboard 3"

EVENT_HIT = "granboard_hit"
EVENT_BUTTON = "granboard_button"
EVENT_AWARD = "granboard_award"

CONF_CONNECT = "connect"
CONF_BUTTON_NEXT = "button_next_player"
DEFAULT_BUTTON_NEXT = True

STORAGE_VERSION = 1
