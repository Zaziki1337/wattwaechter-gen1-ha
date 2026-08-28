# Wattwächter Gen1 für Home Assistant

Eine lokale Home-Assistant-Custom-Integration für den **Wattwächter Wi-Fi/USB
Gen1** mit Tasmota-Firmware. Sie liest die vom installierten Zählerskript
bereitgestellten Werte über die lokale Tasmota-HTTP-API aus.

> Dieses Repository befindet sich im Aufbau. Feldnamen und verfügbare Entitäten
> hängen vom Tasmota-Skript und vom angeschlossenen Stromzähler ab.

## Warum eine Integration und kein Add-on?

HACS installiert Home-Assistant-Custom-Integrationen und keine Supervisor-
Add-ons. Dieses Projekt wird deshalb unter `custom_components/` bereitgestellt
und erscheint nach der Installation unter **Einstellungen → Geräte & Dienste**.

## Installation zum Entwickeln

1. Kopiere `custom_components/wattwaechter_gen1` nach
   `/config/custom_components/wattwaechter_gen1` deiner Home-Assistant-Instanz.
2. Starte Home Assistant neu.
3. Öffne **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
4. Suche nach **Wattwächter Gen1** und gib Hostname oder IP-Adresse ein.

Alternativ kann das Repository in HACS als benutzerdefiniertes Repository der
Kategorie **Integration** hinzugefügt werden.

## Voraussetzungen

- Wattwächter Gen1 im Wi-Fi-Modus und im selben Netzwerk wie Home Assistant
- Ein funktionierendes Tasmota-Zählerskript
- Aktivierte Tasmota-Web-API
- Optional Benutzername und Passwort bei aktivierter Web-Authentifizierung

Die Integration fragt alle 30 Sekunden `Status 10` ab. Die darin enthaltenen
skalaren Messwerte werden beim Einrichten automatisch als Sensoren angelegt.

Für das originale Wattwächter-Gen1-Skript sind folgende Werte explizit
zugeordnet:

| Gruppe | Entitäten | Einheit |
| --- | --- | --- |
| Zählerstände | Netzbezug und Netzeinspeisung gesamt | kWh |
| Netz | Frequenz und aktuelle Wirkleistung | Hz / W |
| Phasen | Strom L1–L3 | A |
| Phasen | Spannung L1–L3 | V |
| Phasen | Wirkleistung L1–L3 | W |
| Phasenwinkel | L1, L2, L3, L1–L2 und L1–L3 | ° |
| Diagnose | Zähler-ID (auch als Geräteseriennummer) | – |

Abweichende Tasmota-Skripte werden weiterhin generisch ausgewertet. Bekannte
Energie-, Leistungs-, Spannungs- und Stromfelder erhalten dabei automatisch
passende Home-Assistant-Geräteklassen und Einheiten.

## Entwicklung

Das Grundgerüst besteht aus einem kleinen asynchronen Tasmota-Client, einem
Config Flow, einem zentralen Data Update Coordinator, dynamischen Sensoren und
Diagnoseunterstützung. Die Sensorzuordnung basiert auf einem echten
`Status 10`-Payload des ausgelieferten Wattwächter-Gen1-Skripts.

## Quellen

- [Wattwächter Wi-Fi/USB Dokumentation](https://docs.wattwächter.de/wifi-usb/)
- [Home Assistant Developer Documentation](https://developers.home-assistant.io/)
- [HACS Publishing Documentation](https://hacs.xyz/docs/publish/integration/)

## Lizenz

MIT License – siehe [LICENSE](LICENSE).
