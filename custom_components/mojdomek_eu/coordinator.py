import logging
from datetime import timedelta, datetime
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

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
    """Koordynator z poprawnym harmonogramem i mechanizmem ukrywania danych."""

    def __init__(self, hass, session, entry):
        self.device_id = entry.data[CONF_DEVICE_ID]
        self.session = session
        self.config_entry = entry
        self.data_is_valid = True  

        # Pobieramy interwał
        scan_val = entry.options.get(
            CONF_SCAN_INTERVAL, 
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MIN)
        )
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=max(int(scan_val), 1)),
        )

    async def _async_update_data(self):
        """Pobranie danych i weryfikacja świeżości."""
        try:
            raw_max_age = self.config_entry.options.get(
                CONF_MAX_AGE, 
                self.config_entry.data.get(CONF_MAX_AGE, DEFAULT_MAX_AGE)
            )
            max_age_hours = float(raw_max_age)
        except (TypeError, ValueError):
            max_age_hours = float(DEFAULT_MAX_AGE)

        url = f"{BASE_URL}?id={self.device_id}"
        
        # 1. Próba pobrania danych
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    _LOGGER.warning("Serwer mojdomek.eu zwrócił status %s. Używam starych danych.", response.status)
                    return self.data if self.data else {}
                
                data = await response.json()
        except Exception as err:
            _LOGGER.error("Błąd połączenia z API: %s. Kolejna próba za %s min.", err, self.update_interval)
            if self.data:
                return self.data
            raise UpdateFailed(f"Błąd komunikacji: {err}")

        # 2. Walidacja struktury
        if not data or "locations" not in data or not data["locations"]:
            _LOGGER.warning("API zwróciło pustą odpowiedź. Harmonogram trwa dalej.")
            return self.data if self.data else {}

        location = data["locations"][0]
        measurement = location.get("measurement", {})
        api_time_str = measurement.get("datatime")

        # 3. Mechanizm Watchdoga (ukrywanie sensorów)
        if max_age_hours <= 0:
            self.data_is_valid = True
        elif api_time_str:
            try:
                api_dt_naive = datetime.strptime(api_time_str, "%Y-%m-%d %H:%M:%S")
                api_dt = dt_util.as_local(api_dt_naive)
                
                now = dt_util.now()
                diff_hours = (now - api_dt).total_seconds() / 3600

                if diff_hours > max_age_hours:
                    _LOGGER.warning(
                        "Dane dla %s są nieaktualne (wiek: %.2f h, limit: %.2f h). Sensory zostaną wyłączone.", 
                        self.device_id, diff_hours, max_age_hours
                    )
                    self.data_is_valid = False 
                else:
                    self.data_is_valid = True
                
            except (ValueError, TypeError):
                self.data_is_valid = True
        else:
            self.data_is_valid = True

        return data
