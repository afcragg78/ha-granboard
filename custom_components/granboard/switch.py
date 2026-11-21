"""Granboard Connection kill switch.

Off disconnects at once and holds no connection until it is turned back on,
so the official phone app can connect. The state lives in the config entry
options, so it is restored after a Home Assistant restart before any
connection attempt is made.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import GranboardConfigEntry
from .entity import GranboardEntity


async def async_setup_entry(hass: HomeAssistant, entry: GranboardConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([GranboardConnectSwitch(entry.runtime_data, "connect")])


class GranboardConnectSwitch(GranboardEntity, SwitchEntity):
    _attr_icon = "mdi:bluetooth-connect"

    @property
    def is_on(self) -> bool:
        return self.coordinator.enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_enabled(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_enabled(False)
