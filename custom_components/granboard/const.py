"""Constants for the Granboard integration."""

from __future__ import annotations

from .protocol import BOARD_NAME, NOTIFY_UUID, SERVICE_UUID, WRITE_UUID  # noqa: F401

DOMAIN = "granboard"
MANUFACTURER = "Granboard"
MODEL = "Granboard 3"

EVENT_HIT = "granboard_hit"
EVENT_BUTTON = "granboard_button"
EVENT_AWARD = "granboard_award"
EVENT_TURN = "granboard_turn"

CONF_CONNECT = "connect"
CONF_BUTTON_NEXT = "button_next_player"
DEFAULT_BUTTON_NEXT = True
CONF_AUTO_NEXT = "auto_next_player"
DEFAULT_AUTO_NEXT = True
CONF_DEBOUNCE_MS = "debounce_ms"
DEFAULT_DEBOUNCE_MS = 250
CONF_LED_FX = "led_effects"
DEFAULT_LED_FX = True

STORAGE_VERSION = 1

CONF_SOUND_PLAYER = "sound_player"
CONF_SOUNDS = "sounds"
CONF_SOUND_VOLUMES = "sound_volumes"
EVENT_SOUND = "granboard_sound"
