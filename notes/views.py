import os
import re
import zipfile
import logging
from io import BytesIO

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views import View

from .models import Note, Color
from .forms import ImportForm, ColorUpdateForm


logger = logging.getLogger(__name__)


class RegisterView(CreateView):
    """User registration view"""

    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("notes:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        Color.create_default_color(self.object)
        messages.success(self.request, "Account created successfully!")
        return response


class NoteListView(LoginRequiredMixin, ListView):
    """Display filterable list of notes"""

    model = Note
    template_name = "notes/list.html"
    context_object_name = "notes"
    paginate_by = 20

    def get_queryset(self):
        queryset = Note.objects.filter(owner=self.request.user).select_related("color")

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        note_type = self.request.GET.get("type")
        if note_type in ["note", "checklist"]:
            queryset = queryset.filter(note_type=note_type)

        color_id = self.request.GET.get("color")
        if color_id:
            try:
                queryset = queryset.filter(color_id=int(color_id))
            except (ValueError, TypeError):
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["colors"] = Color.objects.filter(owner=self.request.user)
        context["search"] = self.request.GET.get("search", "")
        context["selected_type"] = self.request.GET.get("type", "")
        context["selected_color"] = self.request.GET.get("color", "")
        return context


class NoteDetailView(LoginRequiredMixin, DetailView):
    """Display single note detail"""

    model = Note
    template_name = "notes/detail.html"
    context_object_name = "note"

    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user).select_related("color")


class ImportNotesView(LoginRequiredMixin, View):
    """Handle zip file import of notes"""

    def get(self, request):
        form = ImportForm()
        return self.render_form(request, form)

    def post(self, request):
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                self.process_zip_file(request, form.cleaned_data["zip_file"])
                messages.success(request, "Notes imported successfully!")
                return redirect("notes:list")
            except Exception as e:
                logger.error(f"Import error for user {request.user.id}: {str(e)}")
                messages.error(
                    request, "Error importing notes. Please check your file format."
                )

        return self.render_form(request, form)

    def render_form(self, request, form):
        from django.shortcuts import render

        return render(request, "notes/import.html", {"form": form})

    def process_zip_file(self, request, zip_file):
        """Process uploaded zip file and create notes"""
        zip_name = os.path.splitext(zip_file.name)[0]

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            with transaction.atomic():
                color = Color.objects.create(
                    owner=request.user,
                    name=zip_name,
                    hex_value=Color.generate_random_hex(),
                )

                for file_info in zip_ref.infolist():
                    if file_info.filename.endswith(".txt") and not file_info.is_dir():
                        content = zip_ref.read(file_info).decode(
                            "utf-8", errors="ignore"
                        )
                        title = os.path.splitext(os.path.basename(file_info.filename))[
                            0
                        ]
                        note_type = self.detect_note_type(content)

                        Note.objects.create(
                            owner=request.user,
                            title=title,
                            content=content,
                            note_type=note_type,
                            color=color,
                        )

    def detect_note_type(self, content):
        """Detect if content is checklist or note"""
        checklist_pattern = r"^\s*\[(V| )\]\s+"
        for line in content.split("\n"):
            if line.strip() and re.match(checklist_pattern, line):
                return "checklist"
        return "note"


class ColorListView(LoginRequiredMixin, ListView):
    """Display list of colors"""

    model = Color
    template_name = "notes/colors.html"
    context_object_name = "colors"

    def get_queryset(self):
        return Color.objects.filter(owner=self.request.user).order_by("name")


class ColorUpdateView(LoginRequiredMixin, UpdateView):
    """Update color name"""

    model = Color
    form_class = ColorUpdateForm
    template_name = "notes/color_update.html"
    success_url = reverse_lazy("notes:colors")

    def get_queryset(self):
        return Color.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Color updated successfully!")
        return super().form_valid(form)


def manifest_view(request):
    """PWA manifest"""
    manifest = {
        "name": "Notes PWA",
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
const CACHE_NAME = 'notes-pwa-v1';
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
