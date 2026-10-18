# Übergabe (Stand: alle Phasen 0–5 fertig, Prototyp vollständig)
Für Claude Code / Weiterentwicklung. Regeln: CLAUDE.md. Installation: INSTALL.md. 24 Tests grün (`pytest`).
Nur im Simulator getestet – nie mit echter Hardware, nie auf einem echten Handy.

## Aufbau
- `protocol_header.py`: einzige Stelle für Port, Baudrate, Zeilenende, Trennzeichen, SENSOR_ORDER, AKTOREN, Befehle (auch Vorlagen),
  ALLES_AUS, SENDEINTERVALL_S, VERBINDUNG_TIMEOUT_S, PUMPE_MAX_LAUFZEIT_S.
- `app/protocol.py`: parse_sensorzeile (ungültig -> loggen, verwerfen), befehl_* (liefern Zeile inkl. Zeilenende), erkenne_befehl (für Simulator).
- `app/serial_link.py` / `app/simulator.py`: gleiche Schnittstelle `open() close() connected read_line(timeout) write(text)`.
  SerialLink verbindet nach Abbruch alle 2 s neu. Simulator: Werte folgen der Pumpe (Bodenfeuchte steigt, Tank sinkt).
- `app/zustand.py` (Klasse Anlage): letzte Messwerte + Zeitstempel, zuletzt gesendeter Aktorzustand, Pumpen-Maximallaufzeit
  (Wach-Schleife, 1 s), Broadcast an WebSockets, `automatik_tick()` = vorbereitete Stelle.
- `app/main.py`: create_app(simulate); REST /api/config, /api/status, POST /api/pumpe {an, laufzeit_s?}, /duenger {ml}, /licht {an},
  /lueftung {an, stufe?}, /alles-aus (503 ohne Verbindung); WebSocket /ws (Snapshot sofort, je Messung, jede Sekunde); liefert static/.
- `static/`: index.html (SVG-Schema), app.js (Config laden, Sensor-Plaketten dynamisch, Menüs, WS-Reconnect, Banner), style.css,
  manifest.json, sw.js (nur HTTPS/localhost), icons/. `deploy/wifs.service`: systemd.
- Tests: tests/test_header, test_protocol (Parser, Befehle, Simulator), test_api (REST, WS, Oberfläche, PWA), test_zustand_serial (Schutzlogik, SerialLink mit Fake).

## Neue Sensoren/Befehle (ohne Code zu ändern)
Sensor: Zeile in SENSOR_ORDER (Reihenfolge = Arduino-Reihenfolge); erscheint automatisch in der Oberfläche (unten in einer Reihe,
feste Position optional in `POS` in static/app.js). Befehl ändern: nur Header.

## Ideen
- Automatik/Zeitpläne: in `Anlage.automatik_tick()` (läuft jede Sekunde). Vorschlag: Datei `app/automatik.py` mit Regeln
  (Uhrzeit-Zeitplan: Licht an/aus, Pumpe X s; Schwellwert: Bodenfeuchte < Grenze -> Pumpe n s, mit Mindestabstand und Wasserstand-Sperre),
  Konfiguration als JSON-Datei (`data/zeitplaene.json`), REST /api/zeitplaene, Menüpunkt in der UI. Alles über dieselben Anlage-Methoden senden.
  Sicherheitsgrenzen (Maximallaufzeit, Pumpe aus bei leerem Tank) vor jedem Automatikbefehl prüfen.
- Historie: Messwerte in `Anlage.lese_schleife` zusätzlich in SQLite (sqlite3 aus der Standardbibliothek) schreiben, z. B. jede Minute
  gemittelt; REST /api/verlauf?sensor=&von=; kleines Liniendiagramm als SVG im Sensor-Menü. Aufbewahrung begrenzen (SD-Karte schonen).
- Rückmeldung vom Arduino: echte Zustände/Bestätigungen parsen (zusätzliche Zeilenart, im Header beschreiben) und statt "zuletzt gesendet" anzeigen.
- HTTPS (z. B. Caddy mit lokalem Zertifikat), dann greift der Service Worker; optional Login/PIN, falls der Pi über das Heimnetz hinaus erreichbar wird.
- Mehrere Zonen: AKTOREN/Sensoren pro Zone erweitern, Schema je Zone.

## Wichtig für den Arduino
Die Pumpen-Maximallaufzeit (PUMPE_MAX_LAUFZEIT_S) wird im Pi umgesetzt, gehört aber ZUSÄTZLICH in den Arduino-Code
(Schutz bei Ausfall von Pi/USB/WLAN). Ebenso sinnvoll dort: Pumpe aus bei leerem Tank, Obergrenze für Düngermenge.

## Offene Platzhalter
- Port /dev/ttyUSB0, Baudrate 9600; alle Befehlstexte (P1/P0, L1/L0, V1/V0, P{s}, D{ml}, V{stufe}) sind Annahmen
- Sensorauswahl (4 Sensoren); pH, EC fehlen
- Lüfterstufen (nur an/aus), Parameter von Pumpe, Dünger, Lüftung
- Rückmeldung vom Arduino: UI zeigt zuletzt gesendeten Zustand
- Zeitpläne/Automatik (nur vorbereitete Stelle automatik_tick), Historie, Login: nicht umgesetzt
- PUMPE_MAX_LAUFZEIT_S = 60 (geschätzt); Simulator-Wertebereiche und Wiederverbindungszeit (2 s) geschätzt
- Düngerdosierung hat keine Obergrenze (nur >= 0)
- HTTPS (PLATZHALTER): fehlt im Prototyp, daher kein Service Worker über http://<pi-adresse>. Für HTTPS z. B. Reverse-Proxy (Caddy) mit
  lokalem Zertifikat vor uvicorn setzen; sw.js registriert sich dann automatisch.
- Manifest: start_url "/" und Port 80/8000 je nach Installation; "fullscreen" wird von iOS ignoriert (dort Standalone).
