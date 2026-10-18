# Übergabe
## Stand
Phase 0 fertig: Gerüst, protocol_header.py, CLAUDE.md, PLAN.md, README.md, Header-Test.
Phase-1+-Dateien sind nur Gerüste mit TODO.
## Nächster Schritt
Phase 1: serial_link.py, protocol.py, simulator.py (+ pytest für Parser/Befehle). Nur Header-Werte verwenden.
## Offene Platzhalter
- Port /dev/ttyUSB0, Baudrate 9600 (protocol_header.py)
- Alle Befehlstexte (P1/P0, L1/L0, V1/V0, P{s}, D{ml}, V{stufe}) sind Annahmen
- Sensorauswahl (4 Sensoren); pH, EC fehlen
- Lüfterstufen (nur an/aus), Parameter von Pumpe, Dünger, Lüftung
- Rückmeldung vom Arduino: UI zeigt zuletzt gesendeten Zustand
- Zeitpläne/Automatik (nur vorbereitete Stelle), Historie, Login: nicht umgesetzt
- PUMPE_MAX_LAUFZEIT_S = 60 (geschätzt)
## Hinweis Arduino
Die Pumpen-Maximallaufzeit wird im Pi umgesetzt, gehört aber ZUSÄTZLICH in den Arduino-Code.
