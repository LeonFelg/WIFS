"""Parser und Befehlserzeugung. Alle Texte und die Reihenfolge kommen aus protocol_header."""
import logging
import re

import protocol_header as h

log = logging.getLogger(__name__)


def parse_sensorzeile(zeile: str) -> dict[str, float] | None:
    """Zerlegt eine Arduino-Zeile in {Sensor-Schlüssel: Wert}.

    Ungültige Zeilen (falsche Anzahl, keine Zahl) werden geloggt und verworfen (None).
    """
    text = zeile.strip()
    teile = text.split(h.TRENNZEICHEN)
    if len(teile) != len(h.SENSOR_ORDER):
        log.warning("Ungültige Zeile verworfen (Anzahl Werte): %r", zeile)
        return None
    werte = {}
    for (schluessel, _name, _einheit), teil in zip(h.SENSOR_ORDER, teile):
        try:
            wert = float(teil.strip().replace(",", "."))
        except ValueError:
            log.warning("Ungültige Zeile verworfen (keine Zahl %r): %r", teil, zeile)
            return None
        if wert != wert or wert in (float("inf"), float("-inf")):
            log.warning("Ungültige Zeile verworfen (kein endlicher Wert): %r", zeile)
            return None
        werte[schluessel] = wert
    return werte


def _zeile(befehl: str) -> str:
    return befehl + h.ZEILENENDE


def befehl_pumpe(an: bool) -> str:
    return _zeile(h.PUMPE_AN if an else h.PUMPE_AUS)


def befehl_licht(an: bool) -> str:
    return _zeile(h.LICHT_AN if an else h.LICHT_AUS)


def befehl_lueftung(an: bool) -> str:
    return _zeile(h.LUEFTUNG_AN if an else h.LUEFTUNG_AUS)


def befehl_pumpe_laufzeit(sekunden: float) -> str:
    """Pumpe für n Sekunden; begrenzt auf PUMPE_MAX_LAUFZEIT_S (Schutz gegen Dauerlauf)."""
    s = int(round(min(max(sekunden, 0), h.PUMPE_MAX_LAUFZEIT_S)))
    return _zeile(h.PUMPE_LAUFZEIT.format(s=s))


def befehl_duenger(ml: float) -> str:
    # PLATZHALTER: Obergrenze fehlt noch (Tankgröße/Dosierpumpe unbekannt); nur >= 0 erzwungen.
    return _zeile(h.DUENGER_DOSIEREN.format(ml=int(round(max(ml, 0)))))


def befehl_lueftung_stufe(stufe: int) -> str:
    return _zeile(h.LUEFTUNG_STUFE.format(stufe=int(stufe)))


def befehle_alles_aus() -> list[str]:
    return [_zeile(b) for b in h.ALLES_AUS]


def erkenne_befehl(zeile: str) -> tuple[str, dict[str, int]] | None:
    """Gegenstück für den Simulator: ordnet eine Befehlszeile einem Header-Namen zu.

    Rückgabe (NAME_DER_KONSTANTE, Parameter) oder None. Feste Befehle haben Vorrang
    vor Vorlagen; Namen werden aus dem Header gelesen, nichts ist hier fest eingebaut.
    """
    text = zeile.strip()
    vorlagen = []
    for name, wert in vars(h).items():
        if not name.isupper() or not isinstance(wert, str) or name in ("ZEILENENDE", "TRENNZEICHEN", "SERIAL_PORT"):
            continue
        if "{" in wert:
            vorlagen.append((name, wert))
        elif wert == text:
            return name, {}
    for name, vorlage in vorlagen:
        muster = re.sub(r"\\\{(\w+)\\\}", r"(?P<\1>\\d+)", re.escape(vorlage))
        m = re.fullmatch(muster, text)
        if m:
            return name, {k: int(v) for k, v in m.groupdict().items()}
    return None
