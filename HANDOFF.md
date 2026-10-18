# Übergabe
## Stand
Phasen 0–3 fertig. Backend (Phase 2) unverändert, siehe API unten. 15 Tests grün.
- static/index.html: SVG-Schema (viewBox 400x540) mit klickbaren Objekten (data-open): Licht, Lüftung, Tank (-> Sensor wasserstand),
  Dünger, Pumpe, Pflanzbereich (-> Sensor bodenfeuchte); Statusleiste; Sheet-Panel; "ALLES AUS"-Knopf (fest unten).
- static/app.js: lädt /api/config, erzeugt Sensor-Plaketten dynamisch (Positionen in POS; unbekannte Sensoren landen automatisch
  in einer Reihe unten), /ws mit Auto-Reconnect, Menüs (MENUES: pumpe, duenger, licht [nur Ein/Aus], lueftung; Sensoren zeigen Wert+Alter).
  Befehle per POST /api/...; 503 -> Toast. Tank-Füllstand folgt Sensor "wasserstand".
- static/style.css: Handy zuerst; Panel von unten, ab 760 px Breite als Karte rechts; Dunkelmodus per prefers-color-scheme.
- Platzhalter in der UI: Chip "Zustand = zuletzt gesendet", orange Marke "Platzhalter" an Pumpen-Laufzeit, Dünger-Menge, Lüfterstufe.
- Nicht im Browser getestet (keine Browser-Automatisierung laut Regeln): nur JS-Syntax (node --check), SVG-Wohlgeformtheit, Auslieferung per Test/curl.
## Nächster Schritt
Phase 4: PWA (manifest.json, Icons, Service Worker nur wo möglich – SW braucht https/localhost; im Heim-WLAN per http nicht
registrierbar, dann nur Manifest + Meta-Tags) und Handy-Feinschliff (Touch-Ziele, Safe-Areas, Layout prüfen). Optische Prüfung am echten Gerät empfohlen.
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
