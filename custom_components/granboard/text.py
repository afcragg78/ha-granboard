"""Ring Color 2: the LED Ring's second colour as #RRGGBB (empty = the opposite of the light's colour)."""

from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .colors import parse_color
from .coordinator import GranboardConfigEntry
from .entity import GranboardEntity


async def async_setup_entry(hass: HomeAssistant, entry: GranboardConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([GranboardRingColor2(entry.runtime_data, "ring_color_2")])


class GranboardRingColor2(GranboardEntity, TextEntity, RestoreEntity):
    _attr_icon = "mdi:palette-swatch-variant"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min = 0
    _attr_native_max = 7
    _attr_pattern = r"^(#[0-9a-fA-F]{6})?$"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state not in (None, "unknown", "unavailable"):
            color = parse_color(last.state) if last.state else ""
            if color is not None:
                self.coordinator.set_ring_setting("color2", color)

    @property
    def native_value(self) -> str:
        return self.coordinator.ring_settings.get("color2") or ""

    async def async_set_value(self, value: str) -> None:
        value = (value or "").strip()
        color = parse_color(value) if value else ""
        if color is None:
            raise HomeAssistantError(f"Ring Color 2 must be #RRGGBB or empty, got {value!r}")
        self.coordinator.set_ring_setting("color2", color)
        self.async_write_ha_state()
