# Übergabe
## Stand
Phasen 0–2 fertig. Backend läuft: `python -m app.main [--simulate] [--port 8000]`, liefert auch static/ unter "/".
- app/zustand.py: Klasse Anlage (Messwerte+Zeitstempel, zuletzt gesendeter Aktorzustand, Pumpen-Maximallaufzeit,
  Wach-Schleife jede Sekunde, `automatik_tick()` = vorbereitete Stelle für Zeitpläne).
- app/main.py: create_app(simulate). REST (JSON): GET /api/config, GET /api/status,
  POST /api/pumpe {an, laufzeit_s?}, /api/duenger {ml}, /api/licht {an}, /api/lueftung {an, stufe?}, /api/alles-aus.
  Antwort jeweils = Status-Snapshot; 503 wenn Arduino nicht verbunden (Zustand bleibt dann unverändert).
  WebSocket /ws: sendet Snapshot sofort, bei jeder Messung und jede Sekunde.
- Snapshot: verbunden, simulator, messzeit, alter_s, sensoren{key:wert}, aktoren{pumpe{an,rest_s}, duenger{letzte_ml,zeit},
  licht{an}, lueftung{an,stufe}}. Config enthält Sensoren (key,name,einheit), Aktoren (key,name), Zeiten, platzhalter-Liste.
- Pumpe ohne Laufzeit läuft höchstens PUMPE_MAX_LAUFZEIT_S, danach sendet der Pi PUMPE_AUS.
- Header neu: AKTOREN (Schlüssel, Anzeigename). 14 Tests grün.
## Nächster Schritt
Phase 3: Oberfläche in static/ (SVG-Schema, Menüs/Bottom-Sheet, Live-Werte per /ws, Statusleiste, "Alles aus").
Sensor-/Aktornamen aus /api/config holen, nichts fest einbauen außer SVG-Positionen. Platzhalter dezent kennzeichnen.
## Offene Platzhalter
- Port /dev/ttyUSB0, Baudrate 9600; alle Befehlstexte (P1/P0, L1/L0, V1/V0, P{s}, D{ml}, V{stufe}) sind Annahmen
- Sensorauswahl (4 Sensoren); pH, EC fehlen
- Lüfterstufen (nur an/aus), Parameter von Pumpe, Dünger, Lüftung
- Rückmeldung vom Arduino: UI zeigt zuletzt gesendeten Zustand
- Zeitpläne/Automatik (nur vorbereitete Stelle automatik_tick), Historie, Login: nicht umgesetzt
- PUMPE_MAX_LAUFZEIT_S = 60 (geschätzt); Simulator-Wertebereiche und Wiederverbindungszeit (2 s) geschätzt
- Düngerdosierung hat keine Obergrenze (nur >= 0)
## Hinweis Arduino
Die Pumpen-Maximallaufzeit wird im Pi umgesetzt, gehört aber ZUSÄTZLICH in den Arduino-Code.
