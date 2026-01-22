![Logo](logo.png)

# mojdomek.eu – Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

Integracja Home Assistant dla czujników poziomu cieczy serwisu **mojdomek.eu**. 
Pozwala na monitorowanie poziomu szamba, wody deszczowej oraz innych zbiorników.

## 🚀 Instalacja

### Przez HACS (Zalecane)
1. Otwórz **HACS** w Home Assistant.
2. Kliknij trzy kropki w prawym górnym rogu i wybierz **Custom repositories** (Niestandardowe repozytoria).
3. Wklej link do tego repozytorium, wybierz kategorię **Integration** i kliknij **Add**.
4. Znajdź integrację `mojdomek.eu` i kliknij **Download**.
5. **Zrestartuj Home Assistant**.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=martinezcb&repository=mojdomek.eu&category=integration)

### Konfiguracja
1. Przejdź do **Ustawienia** → **Urządzenia oraz usługi**.
2. Kliknij **Dodaj integrację** i wyszukaj `mojdomek.eu`.
3. Podaj **ID urządzenia** (znajdziesz je na obudowie czujnika pod klapką baterii lub w panelu mojdomek.eu).
4. Ustaw **Interwał odpytywania** (sugerowane 15-60 minut, aby oszczędzać baterię i zasoby serwera).

[![Dodaj integrację do swojego Home Assistanta](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=mojdomek_eu)

---

## 📊 Dostępne sensory

### Główne (Włączone domyślnie):
* **Poziom** [% i cm]
* **Temperatura** [°C]
* **Napięcie baterii** [V] oraz **Stan baterii** [%]
* **RSSI** [dBm] (Siła sygnału)
* **Ostatni pomiar** (Czas ostatniej aktualizacji)
* **Statystyki**: Następne zapełnienie, Ostatnie opróżnienie

### Diagnostyka (Domyślnie ukryte):
*Nazwy lokalizacji, dane techniczne zbiornika, wersja oprogramowania oraz parametry alarmowe.*
> Aby je włączyć, przejdź do urządzenia w HA, kliknij w nieaktywną encję i wybierz "Włącz encję".

---

## 🛠 Pomoc i wsparcie
Jeśli masz problem z działaniem integracji, otwórz zgłoszenie w sekcji **Issues** na tym repozytorium.

---
*Integracja nie jest oficjalnym produktem firmy mojdomek.eu, lecz narzędziem stworzonym przez społeczność dla użytkowników tego systemu.*
