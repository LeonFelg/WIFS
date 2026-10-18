"""Serielle Verbindung zum Arduino. Simulator hat dieselbe Schnittstelle (siehe simulator.py).

Schnittstelle: open(), close(), connected (bool), read_line(timeout) -> str | None,
write(text). Die Methoden blockieren nur kurz und sind für einen Hintergrund-Thread gedacht.
"""
import logging
import time

import serial

import protocol_header as h

log = logging.getLogger(__name__)

WIEDERVERBINDEN_S = 2.0  # PLATZHALTER: Wartezeit zwischen Verbindungsversuchen, geschätzt


class SerialLink:
    def __init__(self, port: str = h.SERIAL_PORT, baudrate: int = h.BAUDRATE):
        self.port = port
        self.baudrate = baudrate
        self._ser: serial.Serial | None = None
        self._naechster_versuch = 0.0

    @property
    def connected(self) -> bool:
        return self._ser is not None and self._ser.is_open

    def open(self) -> bool:
        """Versucht zu öffnen; höchstens alle WIEDERVERBINDEN_S. Gibt connected zurück."""
        if self.connected:
            return True
        if time.monotonic() < self._naechster_versuch:
            return False
        self._naechster_versuch = time.monotonic() + WIEDERVERBINDEN_S
        try:
            self._ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            log.info("Seriell verbunden: %s", self.port)
        except (serial.SerialException, OSError) as e:
            log.warning("Verbindung zu %s fehlgeschlagen: %s", self.port, e)
            self._ser = None
        return self.connected

    def close(self) -> None:
        if self._ser is not None:
            try:
                self._ser.close()
            except (serial.SerialException, OSError):
                pass
        self._ser = None

    def read_line(self, timeout: float = 1.0) -> str | None:
        """Liest eine Zeile (ohne Zeilenende) oder None. Verbindet bei Abbruch neu."""
        if not self.open():
            time.sleep(min(timeout, 0.2))
            return None
        ende = time.monotonic() + timeout
        puffer = b""
        zeichen = h.ZEILENENDE.encode()
        try:
            while time.monotonic() < ende:
                teil = self._ser.read(1)
                if not teil:
                    continue
                puffer += teil
                if puffer.endswith(zeichen):
                    return puffer[: -len(zeichen)].decode("ascii", errors="replace").strip()
        except (serial.SerialException, OSError) as e:
            log.warning("Lesefehler, Verbindung wird neu aufgebaut: %s", e)
            self.close()
        return None

    def write(self, text: str) -> bool:
        """Sendet text (inkl. Zeilenende, siehe protocol.py). False, wenn nicht verbunden/Fehler."""
        if not self.connected:
            return False
        try:
            self._ser.write(text.encode("ascii"))
            return True
        except (serial.SerialException, OSError) as e:
            log.warning("Schreibfehler, Verbindung wird neu aufgebaut: %s", e)
            self.close()
            return False
