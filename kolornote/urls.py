from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from django.shortcuts import render


def home(request):
    return render(request, "home.html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home),
    path("notes/", include("notes.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
