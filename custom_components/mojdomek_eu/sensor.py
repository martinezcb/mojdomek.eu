from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.entity import EntityCategory, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

# Importujemy wszystko ze stałych
from .const import DOMAIN, MANUFACTURER, MODEL

# SŁOWNIK: (Nazwa, Jednostka, DeviceClass, StateClass, Ikona, Kategoria, Domyślnie włączony)
SENSORS = {
    "percent": ("Poziom", "%", None, SensorStateClass.MEASUREMENT, "mdi:waves-arrow-up", None, True),
    "cm": ("Poziom cm", "cm", None, SensorStateClass.MEASUREMENT, "mdi:ruler", None, True),
    "datatime": ("Ostatni pomiar", None, None, None, "mdi:history", None, True),
    "nextfull": ("Następne zapełnienie", None, None, None, "mdi:gauge-full", None, True),
    "lastempty": ("Ostatnie opróżnienie", None, None, None, "mdi:gauge-empty", None, True),
    
    "volts": ("Napięcie", "V", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, None, EntityCategory.DIAGNOSTIC, True),
    "batt_level": ("Stan baterii", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, None, EntityCategory.DIAGNOSTIC, True),
    "rssi": ("RSSI", "dBm", SensorDeviceClass.SIGNAL_STRENGTH, SensorStateClass.MEASUREMENT, None, EntityCategory.DIAGNOSTIC, True),
    "temperature": ("Temperatura", "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None, EntityCategory.DIAGNOSTIC, True),

    "name": ("Nazwa lokalizacji", None, None, None, "mdi:map-marker", EntityCategory.DIAGNOSTIC, False),
    "max": ("Poziom maksymalny", "cm", None, None, "mdi:arrow-up-bold-box", EntityCategory.DIAGNOSTIC, False),
    "tanktype": ("Typ zbiornika", None, None, None, "mdi:tank", EntityCategory.DIAGNOSTIC, False),
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Konfiguracja czujników."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Lista encji do dodania
    entities = [MojDomekSensor(coordinator, entry, key) for key in SENSORS]
    
    # Dodajemy nasz binarny sensor statusu (Prawda/Fałsz)
    entities.append(MojDomekBinaryStatusSensor(coordinator, entry))
    
    async_add_entities(entities)

class MojDomekSensor(CoordinatorEntity, SensorEntity):
    """Standardowe sensory - znikają (unavailable) gdy dane są przeterminowane"""
    _attr_has_entity_name = False

    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator)
        device_id = entry.data["device_id"]
        friendly_name, unit, device_class, state_class, icon, category, enabled = SENSORS[key]

        self.key = key
        self._attr_name = f"mojdomek {device_id} {friendly_name}"
        tech_id = f"mojdomek_{device_id}_{friendly_name}".lower().replace(" ", "_")
        self.entity_id = f"sensor.{tech_id}"
        self._attr_unique_id = f"mojdomek_{device_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_icon = icon
        self._attr_entity_category = category
        self._attr_entity_registry_enabled_default = enabled
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"mojdomek {device_id}",
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=f"https://{MANUFACTURER}",
        )

    @property
    def available(self) -> bool:
        """Sensor dostepny tylko gdy dane sa aktualne"""
        return self.coordinator.last_update_success and self.coordinator.data_is_valid

    @property
    def native_value(self):
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

class MojDomekBinaryStatusSensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor binarny: True (ON) = Dane aktualne, False (OFF) = Przeterminowane"""
    _attr_has_entity_name = False

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        device_id = entry.data["device_id"]
        self._attr_name = f"mojdomek {device_id} Dane aktualne"
        self._attr_unique_id = f"mojdomek_{device_id}_status_binary"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        
        tech_id = f"mojdomek_{device_id}_status_danych".lower()
        self.entity_id = f"binary_sensor.{tech_id}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"mojdomek {device_id}",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def available(self) -> bool:
        """Ten sensor jest zawsze widoczny"""
        return True

    @property
    def is_on(self) -> bool:
        """Zwraca True jeśli dane są aktualne"""
        return self.coordinator.data_is_valid

    @property
    def icon(self) -> str:
        """Dynamiczna zmiana ikonki w zaleznosci od stanu danych"""
        if self.is_on:
            return "mdi:database-eye"
        return "mdi:database-eye-off"