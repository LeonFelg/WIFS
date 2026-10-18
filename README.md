# WIFS – Bedienprogramm Bewässerung (Prototyp)

Ein Raspberry Pi stellt eine Webseite (auch als Handy-App/PWA) bereit, mit der eine Bewässerungsanlage
(Pumpe, Düngerdosierung, Licht, Lüftung, Sensoren) bedient wird. Der Pi spricht per USB-Seriell mit einem
Arduino Nano. Der Arduino-Code gehört nicht zu diesem Projekt.

**Befehle, Sensorreihenfolge, Port und Zeiten stehen ausschließlich in `protocol_header.py`.**

## Schnellstart (Simulator, ohne Arduino)
    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python -m app.main --simulate
Dann `http://localhost:8000` öffnen. Optionen: `--host`, `--port`.

## Auf dem Raspberry Pi
Siehe [INSTALL.md](INSTALL.md) (venv, dialout, Port, systemd-Autostart, Handy).

## Aufbau
- `protocol_header.py` – Schnittstelle Pi <-> Arduino (laienverständlich kommentiert)
- `app/` – `protocol.py` (Parser/Befehle), `serial_link.py`, `simulator.py`, `zustand.py`, `main.py` (REST, WebSocket)
- `static/` – Oberfläche (HTML/CSS/Vanilla-JS, SVG-Schema, PWA)
- `deploy/wifs.service` – systemd-Unit; `tools/make_icons.py` – Icons erzeugen
- `PLAN.md`, `HANDOFF.md`, `CLAUDE.md` – Plan, Übergabe, Regeln für Claude Code

## API
`GET /api/config`, `GET /api/status`, `POST /api/pumpe|duenger|licht|lueftung|alles-aus`, WebSocket `/ws`.

## Tests
    .venv/bin/pytest
