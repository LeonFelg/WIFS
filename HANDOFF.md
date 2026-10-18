# Übergabe
## Stand
Phase 0+1 fertig. app/protocol.py (parse_sensorzeile, befehl_*, befehle_alles_aus, erkenne_befehl),
app/serial_link.py (SerialLink, Wiederverbindung alle 2 s), app/simulator.py (Simulator).
Beide Links haben dieselbe Schnittstelle: open(), close(), connected, read_line(timeout)->str|None, write(text)->bool.
Befehle aus protocol.befehl_* enthalten das Zeilenende bereits. 13 Tests grün. pyserial ist installiert.
## Nächster Schritt
Phase 2: Backend in app/main.py (Argument --simulate wählt Simulator statt SerialLink): Lese-Thread mit read_line + parse_sensorzeile,
Zustandsspeicher (zuletzt gesendeter Zustand, Alter des letzten Messwerts), REST, WebSocket, Konfig-Endpunkt (SENSOR_ORDER),
vorbereitete Stelle für Zeitpläne. Pumpen-Dauerlauf-Überwachung (PUMPE_AN nach PUMPE_MAX_LAUFZEIT_S automatisch aus) gehört in den
Zustandsspeicher – protocol.befehl_pumpe_laufzeit begrenzt nur die Laufzeit-Variante.
## Offene Platzhalter
- Port /dev/ttyUSB0, Baudrate 9600 (protocol_header.py)
- Alle Befehlstexte (P1/P0, L1/L0, V1/V0, P{s}, D{ml}, V{stufe}) sind Annahmen
- Sensorauswahl (4 Sensoren); pH, EC fehlen
- Lüfterstufen (nur an/aus), Parameter von Pumpe, Dünger, Lüftung
- Rückmeldung vom Arduino: UI zeigt zuletzt gesendeten Zustand
- Zeitpläne/Automatik (nur vorbereitete Stelle), Historie, Login: nicht umgesetzt
- PUMPE_MAX_LAUFZEIT_S = 60 (geschätzt)
- Simulator-Wertebereiche und Wiederverbindungszeit (2 s) sind geschätzt
- Düngerdosierung hat keine Obergrenze (nur >= 0)
## Hinweis Arduino
Die Pumpen-Maximallaufzeit wird im Pi umgesetzt, gehört aber ZUSÄTZLICH in den Arduino-Code.
