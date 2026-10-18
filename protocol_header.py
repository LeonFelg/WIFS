"""
protocol_header.py – DIE EINZIGE STELLE für Schnittstelle Pi <-> Arduino.

Hier ändern Sie (auch ohne Programmierkenntnisse):
  * den USB-Anschluss und die Geschwindigkeit      -> Abschnitt 1
  * die Reihenfolge/Namen der Sensoren              -> Abschnitt 2
  * die Befehle, die der Pi an den Arduino sendet   -> Abschnitt 3
  * Zeitwerte und Sicherheitsgrenzen                -> Abschnitt 4

Regeln:
  * Texte stehen in Anführungszeichen "...", Zahlen ohne.
  * Kein anderer Programmteil darf Befehle oder die Sensorreihenfolge
    fest einbauen – alles kommt von hier.
"""

# ---------------------------------------------------------------------------
# 1. Verbindung
# ---------------------------------------------------------------------------
# PLATZHALTER: Typischer Port eines Arduino Nano am Raspberry Pi; mit
# "ls /dev/ttyUSB* /dev/ttyACM*" prüfen (Nano-Klone: ttyUSB0, Originale: ttyACM0).
SERIAL_PORT = "/dev/ttyUSB0"
# PLATZHALTER: Muss zur Baudrate im Arduino-Sketch passen.
BAUDRATE = 9600
# Zeilenende, das jede Zeile (in beide Richtungen) abschließt.
ZEILENENDE = "\n"
# Trennzeichen zwischen den Sensorwerten einer Zeile, z. B. 23.4;56.1;412;78
TRENNZEICHEN = ";"

# ---------------------------------------------------------------------------
# 2. Sensoren
# ---------------------------------------------------------------------------
# Reihenfolge = Reihenfolge der Werte in der Zeile vom Arduino.
# Jeder Eintrag: (Schlüssel, Anzeigename, Einheit)
#   Schlüssel: kurzer Name ohne Leerzeichen/Umlaute (intern, z. B. für die Grafik)
# Sensor umsortieren: Zeile verschieben. Sensor hinzufügen: Zeile ergänzen
# (und im Arduino an der passenden Stelle senden).
# PLATZHALTER: Sensorauswahl ist angenommen; pH und EC sind noch nicht dabei.
SENSOR_ORDER = [
    ("lufttemperatur", "Lufttemperatur", "°C"),
    ("luftfeuchte",    "Luftfeuchte",    "%"),
    ("bodenfeuchte",   "Bodenfeuchte",   "%"),
    ("wasserstand",    "Wasserstand",    "%"),
]

# Aktoren, die die Oberfläche anzeigt: (Schlüssel, Anzeigename). Reine Anzeige –
# die Befehle dazu stehen in Abschnitt 3.
AKTOREN = [
    ("pumpe",    "Pumpe"),
    ("duenger",  "Düngerdosierung"),
    ("licht",    "Licht"),
    ("lueftung", "Lüftung"),
]

# ---------------------------------------------------------------------------
# 3. Befehle Pi -> Arduino (eine Zeile pro Befehl, Zeilenende wird automatisch angehängt)
# ---------------------------------------------------------------------------
# PLATZHALTER: Alle Befehlstexte sind Annahmen; an den Arduino-Sketch anpassen.
PUMPE_AN  = "P1"
PUMPE_AUS = "P0"
LICHT_AN  = "L1"
LICHT_AUS = "L0"
LUEFTUNG_AN  = "V1"
LUEFTUNG_AUS = "V0"

# Befehle mit Wert: {platzhalter} wird durch die Zahl ersetzt.
# PLATZHALTER: Pumpe mit Laufzeit; alternativ nur PUMPE_AN + PUMPE_AUS nutzen.
PUMPE_LAUFZEIT = "P{s}"        # {s} = Laufzeit in Sekunden
DUENGER_DOSIEREN = "D{ml}"     # {ml} = Menge in Milliliter
# PLATZHALTER: Lüfterstufen sind noch nicht festgelegt (Lüftung vorerst nur an/aus).
LUEFTUNG_STUFE = "V{stufe}"

# "Alles aus": Befehle, die der Pi nacheinander sendet.
ALLES_AUS = [PUMPE_AUS, LICHT_AUS, LUEFTUNG_AUS]

# ---------------------------------------------------------------------------
# 4. Zeiten und Sicherheit
# ---------------------------------------------------------------------------
# Intervall, in dem der Arduino Messwerte sendet (Sekunden).
SENDEINTERVALL_S = 5
# Nach so vielen Sekunden ohne gültige Zeile gilt "Verbindung verloren".
VERBINDUNG_TIMEOUT_S = 3 * SENDEINTERVALL_S
# Schutz gegen Dauerlauf: Der Pi schaltet die Pumpe nach dieser Zeit selbst aus.
# PLATZHALTER: 60 s ist geschätzt; Wert an die Anlage anpassen.
# Hinweis: Diese Grenze gehört zusätzlich in den Arduino (HANDOFF.md).
PUMPE_MAX_LAUFZEIT_S = 60
