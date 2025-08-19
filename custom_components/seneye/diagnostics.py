from __future__ import annotations
from typing import Any
from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_TEMP_OFFSET, CONF_UPDATE_INTERVAL_MIN, CONF_PH_OFFSET, CONF_PAR_SCALE,
)

TO_REDACT = set()

def _serialize_reading(obj: Any) -> dict[str, Any]:
    if obj is None:
        return {}
    data: dict[str, Any] = {}
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            val = getattr(obj, name)
        except Exception:
            continue
        if callable(val):
            continue
        if isinstance(val, (str, int, float, bool)) or val is None:
            data[name] = val
    return data

async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    diag = {
        "options": {
            CONF_UPDATE_INTERVAL_MIN: entry.options.get(CONF_UPDATE_INTERVAL_MIN),
            CONF_TEMP_OFFSET: entry.options.get(CONF_TEMP_OFFSET),
            CONF_PH_OFFSET: entry.options.get(CONF_PH_OFFSET),
            CONF_PAR_SCALE: entry.options.get(CONF_PAR_SCALE),
        },
        "coordinator": {
            "last_update_success": getattr(coordinator, "last_update_success", None),
            "last_success_utc": getattr(coordinator, "last_success_utc", None),
            "temp_offset": getattr(coordinator, "temp_offset", None),
            "ph_offset": getattr(coordinator, "ph_offset", None),
            "par_scale": getattr(coordinator, "par_scale", None),
        },
        "last_reading": _serialize_reading(getattr(coordinator, "data", None)),
    }
    return async_redact_data(diag, TO_REDACT)
