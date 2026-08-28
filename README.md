# Wattwächter Gen1 für Home Assistant

[![Validate](https://github.com/Zaziki1337/wattwaechter-gen1-ha/actions/workflows/validate.yml/badge.svg)](https://github.com/Zaziki1337/wattwaechter-gen1-ha/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Mit dieser Custom Integration bindest du einen **Wattwächter Wi-Fi/USB Gen1**
mit Tasmota-Firmware direkt in Home Assistant ein. Die Messwerte deines
digitalen Stromzählers werden lokal über die Tasmota-HTTP-API ausgelesen und
als Home-Assistant-Sensoren bereitgestellt.

Die Integration benötigt weder eine Cloud noch einen MQTT-Broker. Home
Assistant kommuniziert direkt mit dem Wattwächter in deinem lokalen Netzwerk.

## Funktionen

- Einrichtung vollständig über die Home-Assistant-Oberfläche
- Lokale Kommunikation über die Tasmota-HTTP-API
- Standardmäßig Aktualisierung alle 2 Sekunden
- Konfigurierbares Abfrageintervall von 2 bis 3600 Sekunden
- Automatische Erkennung der vom Tasmota-Skript gelieferten Messwerte
- Passende Geräteklassen, Einheiten und Langzeitstatistiken
- Geeignete Energiezähler für das Home-Assistant-Energiedashboard
- Optionale Tasmota-Web-Authentifizierung
- Diagnoseinformationen für die Fehlersuche
- Keine Cloud- oder MQTT-Abhängigkeit

## Unterstützte Geräte

Diese Integration ist für den **Wattwächter Wi-Fi/USB Gen1 mit
Tasmota-Firmware** vorgesehen. Der Wattwächter muss sich im Wi-Fi-Modus
befinden und ein funktionierendes Tasmota-Zählerskript verwenden.

Der Wattwächter Plus besitzt eine andere Schnittstelle und wird von dieser
Integration nicht unterstützt.

Welche Messwerte verfügbar sind, hängt vom angeschlossenen Stromzähler, dessen
Freischaltung und dem installierten Tasmota-Skript ab.

## Voraussetzungen

- Home Assistant 2025.1 oder neuer
- Installiertes HACS für die empfohlene Installation
- Wattwächter Gen1 und Home Assistant im selben Netzwerk
- Im Tasmota-Webinterface sichtbare Zählerdaten
- Erreichbare Tasmota-Web-API
- Optional Benutzername und Passwort bei aktivierter Web-Authentifizierung

Du kannst die API vor der Installation in einem Browser testen:

```text
http://WATTWAECHTER-IP/cm?cmnd=Status%2010
```

Die Antwort sollte ein JSON-Objekt mit `StatusSNS` und den Messwerten unter
`eHZ` enthalten.

## Installation über HACS

Das Repository wird zunächst als benutzerdefiniertes HACS-Repository
installiert:

1. Öffne **HACS** in Home Assistant.
2. Öffne oben rechts das Drei-Punkte-Menü.
3. Wähle **Benutzerdefinierte Repositories**.
4. Trage folgende Repository-URL ein:

   ```text
   https://github.com/Zaziki1337/wattwaechter-gen1-ha
   ```

5. Wähle als Kategorie **Integration**.
6. Füge das Repository hinzu und lade **Wattwächter Gen1** herunter.
7. Starte Home Assistant vollständig neu.

## Manuelle Installation

1. Lade dieses Repository herunter.
2. Kopiere den Ordner `custom_components/wattwaechter_gen1` nach:

   ```text
   /config/custom_components/wattwaechter_gen1
   ```

3. Prüfe, dass diese Datei vorhanden ist:

   ```text
   /config/custom_components/wattwaechter_gen1/manifest.json
   ```

4. Starte Home Assistant vollständig neu.

## Einrichtung

1. Öffne **Einstellungen → Geräte & Dienste**.
2. Wähle **Integration hinzufügen**.
3. Suche nach **Wattwächter Gen1**.
4. Gib die IP-Adresse oder den Hostnamen des Wattwächters ein.
5. Trage bei aktivierter Tasmota-Web-Authentifizierung zusätzlich Benutzername
   und Passwort ein.
6. Bestätige die Einrichtung.

Home Assistant prüft die Verbindung und legt anschließend ein Gerät mit den
gefundenen Sensoren an.

## Verfügbare Sensoren

Mit dem originalen Wattwächter-Gen1-Skript werden folgende Felder erkannt:

| Tasmota-Feld | Bedeutung | Einheit | Home-Assistant-Klasse |
| --- | --- | --- | --- |
| `meter_import_total` | Bezogene Energie gesamt | kWh | Energie, Zählerstand |
| `meter_export_total` | Eingespeiste Energie gesamt | kWh | Energie, Zählerstand |
| `net_frequency` | Netzfrequenz | Hz | Frequenz |
| `actual_power` | Aktuelle Wirkleistung gesamt | W | Leistung |
| `current_l1` | Strom Phase L1 | A | Stromstärke |
| `current_l2` | Strom Phase L2 | A | Stromstärke |
| `current_l3` | Strom Phase L3 | A | Stromstärke |
| `voltage_l1` | Spannung Phase L1 | V | Spannung |
| `voltage_l2` | Spannung Phase L2 | V | Spannung |
| `voltage_l3` | Spannung Phase L3 | V | Spannung |
| `eff_power_l1` | Wirkleistung Phase L1 | W | Leistung |
| `eff_power_l2` | Wirkleistung Phase L2 | W | Leistung |
| `eff_power_l3` | Wirkleistung Phase L3 | W | Leistung |
| `phase_l1_l2` | Phasenwinkel L1–L2 | ° | Messwert |
| `phase_l1_l3` | Phasenwinkel L1–L3 | ° | Messwert |
| `phase_l1` | Phasenwinkel L1 | ° | Messwert |
| `phase_l2` | Phasenwinkel L2 | ° | Messwert |
| `phase_l3` | Phasenwinkel L3 | ° | Messwert |
| `ID` | Kennung des Stromzählers | – | Diagnose |

Die Feldnamen aus Tasmotas `StatusSNS`-Antwort werden als Entitätsnamen
übernommen. Liefert ein anderes Zählerskript weitere skalare Werte, legt die
Integration auch dafür Sensoren an. Bekannte Energie-, Leistungs-, Spannungs-
und Stromfelder erhalten automatisch geeignete Metadaten.

## Energiedashboard

Die beiden kumulativen Energiezähler verwenden die Zustandsklasse
`total_increasing` und können deshalb im Home-Assistant-Energiedashboard
verwendet werden:

- `meter_import_total` als **Netzbezug**
- `meter_export_total` als **Rückspeisung ins Netz**

Öffne dazu **Einstellungen → Dashboards → Energie** und wähle die
entsprechenden Entitäten unter **Stromnetz** aus.

## Abfrageintervall ändern

Die Integration fragt den Wattwächter standardmäßig alle 2 Sekunden ab. Das
Intervall kann ohne Neustart geändert werden:

1. Öffne **Einstellungen → Geräte & Dienste**.
2. Öffne **Wattwächter Gen1**.
3. Wähle **Konfigurieren**.
4. Trage ein Intervall zwischen 2 und 3600 Sekunden ein.

Ein sehr kurzes Intervall erzeugt mehr Netzwerkverkehr und zusätzliche Last
auf dem Wattwächter. Bei Verbindungsproblemen empfiehlt sich zunächst ein
größerer Wert.

## Aktualisieren

Updates werden über HACS installiert. Da es sich um Python-Code handelt, muss
Home Assistant nach einem Update vollständig neu gestartet werden. Das bloße
Neuladen oder erneute Einrichten der Integration reicht nicht immer aus.

## Fehlerbehebung

### Die Integration wird nicht gefunden

- Prüfe den Installationspfad unter `/config/custom_components/`.
- Starte Home Assistant nach der Installation vollständig neu.
- Leere gegebenenfalls den Browser-Cache.
- Prüfe unter **Einstellungen → System → Protokolle** auf Fehlermeldungen.

### Verbindung zum Wattwächter schlägt fehl

- Öffne die IP-Adresse des Wattwächters im Browser.
- Teste den Endpunkt `http://WATTWAECHTER-IP/cm?cmnd=Status%2010`.
- Prüfe, ob Home Assistant und Wattwächter dasselbe Netzwerk erreichen können.
- Prüfe Benutzername und Passwort der Tasmota-Web-Authentifizierung.
- Verwende nur Hostname oder IP-Adresse, keinen vollständigen Pfad.

### Es werden keine oder nicht alle Sensoren angelegt

- Prüfe, ob die Werte im Tasmota-Webinterface angezeigt werden.
- Kontrolliere, ob `Status 10` unter `StatusSNS` einen `eHZ`-Block liefert.
- Prüfe das installierte Tasmota-Zählerskript.
- Stelle sicher, dass der Stromzähler für die erweiterten Daten freigeschaltet
  ist.
- Lade die Integration neu, nachdem das Tasmota-Skript neue Felder erhalten
  hat.

### Nach einem Update ist das alte Verhalten weiterhin vorhanden

1. Lade die Integration in HACS erneut herunter.
2. Prüfe die Version in
   `/config/custom_components/wattwaechter_gen1/manifest.json`.
3. Starte Home Assistant vollständig neu.

## Entfernen

1. Entferne **Wattwächter Gen1** unter **Einstellungen → Geräte & Dienste**.
2. Entferne das Repository anschließend in HACS.
3. Starte Home Assistant neu.

Bei einer manuellen Installation muss zusätzlich der Ordner
`/config/custom_components/wattwaechter_gen1` entfernt werden.

## Datenschutz und lokale Kommunikation

Messwerte werden direkt zwischen Home Assistant und dem Wattwächter im lokalen
Netzwerk übertragen. Die Integration selbst verwendet keinen Cloud-Dienst und
sendet keine Telemetriedaten an dieses Projekt.

## Entwicklung und Beiträge

Das Projekt verwendet einen asynchronen Tasmota-Client, einen Home Assistant
Config Flow und einen zentralen Data Update Coordinator. Automatisierte Tests,
Hassfest und die HACS-Validierung laufen über GitHub Actions.

Fehlerberichte und Verbesserungsvorschläge sind unter
[GitHub Issues](https://github.com/Zaziki1337/wattwaechter-gen1-ha/issues)
willkommen. Bitte füge bei Verbindungs- oder Sensorproblemen eine anonymisierte
`Status 10`-Antwort und die relevanten Home-Assistant-Protokolle bei. Entferne
dabei IP-Adressen, Zugangsdaten und persönliche Zählerkennungen.

## Weiterführende Dokumentation

- [Wattwächter Wi-Fi/USB](https://docs.wattwächter.de/wifi-usb/)
- [HACS: Benutzerdefinierte Repositories](https://hacs.xyz/docs/faq/custom_repositories/)
- [Home Assistant: Geräte und Dienste](https://www.home-assistant.io/common-tasks/general/#setting-up-an-integration)

## Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).
