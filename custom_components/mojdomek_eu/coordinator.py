import logging
from datetime import timedelta, datetime
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN, 
    BASE_URL, 
    CONF_DEVICE_ID, 
    CONF_SCAN_INTERVAL, 
    DEFAULT_SCAN_INTERVAL_MIN,
    CONF_MAX_AGE,
    DEFAULT_MAX_AGE
)

_LOGGER = logging.getLogger(__name__)

class MojDomekCoordinator(DataUpdateCoordinator):
    """Koordynator pobierania danych z mojdomek.eu z miękkim Watchdogiem."""

    def __init__(self, hass, session, entry):
        self.device_id = entry.data[CONF_DEVICE_ID]
        self.session = session
        self.config_entry = entry
        self.data_is_valid = True  # Nasza flaga świeżości danych

        scan_interval = entry.options.get(
            CONF_SCAN_INTERVAL, 
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MIN)
        )
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=max(scan_interval, 1)),
        )

    async def _async_update_data(self):
        """Pobranie danych i sprawdzenie ich wieku"""
        max_age_hours = self.config_entry.options.get(
            CONF_MAX_AGE, 
            self.config_entry.data.get(CONF_MAX_AGE, DEFAULT_MAX_AGE)
        )

        url = f"{BASE_URL}?id={self.device_id}"
        
        # 1. Próba pobrania danych
        try:
            async with self.session.get(url, timeout=15) as response:
                response.raise_for_status()
                data = await response.json()
        except Exception as err:
            raise UpdateFailed(f"Błąd połączenia z API: {err}")

        # 2. Walidacja struktury
        if not data or "locations" not in data or not data["locations"]:
            raise UpdateFailed("API zwróciło pustą odpowiedź.")

        location = data["locations"][0]
        measurement = location.get("measurement", {})
        api_time_str = measurement.get("datatime")

        # 3. Miękki Watchdog (0 -wyłączony)
        if max_age_hours == 0:
            self.data_is_valid = True
            _LOGGER.debug("Sprawdzanie wieku danych dla %s jest wyłączone (limit = 0)", self.device_id)
        elif api_time_str:
            try:
                api_dt = datetime.strptime(api_time_str, "%Y-%m-%d %H:%M:%S")
                diff_hours = (datetime.now() - api_dt).total_seconds() / 3600

                if diff_hours > max_age_hours:
                    _LOGGER.warning(
                        "Dane dla %s są nieaktualne (wiek: %.2f h, limit: %s h)", 
                        self.device_id, diff_hours, max_age_hours
                    )
                    self.data_is_valid = False
                else:
                    self.data_is_valid = True
                
            except (ValueError, TypeError):
                # W przypadku błędu formatu daty, uznajemy dane za ważne, by nie blokować sensora
                self.data_is_valid = True
        else:
            # Jeśli w ogóle nie ma daty w API, uznajemy dane za ważne
            self.data_is_valid = True

        return data
