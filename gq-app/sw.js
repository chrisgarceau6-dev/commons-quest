/* Gainz Quest service worker.

   menu.json is rebuilt nightly and index.html carries the whole app, so both
   are network-first: a connected phone always sees today's menu, and the cache
   is only a fallback for offline use. Everything else (sprites, fonts, audio)
   is immutable in practice, so it is cache-first. */

const VERSION = "gq-v1";
const SHELL = [
  "./",
  "./index.html",
  "./menu.json",
  "./spr.json",
  "./manifest.webmanifest",
  "./map.png",
  "./hero.png",
  "./bear.png",
  "./wyrm.png",
  "./frank.png",
  "./pin_berk.png",
  "./pin_wor.png",
  "./pin_frank.png",
  "./icon-180.png",
  "./icon-512.png",
  "./fonts/press-start-2p-latin-400-normal.woff2",
  "./fonts/rubik-latin-600-normal.woff2",
  "./fonts/rubik-latin-700-normal.woff2",
  "./fonts/rubik-latin-800-normal.woff2",
];

// Always revalidate these against the network first.
const FRESH = /\/(index\.html|menu\.json)$|\/$/;

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(VERSION)
      // Individual misses must not abort the whole install.
      .then((c) => Promise.allSettled(SHELL.map((u) => c.add(u))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;

  if (FRESH.test(new URL(req.url).pathname)) {
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then((hit) => hit || caches.match("./index.html")))
    );
    return;
  }

  e.respondWith(
    caches.match(req).then((hit) =>
      hit ||
      fetch(req).then((res) => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put(req, copy));
        }
        return res;
      })
    )
  );
});
