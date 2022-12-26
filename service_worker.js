var PWA_CACHE = 'pwa_cache_01';
var urls_to_cache = [
    '/bot-tac-toe/',
    '/bot-tac-toe/manifest.webmanifest',
    '/bot-tac-toe/assets/minireset.min.css',
    '/bot-tac-toe/style.css',
    '/bot-tac-toe/assets/brython/brython.js',
    '/bot-tac-toe/assets/brython/brython_modules.js',
    '/bot-tac-toe/assets/fonts/HKGrotesk-Medium.woff2',
    '/bot-tac-toe/assets/fonts/TTTPiece.ttf?r8pxat',
    '/bot-tac-toe/assets/icons/icon_dropdown.svg',
    '/bot-tac-toe/assets/icons/favicon.svg',
    '/bot-tac-toe/assets/icons/favicon_180.png',
    '/bot-tac-toe/assets/icons/favicon_196.png',
    '/bot-tac-toe/assets/icons/favicon_512.png',
    '/bot-tac-toe/python/interaction.py'
];

self.addEventListener("install", function(event) {
    console.log("WORKER: install event in progress.");
    event.waitUntil(
        caches.open(PWA_CACHE)
        .then(function(cache) {
            console.log('WORKER: opened cache.');
            return cache.addAll(urls_to_cache);
        })
    );
});

self.addEventListener("activate", function(event) {
    console.log("WORKER: activate event in progress.");
    event.waitUntil(
        (async function() {
            // Enable navigation preload if it's supported.
            // See https://developers.google.com/web/updates/2017/02/navigation-preload
            if ("navigationPreload" in self.registration) {
                await self.registration.navigationPreload.enable();
            }
        })()
    );
    // Tell the active service worker to take control of the page immediately.
    self.clients.claim();
});

self.addEventListener("fetch", function(event) {
    console.log("WORKER: Fetching", event.request);
    event.respondWith(
        caches.match(event.request)
        .then(function(response) {
            // Cache hit - return response
            if (response) {
                return response;
            }
            return fetch(event.request);
        })
    );
});
