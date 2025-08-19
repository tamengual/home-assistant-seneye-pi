from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_UPDATE_INTERVAL_MIN, CONF_TEMP_OFFSET, CONF_PH_OFFSET, CONF_PAR_SCALE,
    DEFAULT_UPDATE_INTERVAL_MIN, DEFAULT_TEMP_OFFSET, DEFAULT_PH_OFFSET, DEFAULT_PAR_SCALE,
)

class SeneyeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is None:
            return self.async_show_form(step_id="user")
        return self.async_create_entry(title="Seneye USB Monitor", data={})

    @staticmethod
    @callback
    def async_get_options_flow(entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return SeneyeOptionsFlowHandler(entry)

class SeneyeOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.entry.options
        schema = vol.Schema({
            vol.Optional(CONF_UPDATE_INTERVAL_MIN, default=current.get(CONF_UPDATE_INTERVAL_MIN, DEFAULT_UPDATE_INTERVAL_MIN)): vol.All(int, vol.Range(min=1, max=60)),
            vol.Optional(CONF_TEMP_OFFSET, default=current.get(CONF_TEMP_OFFSET, DEFAULT_TEMP_OFFSET)): vol.Coerce(float),
            vol.Optional(CONF_PH_OFFSET, default=current.get(CONF_PH_OFFSET, DEFAULT_PH_OFFSET)): vol.Coerce(float),
            vol.Optional(CONF_PAR_SCALE, default=current.get(CONF_PAR_SCALE, DEFAULT_PAR_SCALE)): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=5.0)),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
