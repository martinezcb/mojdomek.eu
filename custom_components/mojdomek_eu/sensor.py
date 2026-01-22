from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

MANUFACTURER = "mojdomek.eu"
MODEL = "Czujnik cieczy"

# SENSORY: (Nazwa, Jednostka, DeviceClass, StateClass, Ikona, Kategoria, Domyślnie włączony)
SENSORS = {
    "percent": ("Poziom", "%", None, SensorStateClass.MEASUREMENT, "mdi:waves-arrow-up", None, True),
    "cm": ("Poziom cm", "cm", None, SensorStateClass.MEASUREMENT, "mdi:ruler", None, True),
    "temperature": ("Temperatura", "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None, None, True),
    "volts": ("Napięcie", "V", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, None, None, True),
    "batt_level": ("Stan baterii", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, None, None, True),
    "rssi": ("RSSI", "dBm", SensorDeviceClass.SIGNAL_STRENGTH, SensorStateClass.MEASUREMENT, None, None, True),
    "datatime": ("Ostatni pomiar", None, None, None, "mdi:history", None, True),
    "nextfull": ("Następne zapełnienie", None, None, None, "mdi:gauge-full", None, True),
    "lastempty": ("Ostatnie opróżnienie", None, None, None, "mdi:gauge-empty", None, True),
# DIAGNOSTYKA: (Domyślnie wyłączone)    
    "name": ("Nazwa lokalizacji", None, None, None, "mdi:map-marker", EntityCategory.DIAGNOSTIC, False),
    "created": ("Data utworzenia", None, None, None, "mdi:calendar-plus", EntityCategory.DIAGNOSTIC, False),
    "max": ("Poziom maksymalny", "cm", None, None, "mdi:arrow-up-bold-box", EntityCategory.DIAGNOSTIC, False),
    "alarm": ("Poziom alarmowy", "cm", None, None, "mdi:alert-outline", EntityCategory.DIAGNOSTIC, False),
    "direction": ("Kierunek zmian", None, None, None, "mdi:arrow-up-down", EntityCategory.DIAGNOSTIC, False),
    "tanktype": ("Typ zbiornika", None, None, None, "mdi:tank", EntityCategory.DIAGNOSTIC, False),
    "mainboard": ("Płyta główna", None, None, None, "mdi:circuit-board", EntityCategory.DIAGNOSTIC, False),
    "software": ("Wersja oprogramowania", None, None, None, "mdi:chip", EntityCategory.DIAGNOSTIC, False),    
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Konfiguracja wszystkich czujników"""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        MojDomekSensor(coordinator, entry, key)
        for key in SENSORS
    )

class MojDomekSensor(CoordinatorEntity, SensorEntity):
    """Reprezentacja czujnika mojdomek.eu"""

    # Wyłączamy to, aby mieć pełną kontrolę nad formatem entity_id
    _attr_has_entity_name = False

    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator)
        device_id = entry.data["device_id"]
        # Pobieramy ładną nazwę ze słownika SENSORS (np. "Ostatni pomiar")
        friendly_name, unit, device_class, state_class, icon, category, enabled = SENSORS[key]

        self.key = key
        
        # 1. USTAWNAMY ŁADNĄ NAZWĘ (Friendly Name)
        self._attr_name = f"mojdomek {device_id} {friendly_name}"
        
        # 2. WYMUSZAMY TECHNICZNE ID (Entity ID)
        tech_id = f"mojdomek_{device_id}_{friendly_name}".lower().replace(" ", "_")
        self.entity_id = f"sensor.{tech_id}"
        
        # Unikalny identyfikator dla bazy danych HA (z prefixem mojdomek dla pewności)
        self._attr_unique_id = f"mojdomek_{device_id}_{key}"
        
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_icon = icon
        self._attr_entity_category = category
        self._attr_entity_registry_enabled_default = enabled
        
        # Automatyczne ustawienie precyzji dla napięcia
        if key == "volts":
            self._attr_suggested_display_precision = 1

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"mojdomek {device_id}",
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=f"https://mojdomek.eu/sensor/{device_id}",
        )

    @property
    def native_value(self):
        """Pobieranie wartości z JSON"""
        try:
            data = self.coordinator.data
            location = data.get("locations", [{}])[0]
            measurement = location.get("measurement", {})
            
            if self.key in measurement:
                return measurement.get(self.key)
            if self.key in location:
                return location.get(self.key)
                
            return None
        except Exception:
            return None
