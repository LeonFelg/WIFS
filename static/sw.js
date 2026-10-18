// Service Worker (nur über HTTPS/localhost aktiv): legt die Oberfläche im Cache ab,
// damit die App auch bei kurzem Verbindungsabriss startet. API und WebSocket nie cachen.
const CACHE = "wifs-v1";
const DATEIEN = ["/", "/style.css", "/app.js", "/manifest.json", "/icons/icon-192.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(DATEIEN)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.pathname.startsWith("/api/") || u.pathname === "/ws") return;
  // Netzwerk zuerst, Cache als Rückfall (Oberfläche soll aktuell bleiben)
  e.respondWith(fetch(e.request).then((r) => {
    const kopie = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, kopie)); return r;
  }).catch(() => caches.match(e.request)));
});
