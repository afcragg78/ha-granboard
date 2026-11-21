"""Ring Palette: WLED-style palette for the LED Ring light's effects."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import palettes
from .coordinator import GranboardConfigEntry
from .entity import GranboardEntity


async def async_setup_entry(hass: HomeAssistant, entry: GranboardConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([GranboardRingPalette(entry.runtime_data, "ring_palette")])


class GranboardRingPalette(GranboardEntity, SelectEntity, RestoreEntity):
    _attr_icon = "mdi:palette"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = list(palettes.PALETTES)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state in palettes.PALETTES:
            self.coordinator.set_ring_setting("palette", last.state)

    @property
    def current_option(self) -> str:
        return self.coordinator.ring_settings.get("palette") or palettes.DEFAULT

    async def async_select_option(self, option: str) -> None:
        self.coordinator.set_ring_setting("palette", option)
        self.async_write_ha_state()
