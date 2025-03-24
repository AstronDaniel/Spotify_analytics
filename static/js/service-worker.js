const CACHE_NAME = 'spotify-analytics-v1';

// Files to cache
const STATIC_CACHE_URLS = [
    '/',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/img/favicon.png'
];

// Install Service Worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(STATIC_CACHE_URLS);
            })
    );
});

// Fetch Event Handler
self.addEventListener('fetch', event => {
    // Skip API requests
    if (event.request.url.includes('/api/')) {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .catch(() => {
                return caches.match(event.request);
            })
    );
});

// Activate Event Handler
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(cacheName => cacheName !== CACHE_NAME)
                    .map(cacheName => caches.delete(cacheName))
            );
        })
    );
});