# WIFS – Bedienprogramm Bewässerung (Prototyp)
Webseite auf dem Raspberry Pi zur Steuerung einer Bewässerungsanlage (Arduino Nano per USB).
Befehle und Sensorreihenfolge: nur in `protocol_header.py`.

## Start im Simulator
    pip install -r requirements.txt
    python -m app.main --simulate
Erreichbar unter http://localhost:8000 (API: /api/status, /api/config; WebSocket: /ws).

## Tests
    pytest
