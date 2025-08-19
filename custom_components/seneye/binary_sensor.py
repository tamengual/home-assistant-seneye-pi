from __future__ import annotations
import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from . import SeneyeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SeneyeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = [
        SeneyeInWaterBinarySensor(coordinator, entry.entry_id),
        SeneyeSlideProblemBinarySensor(coordinator, entry.entry_id),
    ]
    async_add_entities(entities)

class _BaseSeneyeBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    def __init__(self, coordinator: SeneyeDataUpdateCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id

    @property
    def device_info(self) -> DeviceInfo | None:
        serial = getattr(self.coordinator.data, "serial", None) or getattr(self.coordinator.data, "serial_number", None)
        identifiers = {(DOMAIN, serial)} if serial else {(DOMAIN, "seneye_usb")}
        return DeviceInfo(identifiers=identifiers, manufacturer="Seneye", name="Seneye USB", model=getattr(self.coordinator.data, "model", None) or "Unknown")

    @property
    def available(self) -> bool:
        return bool(self.coordinator.last_update_success)

class SeneyeInWaterBinarySensor(_BaseSeneyeBinarySensor):
    _attr_name = "Seneye In Water"
    device_class = BinarySensorDeviceClass.MOISTURE
    def __init__(self, coordinator: SeneyeDataUpdateCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        serial = getattr(coordinator.data, "serial", None) or getattr(coordinator.data, "serial_number", None)
        self._attr_unique_id = f"{serial}_in_water" if serial else f"{entry_id}_in_water"
    @property
    def is_on(self) -> bool | None:
        d = self.coordinator.data
        return bool(getattr(d, "in_water", False)) if d is not None else None

class SeneyeSlideProblemBinarySensor(_BaseSeneyeBinarySensor):
    _attr_name = "Seneye Slide Problem"
    device_class = BinarySensorDeviceClass.PROBLEM
    def __init__(self, coordinator: SeneyeDataUpdateCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        serial = getattr(coordinator.data, "serial", None) or getattr(coordinator.data, "serial_number", None)
        self._attr_unique_id = f"{serial}_slide_problem" if serial else f"{entry_id}_slide_problem"
    @property
    def is_on(self) -> bool | None:
        d = self.coordinator.data
        expired = getattr(d, "slide_expired", None) if d is not None else None
        if expired is None:
            return None
        return bool(expired)
