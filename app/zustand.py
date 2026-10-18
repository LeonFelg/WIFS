"""Zustandsspeicher: letzte Messwerte, zuletzt gesendeter Zustand je Aktor, Schutzlogik."""
import asyncio
import logging
import time

import protocol_header as h
from app import protocol

log = logging.getLogger(__name__)


class Anlage:
    def __init__(self, link, simulator: bool):
        self.link = link
        self.simulator = simulator
        self.werte: dict[str, float] = {}
        self.messzeit: float | None = None  # time.time() der letzten gültigen Zeile
        # PLATZHALTER: keine Rückmeldung vom Arduino – hier steht der zuletzt GESENDETE Zustand
        self.licht = False
        self.lueftung = False
        self.lueftung_stufe: int | None = None
        self.pumpe = False
        self.pumpe_bis: float | None = None  # monotonic; Ende der Pumpenlaufzeit
        self.duenger_letzte_ml: int | None = None
        self.duenger_zeit: float | None = None
        self.clients: set[asyncio.Queue] = set()

    # --- Lesen ---------------------------------------------------------
    def verbunden(self) -> bool:
        return self.messzeit is not None and time.time() - self.messzeit <= h.VERBINDUNG_TIMEOUT_S

    def snapshot(self) -> dict:
        jetzt = time.time()
        rest = None
        if self.pumpe and self.pumpe_bis is not None:
            rest = max(0.0, round(self.pumpe_bis - time.monotonic(), 1))
        return {
            "verbunden": self.verbunden(),
            "simulator": self.simulator,
            "messzeit": self.messzeit,
            "alter_s": None if self.messzeit is None else round(jetzt - self.messzeit, 1),
            "sensoren": self.werte,
            "aktoren": {
                "pumpe": {"an": self.pumpe, "rest_s": rest},
                "duenger": {"letzte_ml": self.duenger_letzte_ml, "zeit": self.duenger_zeit},
                "licht": {"an": self.licht},
                "lueftung": {"an": self.lueftung, "stufe": self.lueftung_stufe},
            },
        }

    def konfig(self) -> dict:
        return {
            "sensoren": [{"key": k, "name": n, "einheit": e} for k, n, e in h.SENSOR_ORDER],
            "aktoren": [{"key": k, "name": n} for k, n in h.AKTOREN],
            "sendeintervall_s": h.SENDEINTERVALL_S,
            "verbindung_timeout_s": h.VERBINDUNG_TIMEOUT_S,
            "pumpe_max_laufzeit_s": h.PUMPE_MAX_LAUFZEIT_S,
            "simulator": self.simulator,
            # PLATZHALTER: Stufen, Parameter und Rückmeldung sind Annahmen (siehe HANDOFF.md)
            "platzhalter": ["rueckmeldung", "lueftung_stufen", "parameter"],
        }

    # --- Senden --------------------------------------------------------
    def _senden(self, *zeilen: str) -> bool:
        """Sendet Zeilen; False (und Zustand unverändert), wenn die Verbindung fehlt."""
        if not self.link.connected:
            return False
        return all(self.link.write(z) for z in zeilen)

    def pumpe_an(self, laufzeit_s: float | None = None) -> bool:
        """Ohne Laufzeit läuft die Pumpe maximal PUMPE_MAX_LAUFZEIT_S (Schutz gegen Dauerlauf)."""
        if laufzeit_s is None:
            ok = self._senden(protocol.befehl_pumpe(True))
            dauer = h.PUMPE_MAX_LAUFZEIT_S
        else:
            dauer = min(max(laufzeit_s, 0), h.PUMPE_MAX_LAUFZEIT_S)
            ok = self._senden(protocol.befehl_pumpe_laufzeit(dauer))
        if ok:
            self.pumpe = dauer > 0
            self.pumpe_bis = time.monotonic() + dauer
        return ok

    def pumpe_aus(self) -> bool:
        ok = self._senden(protocol.befehl_pumpe(False))
        if ok:
            self.pumpe, self.pumpe_bis = False, None
        return ok

    def duenger(self, ml: float) -> bool:
        ok = self._senden(protocol.befehl_duenger(ml))
        if ok:
            self.duenger_letzte_ml, self.duenger_zeit = int(round(max(ml, 0))), time.time()
        return ok

    def licht_set(self, an: bool) -> bool:
        ok = self._senden(protocol.befehl_licht(an))
        if ok:
            self.licht = an
        return ok

    def lueftung_set(self, an: bool, stufe: int | None = None) -> bool:
        # PLATZHALTER: Stufen sind unklar; mit Stufe wird LUEFTUNG_STUFE gesendet, sonst an/aus.
        zeile = protocol.befehl_lueftung_stufe(stufe) if (an and stufe is not None) else protocol.befehl_lueftung(an)
        ok = self._senden(zeile)
        if ok:
            self.lueftung = an
            self.lueftung_stufe = stufe if an else None
        return ok

    def alles_aus(self) -> bool:
        ok = self._senden(*protocol.befehle_alles_aus())
        if ok:
            self.pumpe, self.pumpe_bis, self.licht = False, None, False
            self.lueftung, self.lueftung_stufe = False, None
        return ok

    # --- Hintergrundaufgaben -------------------------------------------
    def melden(self) -> None:
        """Schickt den aktuellen Stand an alle offenen WebSockets."""
        daten = self.snapshot()
        for q in list(self.clients):
            if q.full():
                q.get_nowait()
            q.put_nowait(daten)

    async def lese_schleife(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            zeile = await loop.run_in_executor(None, self.link.read_line, 1.0)
            if zeile:
                werte = protocol.parse_sensorzeile(zeile)
                if werte is not None:
                    self.werte, self.messzeit = werte, time.time()
                    self.melden()

    async def wach_schleife(self) -> None:
        """Pumpen-Maximallaufzeit, Statusalter und Zeitpläne (jede Sekunde)."""
        while True:
            await asyncio.sleep(1)
            if self.pumpe and self.pumpe_bis is not None and time.monotonic() >= self.pumpe_bis:
                log.info("Pumpenlaufzeit abgelaufen, schalte Pumpe aus")
                self.pumpe_aus()
            self.automatik_tick()
            self.melden()

    def automatik_tick(self) -> None:
        # PLATZHALTER: Zeitpläne/Automatik sind nicht umgesetzt – hier wäre die vorbereitete Stelle.
        pass
