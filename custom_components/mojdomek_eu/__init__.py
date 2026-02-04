import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .coordinator import MojDomekCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Konfiguracja integracji"""
    session = async_get_clientsession(hass)
    coordinator = MojDomekCoordinator(hass, session, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.debug("Wstępne odświeżenie zgłosiło błąd: %s", err)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    
    # Rejestracja platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Funkcja obsługi serwisu refresh
    async def async_handle_refresh(call):
        _LOGGER.debug("Wymuszone odświeżenie danych dla wszystkich instancji %s", DOMAIN)
        for coord in hass.data[DOMAIN].values():
            await coord.async_request_refresh()

    # Rejestruj usługę tylko, jeśli jeszcze nie istnieje
    if not hass.services.has_service(DOMAIN, "refresh"):
        hass.services.async_register(
            DOMAIN,
            "refresh",
            async_handle_refresh,
        )

    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Przeładowanie integracji po zmianie opcji"""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Usunięcie integracji - sprzątamy platformy i usługi"""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Usuwamy dane tej konkretnej instancji
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Jeśli to była ostatnia instancja, usuwamy usługę z systemu
        if not hass.data[DOMAIN]:
            if hass.services.has_service(DOMAIN, "refresh"):
                hass.services.async_remove(DOMAIN, "refresh")
                _LOGGER.debug("Usunięto usługę refresh dla %s (brak aktywnych instancji)", DOMAIN)

    return unload_ok
