// Offline support: the app shell and art are cached; menus/hours are fetched fresh when online
// and fall back to the last copy when the dining-hall wifi drops.
const VERSION = "gq-v1";
const SHELL = ["./", "index.html", "src/styles.css", "src/app.js", "src/smartlog.js", "manifest.webmanifest", "data/spr.json"];
self.addEventListener("install", (e) => { e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;
  const fresh = u.pathname.endsWith(".json") || u.pathname.endsWith("/") || u.pathname.endsWith(".html") || u.pathname.endsWith(".js") || u.pathname.endsWith(".css");
  if (fresh) {   // network first, so new menus and app updates show up immediately
    e.respondWith(fetch(e.request).then((r) => { const c = r.clone(); caches.open(VERSION).then((cc) => cc.put(e.request, c)); return r; }).catch(() => caches.match(e.request)));
  } else {       // art, audio, fonts: cache first
    e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request).then((r) => { const c = r.clone(); caches.open(VERSION).then((cc) => cc.put(e.request, c)); return r; })));
  }
});
