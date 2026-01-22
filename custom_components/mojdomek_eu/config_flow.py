import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_DEVICE_ID

async def validate_input(device_id):
    """Sprawdza, czy ID czujnika jest poprawne na serwerze mojdomek.eu"""
    url = f"https://mojdomek.eu/api/api2.php?id={device_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return "cannot_connect"
                data = await resp.json()
                if "errormessage" in data:
                    return "invalid_id"
        return None
    except Exception:
        return "cannot_connect"

class MojDomekConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Obsługa konfiguracji i walidacji"""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Sprawdzamy ID zanim utworzymy wpis
            error = await validate_input(user_input[CONF_DEVICE_ID])
            if not error:
                return self.async_create_entry(
                    title=f"Czujnik {user_input[CONF_DEVICE_ID]}", 
                    data=user_input
                )
            errors["base"] = error

        data_schema = vol.Schema({
            vol.Required(CONF_DEVICE_ID): str,
            vol.Required("scan_interval", default=15): int,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Uruchamia okno opcji"""
        return MojDomekOptionsFlowHandler()

class MojDomekOptionsFlowHandler(config_entries.OptionsFlow):
    """Obsługa zmiany opcji (interwału)"""
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            "scan_interval", 
            self.config_entry.data.get("scan_interval", 15)
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("scan_interval", default=current_interval): int,
            }),
        )
