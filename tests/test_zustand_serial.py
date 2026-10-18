import asyncio
import time

import pytest
import serial

import protocol_header as h
from app import serial_link
from app.serial_link import SerialLink
from app.simulator import Simulator
from app.zustand import Anlage


def test_befehle_ohne_verbindung_aendern_nichts():
    anlage = Anlage(Simulator(), simulator=True)  # nicht geöffnet
    assert anlage.licht_set(True) is False and anlage.licht is False
    assert anlage.alles_aus() is False


def test_pumpe_ohne_laufzeit_ist_begrenzt():
    sim = Simulator(); sim.open()
    anlage = Anlage(sim, simulator=True)
    assert anlage.pumpe_an() and anlage.pumpe
    assert anlage.pumpe_bis - time.monotonic() <= h.PUMPE_MAX_LAUFZEIT_S
    assert anlage.pumpe_an(10**6) and anlage.pumpe_bis - time.monotonic() <= h.PUMPE_MAX_LAUFZEIT_S


def test_wachschleife_schaltet_pumpe_nach_ablauf_aus():
    sim = Simulator(); sim.open()
    anlage = Anlage(sim, simulator=True)
    anlage.pumpe_an()
    anlage.pumpe_bis = time.monotonic() - 1  # Laufzeit überschritten

    async def lauf():
        try:
            await asyncio.wait_for(anlage.wach_schleife(), 1.6)
        except asyncio.TimeoutError:
            pass
    asyncio.run(lauf())
    assert anlage.pumpe is False
    assert sim.zustand.get("PUMPE_AN") is False


def test_alles_aus_sendet_header_befehle():
    sim = Simulator(); sim.open()
    anlage = Anlage(sim, simulator=True)
    anlage.licht_set(True); anlage.lueftung_set(True)
    assert anlage.alles_aus()
    assert sim.befehle[-len(h.ALLES_AUS):] == h.ALLES_AUS
    assert not (anlage.licht or anlage.lueftung or anlage.pumpe)


def test_verbindung_verloren_nach_timeout():
    anlage = Anlage(Simulator(), simulator=True)
    assert anlage.verbunden() is False
    anlage.messzeit = time.time()
    assert anlage.verbunden() is True
    anlage.messzeit = time.time() - h.VERBINDUNG_TIMEOUT_S - 1
    assert anlage.verbunden() is False


class FakeSerial:
    def __init__(self, daten=b""):
        self.daten, self.is_open, self.geschrieben = bytearray(daten), True, b""

    def read(self, n):
        if not self.daten:
            time.sleep(0.01)
            return b""
        b = bytes(self.daten[:n]); del self.daten[:n]
        return b

    def write(self, b):
        self.geschrieben += b

    def close(self):
        self.is_open = False


def test_serial_lesen_schreiben(monkeypatch):
    fake = FakeSerial(b"1;2;3;4" + h.ZEILENENDE.encode())
    monkeypatch.setattr(serial_link.serial, "Serial", lambda *a, **k: fake)
    link = SerialLink()
    assert link.open() and link.read_line(0.5) == "1;2;3;4"
    assert link.write("P1\n") and fake.geschrieben == b"P1\n"


def test_serial_wiederverbinden(monkeypatch):
    versuche = []

    def oeffnen(*a, **k):
        versuche.append(1)
        if len(versuche) == 1:
            raise serial.SerialException("weg")
        return FakeSerial()
    monkeypatch.setattr(serial_link.serial, "Serial", oeffnen)
    monkeypatch.setattr(serial_link, "WIEDERVERBINDEN_S", 0.0)
    link = SerialLink()
    assert link.open() is False and link.write("P1\n") is False  # kein Absturz
    assert link.open() is True


def test_serial_lesefehler_schliesst(monkeypatch):
    class Kaputt(FakeSerial):
        def read(self, n):
            raise serial.SerialException("abgezogen")
    monkeypatch.setattr(serial_link.serial, "Serial", lambda *a, **k: Kaputt())
    link = SerialLink()
    link.open()
    assert link.read_line(0.2) is None and link.connected is False
