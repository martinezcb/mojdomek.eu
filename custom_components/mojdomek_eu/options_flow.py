import voluptuous as vol
from homeassistant import config_entries

class MojDomekOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        scan_interval = self.config_entry.options.get("scan_interval", 15)
        data_schema = vol.Schema({
            vol.Required("scan_interval", default=scan_interval): int,
        })

        return self.async_show_form(step_id="init", data_schema=data_schema)
