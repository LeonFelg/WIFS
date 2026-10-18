import pytest

import protocol_header as h
from app import protocol
from app.simulator import Simulator


def test_parser_gueltig():
    n = len(h.SENSOR_ORDER)
    zeile = h.TRENNZEICHEN.join(str(10 + i) + ".5" for i in range(n))
    werte = protocol.parse_sensorzeile(zeile + "\r\n")
    assert list(werte) == [k for k, _, _ in h.SENSOR_ORDER]
    assert werte[h.SENSOR_ORDER[0][0]] == 10.5


@pytest.mark.parametrize("zeile", ["", "abc", "1;2", "1;x;3;4", "1;;3;4", "nan;1;2;3", "1;2;3;4;5"])
def test_parser_ungueltig(zeile):
    assert protocol.parse_sensorzeile(zeile) is None


def test_befehle_aus_header():
    assert protocol.befehl_pumpe(True) == h.PUMPE_AN + h.ZEILENENDE
    assert protocol.befehl_licht(False) == h.LICHT_AUS + h.ZEILENENDE
    assert protocol.befehl_duenger(12.4) == h.DUENGER_DOSIEREN.format(ml=12) + h.ZEILENENDE
    assert protocol.befehle_alles_aus() == [b + h.ZEILENENDE for b in h.ALLES_AUS]


def test_pumpe_max_laufzeit():
    assert protocol.befehl_pumpe_laufzeit(10**6) == h.PUMPE_LAUFZEIT.format(s=h.PUMPE_MAX_LAUFZEIT_S) + h.ZEILENENDE
    assert protocol.befehl_pumpe_laufzeit(-5) == h.PUMPE_LAUFZEIT.format(s=0) + h.ZEILENENDE


def test_erkenne_befehl():
    assert protocol.erkenne_befehl(h.PUMPE_AN) == ("PUMPE_AN", {})
    assert protocol.erkenne_befehl(h.DUENGER_DOSIEREN.format(ml=7)) == ("DUENGER_DOSIEREN", {"ml": 7})
    assert protocol.erkenne_befehl("???") is None


def test_simulator_roundtrip():
    sim = Simulator(intervall=0.05)
    sim.open()
    werte = protocol.parse_sensorzeile(sim.read_line(1))
    assert werte is not None and len(werte) == len(h.SENSOR_ORDER)
    assert sim.read_line(0.01) is None  # Intervall noch nicht um
    sim.write(protocol.befehl_licht(True))
    assert sim.zustand["LICHT_AN"] is True
    sim.write(protocol.befehl_licht(False))
    assert sim.zustand["LICHT_AN"] is False
    assert protocol.parse_sensorzeile(sim.read_line(1)) is not None
