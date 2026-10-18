# WIFS – Bedienprogramm Bewässerungsanlage (Prototyp)
Arbeitet phasenweise in getrennten Sitzungen. Stand: siehe HANDOFF.md, Plan: PLAN.md.
Pro Sitzung NUR die in der Anweisung genannte Phase.

## Projekt
- Raspberry Pi stellt Webseite bereit (Heim-WLAN, Handy als PWA). Pi <-> Arduino Nano per USB-Seriell.
- Arduino schaltet Pumpe, Dünger, Licht, Lüftung und misst Sensoren. Arduino-Code gehört NICHT zum Projekt.
- Eine Zone. Aktoren: Pumpe (an/aus, Laufzeit s), Dünger (ml), Licht (nur an/aus), Lüftung (an/aus).
- Sensoren: Lufttemperatur, Luftfeuchte, Bodenfeuchte, Wasserstand.

## Technik (fest)
- Python 3.11+, FastAPI, uvicorn, pyserial, WebSocket für Live-Werte.
- UI: HTML/CSS/Vanilla-JS, kein Build, kein npm. Schema als SVG. PWA (manifest, Service Worker nur wo möglich).
- Möglichst wenige Abhängigkeiten. Kommentare und Oberfläche auf Deutsch.

## Header-Regel (wichtigste Anforderung)
protocol_header.py ist die EINZIGE Stelle für Port, Baudrate, Zeilenende, Trennzeichen, SENSOR_ORDER,
alle Befehle (auch Vorlagen wie "D{ml}"), SENDEINTERVALL_S, VERBINDUNG_TIMEOUT_S, PUMPE_MAX_LAUFZEIT_S.
Nirgends sonst Befehle oder Sensorreihenfolge fest einbauen. Datei laienverständlich kommentiert halten.

## Protokoll (Annahme)
Arduino->Pi: alle 5 s eine Zeile, Werte in SENSOR_ORDER-Reihenfolge, getrennt durch TRENNZEICHEN
(z. B. 23.4;56.1;412;78). Ungültige Zeilen loggen und verwerfen. Pi->Arduino: eine Zeile pro Befehl.

## Simulator
`--simulate`: Fake-Arduino mit realistischen Werten, nimmt Befehle an. In der Cloud nur damit testen.

## Platzhalter-Regel
Unklares: sinnvolle Annahme, im Code "# PLATZHALTER: <Grund>", in der UI dezent kennzeichnen,
in HANDOFF.md auflisten. Nicht nachfragen. Zeitpläne/Automatik: nur vorbereitete Stelle. Historie, Login: nicht umsetzen.
Pumpen-Maximallaufzeit im Pi umsetzen; HANDOFF.md vermerkt: gehört zusätzlich in den Arduino.

## Budget-Regeln (knapp, 100 $ gesamt)
- Sparsam: nur nötige Dateien lesen, gezielte Edits, keine langen Ausgaben im Chat.
- Nichts außerhalb des Plans bauen.
- Tests knapp: pytest für Header, Parser, Befehlserzeugung. Keine Browser-Automatisierung.
- Server nur kurz im Hintergrund starten, mit curl prüfen, beenden.
- Phasenende: Tests grün, PLAN.md abhaken, HANDOFF.md aktualisieren, Commit "Phase N: ...", Push,
  dann STOPP mit höchstens 10 Zeilen Zusammenfassung ("Phase N fertig ..."). Keine nächste Phase ungefragt.
- Wird eine Phase zu groß: sauber abschließen, Rest in HANDOFF.md, committen, pushen, stoppen.

## Phasenplan
0 Gerüst, Header, CLAUDE/PLAN/HANDOFF | 1 Serial, Parser, Simulator | 2 Backend (Zustand, REST, WebSocket, Konfig)
3 Oberfläche (SVG, Menüs, Live, Statusleiste, "Alles aus") | 4 PWA, Handy-Feinschliff | 5 Tests, INSTALL.md (systemd), README, HANDOFF
