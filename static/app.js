// Bedienoberfläche: lädt /api/config, hört auf /ws, schickt Befehle per REST.
"use strict";
const NS = "http://www.w3.org/2000/svg";
const $ = (id) => document.getElementById(id);
let cfg = null, st = null, offen = null;

// Positionen der Sensor-Plaketten im Schema (nur Layout; Namen/Einheiten kommen von /api/config).
// Unbekannte (neue) Sensoren werden automatisch in einer Reihe unten eingefügt.
const POS = { lufttemperatur: [15, 40], luftfeuchte: [15, 82], wasserstand: [20, 268], bodenfeuchte: [155, 482] };

function el(tag, attrs = {}, text) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (text !== undefined) e.textContent = text;
  return e;
}
function h(tag, attrs = {}, ...kids) {
  const e = document.createElement(tag);
  for (const k in attrs) k === "class" ? (e.className = attrs[k]) : e.setAttribute(k, attrs[k]);
  kids.forEach((c) => e.append(c));
  return e;
}
function toast(t) {
  const e = $("toast"); e.textContent = t; e.hidden = false;
  clearTimeout(toast.t); toast.t = setTimeout(() => (e.hidden = true), 3000);
}
const fmt = (v) => (v == null ? "–" : v.toFixed(1));
const sensor = (key) => cfg.sensoren.find((s) => s.key === key);
const platz = () => h("span", { class: "pl", title: "PLATZHALTER: Parameter noch nicht festgelegt" }, "Platzhalter");

// ---- Sensoren zeichnen ----
function baueSensoren() {
  const g = $("sensoren"); let extra = 0;
  for (const s of cfg.sensoren) {
    let p = POS[s.key];
    if (!p) { p = [10 + (extra % 3) * 130, 500 + Math.floor(extra / 3) * 40]; extra++; }
    const a = el("g", { class: "sensor", id: "s-" + s.key, tabindex: 0, role: "button", "data-open": "sensor:" + s.key, transform: `translate(${p[0]} ${p[1]})` });
    a.append(el("rect", { class: "badge", width: 110, height: 34, rx: 8 }),
      el("text", { class: "n", x: 8, y: 13 }, s.name),
      el("text", { class: "v", x: 8, y: 29, id: "v-" + s.key }, "–"),
      el("text", { class: "n", x: 102, y: 29, "text-anchor": "end" }, s.einheit));
    g.append(a);
  }
}

// ---- Anzeige aktualisieren ----
function zeige(d) {
  st = d;
  document.body.classList.toggle("offline", !d.verbunden);
  $("dot").className = d.verbunden ? "ok" : "bad";
  $("verb").textContent = d.verbunden ? "Arduino verbunden" : "Arduino nicht verbunden";
  $("alter").textContent = "Messwert: " + (d.alter_s == null ? "–" : "vor " + Math.round(d.alter_s) + " s");
  $("sim").hidden = !d.simulator;
  for (const s of cfg.sensoren) {
    const v = d.sensoren[s.key], t = $("v-" + s.key);
    if (t) { t.textContent = fmt(v); $("s-" + s.key).classList.toggle("alt", !d.verbunden); }
  }
  const a = d.aktoren;
  $("o-pumpe").classList.toggle("an", a.pumpe.an);
  $("tropfen").classList.toggle("an", a.pumpe.an);
  $("pumpe-txt").textContent = a.pumpe.an ? (a.pumpe.rest_s != null ? "läuft, noch " + Math.round(a.pumpe.rest_s) + " s" : "läuft") : "aus";
  $("o-licht").classList.toggle("an", a.licht.an);
  $("o-lueftung").classList.toggle("an", a.lueftung.an);
  $("duenger-txt").textContent = a.duenger.letzte_ml != null ? "zuletzt " + a.duenger.letzte_ml + " ml" : "";
  const w = d.sensoren.wasserstand;
  if (w != null) {
    const hh = Math.max(0, Math.min(100, w)) * 1.1;
    $("tankfill").setAttribute("y", 260 - hh); $("tankfill").setAttribute("height", hh);
  }
  if (offen) sheetUpdate();
}

// ---- Befehle ----
async function post(pfad, body) {
  try {
    const r = await fetch("/api/" + pfad, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body || {}) });
    if (r.status === 503) return toast("Arduino nicht verbunden – Befehl nicht gesendet");
    if (!r.ok) return toast("Fehler " + r.status);
    zeige(await r.json());
  } catch { toast("Server nicht erreichbar"); }
}

// ---- Menü (Panel) ----
// Jedes Menü: titel, bau() liefert Elemente, upd() aktualisiert Live-Anteile.
function zahl(id, label, wert, min, max, extra) {
  return h("div", { class: "zeile" }, h("label", { for: id }, label, ...(extra ? [extra] : [])),
    h("input", { id, type: "number", inputmode: "decimal", min, max, value: wert }));
}
function anAus(id, onAn, onAus) {
  const an = h("button", { class: "b", id: id + "-an" }, "Ein"), aus = h("button", { class: "b aus", id: id + "-aus" }, "Aus");
  an.onclick = onAn; aus.onclick = onAus;
  return h("div", { class: "zeile zwei" }, an, aus);
}
function markiere(id, ist) {
  $(id + "-an").classList.toggle("an", ist); $(id + "-aus").classList.toggle("aktiv", !ist);
}
const MENUES = {
  pumpe: {
    titel: "Pumpe",
    bau() {
      const max = cfg.pumpe_max_laufzeit_s;
      const b = h("button", { class: "b pri" }, "Für Laufzeit starten");
      b.onclick = () => post("pumpe", { an: true, laufzeit_s: Number($("p-zeit").value) });
      return [anAus("p", () => post("pumpe", { an: true }), () => post("pumpe", { an: false })),
        h("div", { class: "stat", id: "p-stat" }),
        zahl("p-zeit", `Laufzeit in Sekunden (max. ${max} s)`, Math.min(10, max), 1, max, platz()), b];
    },
    upd() { const p = st.aktoren.pumpe; markiere("p", p.an);
      $("p-stat").textContent = p.an ? "Läuft" + (p.rest_s != null ? ", noch " + Math.round(p.rest_s) + " s" : "") : "Aus"; },
  },
  duenger: {
    titel: "Düngerdosierung",
    bau() {
      const b = h("button", { class: "b pri" }, "Dosieren");
      b.onclick = () => post("duenger", { ml: Number($("d-ml").value) });
      return [h("div", { class: "stat", id: "d-stat" }), zahl("d-ml", "Menge in ml", 5, 0, 1000, platz()), b];
    },
    upd() { const d = st.aktoren.duenger; $("d-stat").textContent = d.letzte_ml != null ? `Zuletzt gesendet: ${d.letzte_ml} ml` : "Noch nichts dosiert"; },
  },
  licht: {
    titel: "Licht",
    bau() { return [anAus("l", () => post("licht", { an: true }), () => post("licht", { an: false })), h("div", { class: "stat" }, "Nur Ein/Aus (nicht dimmbar)")]; },
    upd() { markiere("l", st.aktoren.licht.an); },
  },
  lueftung: {
    titel: "Lüftung",
    bau() {
      return [anAus("v", () => { const s = $("v-stufe").value; post("lueftung", { an: true, stufe: s === "" ? null : Number(s) }); }, () => post("lueftung", { an: false })),
        zahl("v-stufe", "Stufe (optional)", "", 0, 9, platz())];
    },
    upd() { markiere("v", st.aktoren.lueftung.an); },
  },
};
function sensorMenue(key) {
  const s = sensor(key);
  return {
    titel: s.name,
    bau: () => [h("div", { class: "gross", id: "sv" }), h("div", { class: "stat", id: "sa" })],
    upd() { $("sv").textContent = fmt(st.sensoren[key]) + " " + s.einheit;
      $("sa").textContent = st.alter_s == null ? "Noch kein Messwert" : "Gemessen vor " + Math.round(st.alter_s) + " s"; },
  };
}
let aktuell = null;
function oeffne(ziel) {
  aktuell = ziel.startsWith("sensor:") ? (sensor(ziel.slice(7)) ? sensorMenue(ziel.slice(7)) : null) : MENUES[ziel];
  if (!aktuell) return;
  offen = ziel;
  $("sheet-titel").textContent = aktuell.titel;
  $("sheet-inhalt").replaceChildren(...aktuell.bau());
  $("sheet").classList.add("offen"); $("sheet").setAttribute("aria-hidden", "false"); $("scrim").hidden = false;
  if (st) sheetUpdate();
}
function sheetUpdate() { if (aktuell) aktuell.upd(); }
function schliesse() {
  offen = aktuell = null;
  $("sheet").classList.remove("offen"); $("sheet").setAttribute("aria-hidden", "true"); $("scrim").hidden = true;
}

// ---- Start ----
function verbinde() {
  const ws = new WebSocket((location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws");
  ws.onmessage = (e) => zeige(JSON.parse(e.data));
  ws.onclose = () => {
    $("dot").className = "bad"; $("verb").textContent = "Server getrennt";
    document.body.classList.add("offline");
    setTimeout(verbinde, 2000);
  };
}
async function start() {
  try { cfg = await (await fetch("/api/config")).json(); }
  catch { $("verb").textContent = "Server nicht erreichbar"; return setTimeout(start, 2000); }
  baueSensoren();
  document.addEventListener("click", (e) => { const t = e.target.closest("[data-open]"); if (t) oeffne(t.dataset.open); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") schliesse();
    if ((e.key === "Enter" || e.key === " ") && e.target.dataset && e.target.dataset.open) { e.preventDefault(); oeffne(e.target.dataset.open); }
  });
  $("sheet-zu").onclick = $("scrim").onclick = schliesse;
  $("alles-aus").onclick = () => post("alles-aus");
  verbinde();
}
start();
