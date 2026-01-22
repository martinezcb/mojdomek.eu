import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession # Import sesji HA
from .const import DOMAIN, CONF_DEVICE_ID

_LOGGER = logging.getLogger(__name__)

class MojDomekCoordinator(DataUpdateCoordinator):
    """Zarządzanie pobieraniem danych z obsługą błędów."""

    def __init__(self, hass, device_id, scan_interval):
        self.device_id = device_id
        # Używamy sesji HA zamiast tworzyć nową w każdym zapytaniu
        self.session = async_get_clientsession(hass)
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device_id}",
            update_interval=timedelta(minutes=scan_interval),
        )

    async def _async_update_data(self):
        """Pobierz dane z API."""
        url = f"https://mojdomek.eu/api/api2.php?id={self.device_id}"
        try:
            # Rezygnujemy z 'async with aiohttp.ClientSession()' na rzecz sesji z HA
            async with self.session.get(url, timeout=10) as resp:
                resp.raise_for_status()
                data = await resp.json()
                
                if not data or "locations" not in data:
                    raise UpdateFailed("Otrzymano pustą lub nieprawidłową odpowiedź z serwera.")

                if "errormessage" in data:
                    raise UpdateFailed(f"Błąd API: {data['errormessage']}")
                    
                return data
        except Exception as err:
            raise UpdateFailed(f"Błąd komunikacji z serwerem: {err}")

async def async_setup_entry(hass, entry):
    """Konfiguracja integracji."""
    device_id = entry.data[CONF_DEVICE_ID]
    # Pobieramy interwał najpierw z opcji, potem z danych startowych
    scan_interval = entry.options.get("scan_interval", entry.data.get("scan_interval", 15))

    coordinator = MojDomekCoordinator(hass, device_id, scan_interval)
    
    # Inicjalizacja danych, jeśli to pierwszy czujnik
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Rejestracja listenera zmian opcji
    entry.async_on_unload(entry.add_update_listener(update_listener))

    # Pierwsze pobranie danych
    await coordinator.async_config_entry_first_refresh()
    
    # Uruchomienie platformy sensorów
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    return True

async def update_listener(hass, entry):
    """Obsługa zmian w ustawieniach"""
    # To wymusi przeładowanie całej integracji przy zmianie interwału
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    """Usunięcie integracji."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
