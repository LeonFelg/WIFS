# Installation auf dem Raspberry Pi

Voraussetzung: Raspberry Pi OS mit Python 3.11+ (`python3 --version`), Netzwerk, Arduino Nano per USB.
Die Beispiele nutzen den Benutzer `pi`; bei anderem Benutzernamen überall ersetzen.

## 1. Repository holen und Umgebung anlegen
```
cd ~
git clone https://github.com/LeonFelg/WIFS.git
cd WIFS
python3 -m venv .venv
.venv/bin/pip install fastapi "uvicorn[standard]" pyserial
```
(`requirements.txt` enthält zusätzlich die Test-Pakete `pytest` und `httpx`; für den Betrieb nicht nötig.)

## 2. Zugriff auf die serielle Schnittstelle
```
sudo usermod -aG dialout pi
```
Danach einmal ab- und wieder anmelden (oder neu starten).

## 3. Seriellen Port finden
Arduino abziehen, `ls /dev/ttyUSB* /dev/ttyACM*` ausführen, Arduino anstecken, erneut ausführen –
der neue Eintrag ist der Port (Nano-Klone meist `/dev/ttyUSB0`, Originale `/dev/ttyACM0`).
Stabiler Name: `ls /dev/serial/by-id/`.
Eintragen in `protocol_header.py` bei `SERIAL_PORT` (dort auch `BAUDRATE`, Befehle und Sensorreihenfolge
an den Arduino-Sketch anpassen – das ist die einzige Stelle dafür).

## 4. Erster Test (ohne Arduino)
```
.venv/bin/python -m app.main --simulate
```
Im Browser `http://<pi-adresse>:8000` öffnen (Pi-Adresse: `hostname -I`). Mit Strg+C beenden.
Mit Arduino: derselbe Befehl ohne `--simulate`; die Statusleiste zeigt "Arduino verbunden".

## 5. Autostart mit systemd
```
sudo cp deploy/wifs.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now wifs
```
Prüfen: `systemctl status wifs`, Log: `journalctl -u wifs -f`.
Neustart nach Änderungen (z. B. `protocol_header.py`): `sudo systemctl restart wifs`.
Soll der Dienst im Simulator laufen, in der Unit `--simulate` an die `ExecStart`-Zeile anhängen.

## 6. Aufruf vom Handy
Handy im selben WLAN: `http://<pi-adresse>:8000` (oder `http://raspberrypi.local:8000`).
- iPhone (Safari): Teilen -> "Zum Home-Bildschirm".
- Android (Chrome): Menü -> "App installieren" bzw. "Zum Startbildschirm".

Ohne HTTPS läuft die App ohne Service Worker (kein Offline-Cache); sonst ist alles nutzbar.
Es gibt keinen Login – den Pi nur im vertrauenswürdigen Heimnetz erreichbar machen, nicht ins Internet freigeben.
