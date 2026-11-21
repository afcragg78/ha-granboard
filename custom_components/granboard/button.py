"""Release Board button: turns the Granboard Connection switch off."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import GranboardConfigEntry
from .entity import GranboardEntity


async def async_setup_entry(hass: HomeAssistant, entry: GranboardConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([ReleaseBoardButton(entry.runtime_data, "release")])


class ReleaseBoardButton(GranboardEntity, ButtonEntity):
    _attr_icon = "mdi:bluetooth-off"

    async def async_press(self) -> None:
        await self.coordinator.async_set_enabled(False)
