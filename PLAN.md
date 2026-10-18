# Phasenplan
## Phase 0 – Gerüst
- [x] Struktur app/, static/, tests/, requirements.txt
- [x] protocol_header.py
- [x] CLAUDE.md, PLAN.md, HANDOFF.md, README.md
- [x] Header-Test
## Phase 1 – Serial, Parser, Simulator
- [x] serial_link.py (lesen, senden, Wiederverbindung)
- [x] protocol.py (Parser, Befehle, Pumpen-Maximallaufzeit)
- [x] simulator.py (Fake-Arduino)
- [x] Tests Parser/Befehle
## Phase 2 – Backend
- [x] Zustandsspeicher (zuletzt gesendeter Zustand)
- [x] REST-Endpunkte (Aktoren, "Alles aus")
- [x] WebSocket mit Live-Werten
- [x] Konfigurations-Endpunkt (Sensoren aus Header)
- [x] Vorbereitete Stelle für Zeitpläne/Automatik
## Phase 3 – Oberfläche
- [x] SVG-Schema mit Live-Werten und Aktorfarben
- [x] Menüs (Handy: Panel von unten)
- [x] Statusleiste, "Alles aus"
## Phase 4 – PWA
- [ ] manifest.json, Icons, Service Worker (wo möglich)
- [ ] Handy-Feinschliff
## Phase 5 – Abschluss
- [ ] Tests abrunden
- [ ] INSTALL.md (Raspberry Pi, systemd)
- [ ] README, finale HANDOFF.md
