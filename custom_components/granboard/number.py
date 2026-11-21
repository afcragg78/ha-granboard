"""Ring Speed and Ring Intensity for the LED Ring light's effects (0-255, like WLED)."""

from __future__ import annotations

from homeassistant.components.number import NumberMode, RestoreNumber
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import GranboardConfigEntry, GranboardCoordinator
from .effects import DEFAULT_INTENSITY, DEFAULT_SPEED
from .entity import GranboardEntity


async def async_setup_entry(hass: HomeAssistant, entry: GranboardConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        [
            GranboardRingNumber(coordinator, "ring_speed", "speed", "mdi:speedometer"),
            GranboardRingNumber(coordinator, "ring_intensity", "intensity", "mdi:tune-variant"),
        ]
    )


class GranboardRingNumber(GranboardEntity, RestoreNumber):
    """Speed scales effect timing (never faster than one write per 250 ms); intensity sets depth / density."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 255
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: GranboardCoordinator, key: str, setting: str, icon: str) -> None:
        super().__init__(coordinator, key)
        self._setting = setting
        self._attr_icon = icon

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_number_data()
        if last is not None and last.native_value is not None:
            self.coordinator.set_ring_setting(self._setting, int(max(0, min(255, last.native_value))))

    @property
    def native_value(self) -> float:
        default = DEFAULT_SPEED if self._setting == "speed" else DEFAULT_INTENSITY
        return float(self.coordinator.ring_settings.get(self._setting, default))

    async def async_set_native_value(self, value: float) -> None:
        self.coordinator.set_ring_setting(self._setting, int(max(0, min(255, round(value)))))
        self.async_write_ha_state()
