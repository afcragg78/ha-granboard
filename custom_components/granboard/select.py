"""Ring Palette and Sound Theme selects."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import palettes
from .coordinator import GranboardConfigEntry
from .entity import GranboardEntity
from .sounds import THEME_OFF, theme_options


async def async_setup_entry(hass: HomeAssistant, entry: GranboardConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        [
            GranboardRingPalette(coordinator, "ring_palette"),
            GranboardSoundTheme(coordinator, "sound_theme"),
        ]
    )


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


class GranboardSoundTheme(GranboardEntity, SelectEntity, RestoreEntity):
    """Folder-based sound pack, plus Off to use only the Configure file boxes."""

    _attr_icon = "mdi:music-box-multiple"
    _attr_entity_category = EntityCategory.CONFIG

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last is not None and last.state not in (None, "", "unknown", "unavailable"):
            self.coordinator.set_sound_theme(last.state)
        # Discover folders at startup (also happens when options are read and on each play).
        options = await self.hass.async_add_executor_job(self.coordinator.list_sound_themes)
        if self.coordinator.sound_theme not in options:
            # Keep a restored name in the list even if the folder is not there yet.
            pass
        self.async_on_remove(self.coordinator.async_on_sound_theme(self.async_write_ha_state))
        self.async_write_ha_state()

    @property
    def options(self) -> list[str]:
        # Rescan when Home Assistant asks for the options (the dropdown is opened).
        return theme_options(self.coordinator.sounds_root, self.coordinator.sound_theme)

    @property
    def current_option(self) -> str:
        return self.coordinator.sound_theme or THEME_OFF

    async def async_select_option(self, option: str) -> None:
        self.coordinator.set_sound_theme(option or THEME_OFF)
        self.async_write_ha_state()
