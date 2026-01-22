import aiohttp
import async_timeout
import logging

from datetime import timedelta
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MojDomekCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, device_id, scan_interval):
        self.device_id = device_id

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device_id}",
            update_interval=timedelta(minutes=scan_interval),
        )

    async def _async_update_data(self):
        params = {
            "id": self.device_id,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(15):
                    async with session.get(BASE_URL, params=params) as response:
                        data = await response.json()

        except Exception as err:
            raise UpdateFailed("Błąd komunikacji z mojdomek.eu") from err

        # 🔴 BŁĄD LOGICZNY API
        if "errorcode" in data:
            if data.get("errorcode") == "745801":
                raise UpdateFailed("Nieprawidłowy identyfikator czujnika")

            raise UpdateFailed(data.get("errormessage", "Błąd API mojdomek.eu"))

        # 🔴 brak spodziewanych danych
        if "locations" not in data:
            raise UpdateFailed("Nieprawidłowa odpowiedź API")

        return data
