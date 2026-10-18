"""FastAPI-App: REST, WebSocket, statische Oberfläche. Start: python -m app.main [--simulate]"""
import argparse
import asyncio
import contextlib
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import protocol_header as h
from app.serial_link import SerialLink
from app.simulator import Simulator
from app.zustand import Anlage

STATIC = Path(__file__).resolve().parent.parent / "static"


class AnAus(BaseModel):
    an: bool


class PumpeIn(BaseModel):
    an: bool
    laufzeit_s: float | None = Field(None, ge=0)


class LueftungIn(BaseModel):
    an: bool
    stufe: int | None = Field(None, ge=0)  # PLATZHALTER: Stufen unklar


class DuengerIn(BaseModel):
    ml: float = Field(ge=0)


def create_app(simulate: bool = False, sim_intervall: float = h.SENDEINTERVALL_S) -> FastAPI:
    link = Simulator(sim_intervall) if simulate else SerialLink()
    anlage = Anlage(link, simulator=simulate)

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        link.open()
        tasks = [asyncio.create_task(anlage.lese_schleife()), asyncio.create_task(anlage.wach_schleife())]
        yield
        for t in tasks:
            t.cancel()
        link.close()

    app = FastAPI(title="WIFS", lifespan=lifespan)
    app.state.anlage = anlage

    def quittieren(ok: bool) -> dict:
        if not ok:
            raise HTTPException(503, "Arduino nicht verbunden")
        anlage.melden()
        return anlage.snapshot()

    @app.get("/api/config")
    def config():
        return anlage.konfig()

    @app.get("/api/status")
    def status():
        return anlage.snapshot()

    @app.post("/api/pumpe")
    def pumpe(p: PumpeIn):
        return quittieren(anlage.pumpe_an(p.laufzeit_s) if p.an else anlage.pumpe_aus())

    @app.post("/api/duenger")
    def duenger(d: DuengerIn):
        return quittieren(anlage.duenger(d.ml))

    @app.post("/api/licht")
    def licht(a: AnAus):
        return quittieren(anlage.licht_set(a.an))

    @app.post("/api/lueftung")
    def lueftung(l: LueftungIn):
        return quittieren(anlage.lueftung_set(l.an, l.stufe))

    @app.post("/api/alles-aus")
    def alles_aus():
        return quittieren(anlage.alles_aus())

    @app.websocket("/ws")
    async def ws(sock: WebSocket):
        await sock.accept()
        q: asyncio.Queue = asyncio.Queue(maxsize=5)
        anlage.clients.add(q)
        try:
            await sock.send_json(anlage.snapshot())
            while True:
                await sock.send_json(await q.get())
        except (WebSocketDisconnect, RuntimeError):
            pass
        finally:
            anlage.clients.discard(q)

    if STATIC.is_dir():
        app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
    return app


def main() -> None:
    import uvicorn

    ap = argparse.ArgumentParser(description="WIFS Bedienprogramm")
    ap.add_argument("--simulate", action="store_true", help="Fake-Arduino statt serieller Verbindung")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    uvicorn.run(create_app(a.simulate), host=a.host, port=a.port)


if __name__ == "__main__":
    main()
