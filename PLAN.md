# Phasenplan
## Phase 0 – Gerüst
- [x] Struktur app/, static/, tests/, requirements.txt
- [x] protocol_header.py
- [x] CLAUDE.md, PLAN.md, HANDOFF.md, README.md
- [x] Header-Test
## Phase 1 – Serial, Parser, Simulator
- [ ] serial_link.py (lesen, senden, Wiederverbindung)
- [ ] protocol.py (Parser, Befehle, Pumpen-Maximallaufzeit)
- [ ] simulator.py (Fake-Arduino)
- [ ] Tests Parser/Befehle
## Phase 2 – Backend
- [ ] Zustandsspeicher (zuletzt gesendeter Zustand)
- [ ] REST-Endpunkte (Aktoren, "Alles aus")
- [ ] WebSocket mit Live-Werten
- [ ] Konfigurations-Endpunkt (Sensoren aus Header)
- [ ] Vorbereitete Stelle für Zeitpläne/Automatik
## Phase 3 – Oberfläche
- [ ] SVG-Schema mit Live-Werten und Aktorfarben
- [ ] Menüs (Handy: Panel von unten)
- [ ] Statusleiste, "Alles aus"
## Phase 4 – PWA
- [ ] manifest.json, Icons, Service Worker (wo möglich)
- [ ] Handy-Feinschliff
## Phase 5 – Abschluss
- [ ] Tests abrunden
- [ ] INSTALL.md (Raspberry Pi, systemd)
- [ ] README, finale HANDOFF.md
