/* eslint-disable no-restricted-globals */

const CACHE_NAME = 'medmatch-v1';
const STATIC_CACHE = 'medmatch-static-v1';
const DYNAMIC_CACHE = 'medmatch-dynamic-v1';
const TRANSLATION_CACHE = 'medmatch-translations-v1'; // PA-2: Translation cache

// Static assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/offline.html'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[ServiceWorker] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== STATIC_CACHE && name !== DYNAMIC_CACHE && name !== TRANSLATION_CACHE)
          .map((name) => {
            console.log('[ServiceWorker] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - network first with cache fallback
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests - Let POST requests pass through
  if (request.method !== 'GET') return;

  // Skip API calls - always go to network
  if (url.pathname.startsWith('/api')) {
    return;
  }

  // For navigation requests, use network first
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache successful responses
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Return cached version or offline page
          return caches.match(request)
            .then((cached) => cached || caches.match('/offline.html'));
        })
    );
    return;
  }

  // For other assets, use cache first with network fallback
  event.respondWith(
    caches.match(request)
      .then((cached) => {
        if (cached) {
          // Return cached, but fetch fresh version in background
          fetch(request).then((response) => {
            if (response.ok) {
              caches.open(DYNAMIC_CACHE).then((cache) => {
                cache.put(request, response);
              });
            }
          }).catch(() => {});
          return cached;
        }

        // Not in cache, fetch from network
        return fetch(request)
          .then((response) => {
            if (response.ok) {
              const responseClone = response.clone();
              caches.open(DYNAMIC_CACHE).then((cache) => {
                cache.put(request, responseClone);
              });
            }
            return response;
          });
      })
  );
});

/**
 * PA-2: Handle translation API requests with caching
 * Caches successful translation responses for instant retrieval
 */
async function handleTranslationRequest(request) {
  try {
    // Clone request to read body
    const requestClone = request.clone();
    const body = await requestClone.json();
    const { texts, target_language } = body;
    
    // Create a cache key from the request
    const cacheKey = `translate:${target_language}:${texts.sort().join('|')}`;
    
    // Try to get from cache first
    const cache = await caches.open(TRANSLATION_CACHE);
    const cachedResponse = await cache.match(cacheKey);
    
    if (cachedResponse) {
      console.log('[ServiceWorker] Returning cached translation for:', target_language);
      return cachedResponse.clone();
    }
    
    // Not in cache, fetch from network
    const response = await fetch(request);
    
    if (response.ok) {
      // Cache successful responses
      const responseClone = response.clone();
      
      // Store with a custom cache key
      const cacheResponse = new Response(await responseClone.text(), {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers
      });
      
      await cache.put(cacheKey, cacheResponse);
      console.log('[ServiceWorker] Cached translation for:', target_language);
    }
    
    return response;
    
  } catch (error) {
    console.error('[ServiceWorker] Translation cache error:', error);
    // Fallback to network
    return fetch(request);
  }
}

// Handle push notifications
self.addEventListener('push', (event) => {
  const data = event.data?.json() || {};
  const title = data.title || 'MedMatch';
  const options = {
    body: data.body || 'New job matches found!',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/'
    },
    actions: [
      { action: 'view', title: 'View Jobs' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'view' || !event.action) {
    const url = event.notification.data?.url || '/';
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then((clientList) => {
        // If a window is already open, focus it
        for (const client of clientList) {
          if (client.url.includes(url) && 'focus' in client) {
            return client.focus();
          }
        }
        // Otherwise open a new window
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
    );
  }
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-applications') {
    event.waitUntil(syncApplications());
  }
});

async function syncApplications() {
  // Sync any pending offline applications when back online
  console.log('[ServiceWorker] Syncing applications...');
}
