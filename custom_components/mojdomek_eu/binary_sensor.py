from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.entity import EntityCategory, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, MANUFACTURER, MODEL

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MojDomekBinaryStatusSensor(coordinator, entry)])

class MojDomekBinaryStatusSensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor binarny statusu danych - True gdy aktualne"""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        device_id = entry.data["device_id"]
        self._attr_name = f"mojdomek {device_id} Dane aktualne"
        self._attr_unique_id = f"mojdomek_{device_id}_binary_status"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"mojdomek {device_id}",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def available(self) -> bool:
        return True  # Zawsze dostępny

    @property
    def is_on(self) -> bool:
        """Zwraca True, jeśli dane są aktualne"""
        return self.coordinator.data_is_valid