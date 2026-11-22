"""LED Ring light: use the board's ring like a WLED-style light between games.

Only documented ring commands are used, loop effects write at most four times a
second, and nothing is sent while the board is released or offline. While a
game is playing the light steps aside (state stays on, attribute
paused_for_game is true) and comes back once the game ends and the game
effects have finished. A hit outside a game plays its flash, then the light
comes back.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import effects, led
from .colors import parse_color, to_rgb
from .const import DOMAIN
from .coordinator import GranboardConfigEntry, GranboardCoordinator
from .entity import GranboardEntity

_LOGGER = logging.getLogger(__name__)

# Pause after game / hit effects finish so the flash is seen before the light returns.
RESUME_DELAY_S = 1.5


async def async_setup_entry(hass: HomeAssistant, entry: GranboardConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([GranboardRingLight(entry.runtime_data, "ring")])


class GranboardRingLight(GranboardEntity, LightEntity, RestoreEntity):
    _attr_icon = "mdi:led-strip-variant"
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = list(effects.EFFECTS)

    def __init__(self, coordinator: GranboardCoordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._attr_is_on = False
        self._attr_rgb_color = (255, 255, 255)
        self._attr_brightness = 255
        self._attr_effect = effects.SOLID
        self._task: asyncio.Task[None] | None = None
        self._ring_context: tuple[bool, bool] | None = None
        self._unsub_led: Any = None
        self._unsub_ring: Any = None

    # ------------------------------------------------------------ lifecycle
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None:
            self._attr_is_on = last.state == STATE_ON
            rgb = last.attributes.get(ATTR_RGB_COLOR)
            if isinstance(rgb, (list, tuple)) and len(rgb) == 3:
                self._attr_rgb_color = tuple(int(c) for c in rgb)
            if last.attributes.get(ATTR_BRIGHTNESS) is not None:
                self._attr_brightness = int(last.attributes[ATTR_BRIGHTNESS])
            if last.attributes.get(ATTR_EFFECT) in effects.EFFECTS:
                self._attr_effect = last.attributes[ATTR_EFFECT]
        self._unsub_led = self.coordinator.add_led_listener(self._on_game_led)
        self._unsub_ring = self.coordinator.add_ring_listener(self._on_ring_settings)
        self._ring_context = self._current_context()
        self._restart()

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub_led is not None:
            self._unsub_led()
            self._unsub_led = None
        if self._unsub_ring is not None:
            self._unsub_ring()
            self._unsub_ring = None
        self._cancel()
        await super().async_will_remove_from_hass()

    # ------------------------------------------------------------ state
    @property
    def paused_for_game(self) -> bool:
        return self.coordinator.game_playing

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"paused_for_game": self.paused_for_game, "paused_for_raw_frame": self.coordinator.led_hold}

    def _current_context(self) -> tuple[bool, bool]:
        return self.coordinator.can_write, self.coordinator.game_playing

    def _should_run(self) -> bool:
        return (
            bool(self._attr_is_on)
            and self.coordinator.can_write
            and not self.coordinator.game_playing
            and not self.coordinator.led_hold
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_RGB_COLOR in kwargs:
            self._attr_rgb_color = tuple(int(c) for c in kwargs[ATTR_RGB_COLOR])
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = int(kwargs[ATTR_BRIGHTNESS])
        if kwargs.get(ATTR_EFFECT) in effects.EFFECTS:
            self._attr_effect = kwargs[ATTR_EFFECT]
        self._attr_is_on = True
        self.coordinator.led_hold = False  # taking the light back ends a raw test frame
        self._restart()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        self._cancel()
        if self.coordinator.can_write and not self.coordinator.game_playing:
            self.coordinator.led_play([(led.clear_command(), led.MIN_GAP_MS)], ambient=True)
        self.async_write_ha_state()

    # ------------------------------------------------------------ coordination
    @callback
    def _handle_coordinator_update(self) -> None:
        context = self._current_context()
        if context != self._ring_context:
            # Connected / disconnected, or a game started / ended.
            self._ring_context = context
            self._restart(delay=RESUME_DELAY_S if context[0] else 0)
            if self._attr_is_on and context == (True, True) and not self.coordinator.led_effects:
                # Game lights are off in Configure: do not leave the ambient colour frozen on the ring.
                self.coordinator.led_play([(led.clear_command(), led.MIN_GAP_MS)], ambient=True)
        super()._handle_coordinator_update()

    @callback
    def _on_game_led(self) -> None:
        """A hit, turn, game or service effect was queued: step aside, come back after it."""
        if self._attr_is_on:
            self._restart(delay=RESUME_DELAY_S)
        if self.hass is not None:
            self.async_write_ha_state()  # paused_for_raw_frame may have changed

    @callback
    def _on_ring_settings(self) -> None:
        """Palette, speed, intensity or Color 2 changed: show it now."""
        if self._attr_is_on and self._attr_effect not in effects.SETTINGS_FREE_EFFECTS:
            self._restart()

    def _options(self) -> effects.RingOptions:
        settings = self.coordinator.ring_settings
        color2 = parse_color(settings.get("color2")) if settings.get("color2") else None
        return effects.RingOptions(
            color=tuple(self._attr_rgb_color or (255, 255, 255)),  # type: ignore[arg-type]
            brightness=self._attr_brightness if self._attr_brightness is not None else 255,
            color2=to_rgb(color2) if color2 else None,
            palette=str(settings.get("palette") or "Default"),
            speed=int(settings.get("speed", effects.DEFAULT_SPEED)),
            intensity=int(settings.get("intensity", effects.DEFAULT_INTENSITY)),
        )

    @callback
    def _cancel(self) -> None:
        task, self._task = self._task, None
        if task is not None and not task.done():
            task.cancel()

    @callback
    def _restart(self, delay: float = 0) -> None:
        self._cancel()
        if not self._should_run():
            return
        self._task = self.coordinator.entry.async_create_background_task(
            self.hass, self._run(delay), name=f"{DOMAIN}-{self.coordinator.address}-ring"
        )

    async def _run(self, delay: float) -> None:
        """Apply the light: one write for Solid, a slow loop for the others."""
        effect = self._attr_effect or effects.SOLID
        steps = effects.frames(effect, self._options())
        last: bytes | None = None
        try:
            await self.coordinator.async_led_idle()
            if delay:
                await asyncio.sleep(delay)
            for cmd, wait_ms in steps:
                if not self._should_run():
                    return
                await self.coordinator.async_led_idle()
                if not self._should_run():
                    return
                # A whole-ring colour that has not changed is not re-sent.
                if cmd != last or effect not in effects.HOLD_EFFECTS:
                    self.coordinator.led_play([(cmd, led.MIN_GAP_MS)], ambient=True)
                    last = cmd
                await asyncio.sleep(max(led.AMBIENT_MIN_GAP_MS, wait_ms) / 1000)
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001 - the light must never break hit reading
            _LOGGER.debug("Granboard %s LED Ring effect stopped: %s", self.coordinator.address, err)
