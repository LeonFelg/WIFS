"""Erzeugt die App-Icons (PNG, nur Standardbibliothek): python tools/make_icons.py"""
import struct
import zlib
from pathlib import Path

BG, FG = (27, 94, 63), (255, 255, 255)


def png(n: int) -> bytes:
    """Grüner Hintergrund mit weißem Wassertropfen (Kreis + Spitze), 4x4-Supersampling."""
    cx, cy, r = n / 2, n * 0.58, n * 0.24
    top = n * 0.18
    zeilen = []
    for y in range(n):
        z = bytearray([0])
        for x in range(n):
            treffer = 0
            for sy in (0.125, 0.375, 0.625, 0.875):
                for sx in (0.125, 0.375, 0.625, 0.875):
                    px, py = x + sx, y + sy
                    im_kreis = (px - cx) ** 2 + (py - cy) ** 2 <= r * r
                    # Spitze: Dreieck von (cx, top) zu den Tangentenpunkten
                    breite = r * (py - top) / (cy - top) * 0.92 if top <= py <= cy else -1
                    treffer += im_kreis or abs(px - cx) <= breite
            a = treffer / 16
            z += bytes(round(BG[i] * (1 - a) + FG[i] * a) for i in range(3))
        zeilen.append(bytes(z))
    roh = b"".join(zeilen)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(roh, 9)) + chunk(b"IEND", b""))


ziel = Path(__file__).resolve().parent.parent / "static" / "icons"
for name, n in (("icon-192.png", 192), ("icon-512.png", 512), ("apple-touch-icon.png", 180)):
    (ziel / name).write_bytes(png(n))
