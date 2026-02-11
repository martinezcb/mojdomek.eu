import voluptuous as vol
from homeassistant import config_entries
from .const import (
    DOMAIN, 
    CONF_DEVICE_ID, 
    CONF_SCAN_INTERVAL, 
    DEFAULT_SCAN_INTERVAL_MIN,
    CONF_MAX_AGE,
    DEFAULT_MAX_AGE
)

class MojDomekConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Obsługa instalacji przez UI"""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=f"mojdomek {user_input[CONF_DEVICE_ID]}", 
                data=user_input
            )

        # Używamy vol.Coerce, aby HA wiedział, jak konwertować dane z formularza
        data_schema = vol.Schema({
            vol.Required(CONF_DEVICE_ID): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL_MIN): vol.Coerce(int),
            vol.Optional(CONF_MAX_AGE, default=DEFAULT_MAX_AGE): vol.Coerce(float),
        })

        return self.async_show_form(step_id="user", data_schema=data_schema)

    @staticmethod
    def async_get_options_flow(config_entry):
        return MojDomekOptionsFlowHandler(config_entry)

class MojDomekOptionsFlowHandler(config_entries.OptionsFlow):
    """Obsługa przycisku KONFIGURUJ"""
    def __init__(self, config_entry):
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self._entry.options.get(
            CONF_SCAN_INTERVAL, 
            self._entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MIN)
        )
        current_max_age = self._entry.options.get(
            CONF_MAX_AGE, 
            self._entry.data.get(CONF_MAX_AGE, DEFAULT_MAX_AGE)
        )

        # Tutaj również vol.Coerce(float) dla max_age
        options_schema = vol.Schema({
            vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): vol.Coerce(int),
            vol.Optional(CONF_MAX_AGE, default=current_max_age): vol.Coerce(float),
        })

        return self.async_show_form(step_id="init", data_schema=options_schema)
