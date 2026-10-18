"""Fake-Arduino für --simulate: gleiche Schnittstelle wie SerialLink."""
import logging
import math
import queue
import random
import time

import protocol_header as h
from app import protocol

log = logging.getLogger(__name__)

# PLATZHALTER: Wertebereiche je Sensor-Schlüssel (Mittelwert, Schwankung); unbekannte Sensoren: 50 ± 5
_BEREICH = {
    "lufttemperatur": (23.0, 2.0),
    "luftfeuchte": (55.0, 8.0),
    "bodenfeuchte": (45.0, 0.0),  # wird unten dynamisch geführt
    "wasserstand": (80.0, 0.0),
}


class Simulator:
    def __init__(self, intervall: float = h.SENDEINTERVALL_S):
        self.intervall = intervall
        self.zustand: dict[str, bool] = {}  # NAME der Header-Konstante -> zuletzt gesetzt
        self.befehle: list[str] = []        # empfangene Zeilen (für Tests/Debug)
        self._q: queue.Queue[str] = queue.Queue()
        self._offen = False
        self._naechster = 0.0
        self._t0 = time.monotonic()
        self._boden = 45.0
        self._tank = 80.0
        self._pumpe_bis = 0.0

    @property
    def connected(self) -> bool:
        return self._offen

    def open(self) -> bool:
        if not self._offen:
            self._offen = True
            self._naechster = time.monotonic()  # erste Zeile sofort
        return True

    def close(self) -> None:
        self._offen = False

    def _pumpe_laeuft(self) -> bool:
        return self.zustand.get("PUMPE_AN", False) or time.monotonic() < self._pumpe_bis

    def _messen(self) -> str:
        t = time.monotonic() - self._t0
        if self._pumpe_laeuft():
            self._boden = min(100.0, self._boden + 3.0)
            self._tank = max(0.0, self._tank - 1.0)
        else:
            self._boden = max(15.0, self._boden - 0.2)
        werte = []
        for schluessel, _n, _e in h.SENSOR_ORDER:
            if schluessel == "bodenfeuchte":
                w = self._boden + random.gauss(0, 0.3)
            elif schluessel == "wasserstand":
                w = self._tank + random.gauss(0, 0.2)
            else:
                mitte, amp = _BEREICH.get(schluessel, (50.0, 5.0))
                w = mitte + amp * math.sin(t / 600) + random.gauss(0, 0.2)
            werte.append(f"{w:.1f}")
        return h.TRENNZEICHEN.join(werte)

    def read_line(self, timeout: float = 1.0) -> str | None:
        if not self._offen:
            return None
        ende = time.monotonic() + timeout
        while True:
            jetzt = time.monotonic()
            if jetzt >= self._naechster:
                self._naechster = jetzt + self.intervall
                return self._messen()
            rest = min(ende, self._naechster) - jetzt
            if rest <= 0:
                return None
            time.sleep(min(rest, 0.05))

    def write(self, text: str) -> bool:
        if not self._offen:
            return False
        for zeile in text.split(h.ZEILENENDE):
            if zeile.strip():
                self._befehl(zeile)
        return True

    def _befehl(self, zeile: str) -> None:
        self.befehle.append(zeile)
        erkannt = protocol.erkenne_befehl(zeile)
        if erkannt is None:
            log.warning("Simulator: unbekannter Befehl %r", zeile)
            return
        name, par = erkannt
        # Paare AN/AUS aus dem Header: Name endet auf _AN bzw. _AUS
        if name.endswith("_AN"):
            self.zustand[name] = True
        elif name.endswith("_AUS"):
            self.zustand[name[:-4] + "_AN"] = False
        elif name == "PUMPE_LAUFZEIT":
            self._pumpe_bis = time.monotonic() + par["s"]
        log.info("Simulator: %s %s", name, par)
