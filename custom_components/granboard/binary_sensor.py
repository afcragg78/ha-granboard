"""Connected binary sensor."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import GranboardConfigEntry
from .entity import GranboardEntity


async def async_setup_entry(hass: HomeAssistant, entry: GranboardConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([GranboardConnected(entry.runtime_data, "connected")])


class GranboardConnected(GranboardEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.connected

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data
        return {"notify_uuid": data.notify_uuid, "write_uuid": data.write_uuid}
