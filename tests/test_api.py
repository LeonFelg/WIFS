import protocol_header as h
from fastapi.testclient import TestClient

from app.main import create_app


def test_api_simulator():
    with TestClient(create_app(simulate=True, sim_intervall=0.1)) as c:
        cfg = c.get("/api/config").json()
        assert [s["key"] for s in cfg["sensoren"]] == [k for k, _, _ in h.SENSOR_ORDER]
        with c.websocket_connect("/ws") as ws:
            snap = ws.receive_json()
            assert "aktoren" in snap
            for _ in range(5):
                snap = ws.receive_json()
                if snap["verbunden"]:
                    break
            assert snap["verbunden"] and set(snap["sensoren"]) == {k for k, _, _ in h.SENSOR_ORDER}
        assert c.post("/api/licht", json={"an": True}).json()["aktoren"]["licht"]["an"] is True
        p = c.post("/api/pumpe", json={"an": True, "laufzeit_s": 10**6}).json()["aktoren"]["pumpe"]
        assert p["an"] and p["rest_s"] <= h.PUMPE_MAX_LAUFZEIT_S
        s = c.post("/api/alles-aus").json()["aktoren"]
        assert not s["pumpe"]["an"] and not s["licht"]["an"]
        assert c.post("/api/duenger", json={"ml": -1}).status_code == 422


def test_oberflaeche_ausgeliefert():
    with TestClient(create_app(simulate=True, sim_intervall=0.1)) as c:
        r = c.get("/")
        assert r.status_code == 200 and "schema" in r.text
        # Sensornamen dürfen nicht fest im HTML stehen (kommen von /api/config)
        assert all(n not in r.text for _, n, _ in h.SENSOR_ORDER)
        assert c.get("/app.js").status_code == 200 and c.get("/style.css").status_code == 200
