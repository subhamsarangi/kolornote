from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "notes"


urlpatterns = [
    path("", views.NoteListView.as_view(), name="list"),
    path("note/<int:pk>/", views.NoteDetailView.as_view(), name="detail"),
    path("import/", views.ImportNotesView.as_view(), name="import"),
    path("colors/", views.ColorListView.as_view(), name="colors"),
    path(
        "colors/<int:pk>/update/", views.ColorUpdateView.as_view(), name="color_update"
    ),
    path("register/", views.EmailRegisterView.as_view(), name="register"),
    path("login/", views.EmailLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("manifest.json", views.manifest_view, name="manifest"),
    path("sw.js", views.service_worker_view, name="service_worker"),
]
