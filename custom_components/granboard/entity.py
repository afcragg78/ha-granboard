"""Shared device info for Granboard entities."""

from __future__ import annotations

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import GranboardCoordinator


class GranboardEntity(CoordinatorEntity[GranboardCoordinator]):
    """Always available; connection is its own entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: GranboardCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_translation_key = key
        self._attr_unique_id = f"{coordinator.address}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
            connections={(dr.CONNECTION_BLUETOOTH, coordinator.address)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=coordinator.entry.title,
        )

    @property
    def available(self) -> bool:
        return True
