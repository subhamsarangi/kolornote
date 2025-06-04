from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def manifest_view(request):
    """PWA manifest"""
    manifest = {
        "name": "Kolornote",
        "short_name": "Notes",
        "description": "A PWA for managing notes and checklists",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#007bff",
        "icons": [
            {
                "src": "/static/icons/icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
            },
            {
                "src": "/static/icons/icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
            },
        ],
    }
    return JsonResponse(manifest)


def service_worker_view(request):
    """Service worker for PWA"""
    sw_content = """
const CACHE_NAME = 'kolornote-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});
"""
    return HttpResponse(sw_content, content_type="application/javascript")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home),
    path("notes/", include("notes.urls")),
    path("manifest.json", manifest_view, name="manifest"),
    path("sw.js", service_worker_view, name="service_worker"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
