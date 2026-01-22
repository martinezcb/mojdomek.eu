import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import MojDomekCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Konfiguracja integracji"""
    session = async_get_clientsession(hass)
    coordinator = MojDomekCoordinator(hass, session, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.debug("Wstępne odświeżenie zgłosiło błąd: %s", err)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    
    # Rejestrujemy platformę sensorów
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Słuchacz zmian w opcjach - kluczowy dla natychmiastowego przeładowania
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Przeładowanie integracji po zmianie opcji"""
    _LOGGER.info("Przeładowanie integracji MojDomek po zmianie ustawień...")
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Usunięcie integracji"""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok