from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Any, Callable
from datetime import datetime

from homeassistant.components.sensor import (
    SensorEntity, SensorEntityDescription, SensorStateClass, SensorDeviceClass,
)
from homeassistant.const import UnitOfTemperature, CONCENTRATION_PARTS_PER_MILLION, LIGHT_LUX
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from . import SeneyeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass
class SeneyeSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[Any], Any] | None = None
    transform_fn: Callable[[Any, SeneyeDataUpdateCoordinator], Any] | None = None

SENSORS: tuple[SeneyeSensorEntityDescription, ...] = (
    SeneyeSensorEntityDescription(
        key="temperature", name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: getattr(d, "temperature", None),
        transform_fn=lambda v, c: (float(v) + float(getattr(c, "temp_offset", 0.0))) if isinstance(v, (int, float)) else v,
    ),
    SeneyeSensorEntityDescription(
        key="ph", name="pH", native_unit_of_measurement="pH",
        icon="mdi:ph", state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: getattr(d, "ph", None),
        transform_fn=lambda v, c: (float(v) + float(getattr(c, "ph_offset", 0.0))) if isinstance(v, (int, float)) else v,
    ),
    SeneyeSensorEntityDescription(
        key="nh3", name="NH3", native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        icon="mdi:molecule", state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: getattr(d, "nh3", None),
    ),
    SeneyeSensorEntityDescription(
        key="par", name="PAR", native_unit_of_measurement="μmol/m²/s",
        icon="mdi:solar-power", state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: getattr(d, "par", None),
        transform_fn=lambda v, c: (float(v) * float(getattr(c, "par_scale", 1.0))) if isinstance(v, (int, float)) else v,
    ),
    SeneyeSensorEntityDescription(
        key="pur", name="PUR", native_unit_of_measurement="%",
        icon="mdi:theme-light-dark", state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: getattr(d, "pur", None),
    ),
    SeneyeSensorEntityDescription(
        key="lux", name="LUX", native_unit_of_measurement=LIGHT_LUX,
        device_class=SensorDeviceClass.ILLUMINANCE, state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: getattr(d, "lux", None),
    ),
    SeneyeSensorEntityDescription(
        key="kelvin", name="Kelvin", native_unit_of_measurement="K",
        icon="mdi:temperature-kelvin", state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: getattr(d, "kelvin", None),
    ),
    SeneyeSensorEntityDescription(
        key="last_update", name="Last Successful Update",
        device_class=SensorDeviceClass.TIMESTAMP, value_fn=lambda d: None,
    ),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SeneyeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [SeneyeSensor(coordinator, desc, entry.entry_id) for desc in SENSORS]
    async_add_entities(entities)

class SeneyeSensor(CoordinatorEntity, SensorEntity):
    entity_description: SeneyeSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator: SeneyeDataUpdateCoordinator, description: SeneyeSensorEntityDescription, entry_id: str) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry_id = entry_id
        serial = getattr(coordinator.data, "serial", None) or getattr(coordinator.data, "serial_number", None)
        self._attr_unique_id = f"{serial}_{description.key}" if serial else f"{entry_id}_{description.key}"
        self._attr_name = f"Seneye {description.name}"

    @property
    def device_info(self) -> DeviceInfo | None:
        serial = getattr(self.coordinator.data, "serial", None) or getattr(self.coordinator.data, "serial_number", None)
        identifiers = {(DOMAIN, serial)} if serial else {(DOMAIN, "seneye_usb")}
        return DeviceInfo(identifiers=identifiers, manufacturer="Seneye", name="Seneye USB", model=getattr(self.coordinator.data, "model", None) or "Unknown")

    @property
    def available(self) -> bool:
        return bool(self.coordinator.last_update_success)

    @property
    def native_value(self):
        if self.entity_description.key == "last_update":
            ts = getattr(self.coordinator, "last_success_utc", None)
            return ts if isinstance(ts, datetime) else None
        if self.coordinator.data:
            try:
                raw = self.entity_description.value_fn(self.coordinator.data) if self.entity_description.value_fn else None
                if self.entity_description.transform_fn:
                    return self.entity_description.transform_fn(raw, self.coordinator)
                return raw
            except Exception as exc:
                _LOGGER.debug("Value failed for %s: %s", self.entity_description.key, exc)
                return None
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        d = self.coordinator.data
        if not d:
            return None
        attrs: dict[str, Any] = {}
        for k in ("in_water", "slide_expired"):
            if hasattr(d, k):
                attrs[k] = getattr(d, k)
        return attrs or None
