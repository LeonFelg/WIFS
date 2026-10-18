# Übergabe
## Stand
Phasen 0–4 fertig. 16 Tests grün.
- PWA: static/manifest.json (display fullscreen, Icons 192/512), Icons in static/icons/ (erzeugt mit tools/make_icons.py, nur stdlib),
  iOS-Meta-Tags + apple-touch-icon in index.html. Über http://<pi-adresse> läuft alles ohne Service Worker; "Zum Home-Bildschirm" geht auf iOS/Android.
- static/sw.js: nur aktiv, wenn window.isSecureContext (HTTPS/localhost); Netzwerk zuerst, Cache als Rückfall, API/WS nie gecacht.
- Handy: Tippflächen >= 56 px, vergrößerte Treffer-Fläche an Sensor-Plaketten, Safe-Areas, Panel von unten, kein Text-Markieren/Zoom-Doppeltipp.
- Verbindungsabriss: rotes Banner "Verbindung zum Pi unterbrochen", WebSocket-Reconnect mit Backoff (1–5 s), Wiederverbindung bei
  online/visibilitychange/pageshow, Stille-Erkennung (>5 s ohne Nachricht -> neu verbinden).
- Nicht auf echtem Gerät getestet (nur Tests/curl); Layout und Vollbild am Handy prüfen.
## Nächster Schritt
Phase 5: Tests abrunden, INSTALL.md für Raspberry Pi mit systemd-Autostart (Benutzer in Gruppe dialout, Port-Prüfung, --host/--port),
README, abschließende HANDOFF.md. Hinweis für INSTALL: Handy-Zugriff über http://<pi-adresse>:8000.
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
## Hinweis Arduino
Die Pumpen-Maximallaufzeit wird im Pi umgesetzt, gehört aber ZUSÄTZLICH in den Arduino-Code.
