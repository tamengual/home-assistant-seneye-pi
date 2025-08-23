"""Config flow for the Seneye integration."""
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_TYPE
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import DOMAIN

BACKEND_TYPES = ["HID", "MQTT"]


class SeneyeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Seneye config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        if user_input is not None:
            # Create a unique title for the entry
            title = f"Seneye ({user_input[CONF_TYPE]})"
            
            # Create the config entry
            return self.async_create_entry(title=title, data=user_input)

        # Show the form to the user
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TYPE, default="HID"): SelectSelector(
                        SelectSelectorConfig(
                            options=BACKEND_TYPES,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

