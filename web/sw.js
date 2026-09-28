const CORE='aw139-core-v2',CHARTS='aw139-charts-v1';
const FILES=['./','./index.html','./wat-data.js','./distance-data.js','./offshore-data.js','./source-catalog.js','./engine.js','./app.js','./pwa.js','./manifest.webmanifest','./icons/icon-192.png','./icons/icon-512.png','./icons/apple-touch-icon.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CORE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('aw139-')&&k!==CORE&&k!==CHARTS).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(u.origin!==self.location.origin||e.request.method!=='GET')return;e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(r=>{if(r.ok&&u.pathname.includes('/charts/')){const copy=r.clone();e.waitUntil(caches.open(CHARTS).then(c=>c.put(e.request,copy)));}return r;})));});
