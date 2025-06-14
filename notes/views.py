import json
import logging
import os
import re
import zipfile

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.forms import BooleanField
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.decorators.http import require_POST

from accounts.forms import EmailRegistrationForm, EmailLoginForm
from accounts.models import LoginHistory, CustomUser
from .forms import ImportForm, ColorUpdateForm, ProfileForm
from .models import Note, Color


logger = logging.getLogger(__name__)


@login_required
def profile(request):
    if request.method == "POST":
        if "update_profile" in request.POST:
            form = ProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Your profile has been updated successfully!")
                return redirect("notes:profile")

        elif "change_password" in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, "Your password was successfully updated!")
                return redirect("notes:profile")
            else:
                messages.error(request, "Please correct the error below.")

    else:
        form = ProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    # Get login history with pagination
    login_history = LoginHistory.objects.filter(user=request.user)
    paginator = Paginator(login_history, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "form": form,
        "password_form": password_form,
        "login_history": page_obj,
    }
    return render(request, "notes/profile.html", context)


class EmailRegisterView(CreateView):
    """User registration view"""

    form_class = EmailRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("notes:login")

    def form_valid(self, form):
        print(form.cleaned_data, "form.cleaned_data+++++++++++++++++++++++++")
        # Manually set the timezone before saving
        user = form.save(commit=False)
        user.timezone = form.cleaned_data.get("timezone", "UTC")
        user.save()

        Color.create_default_color(user)
        messages.success(self.request, "Account created successfully!")
        return redirect(self.success_url)

    def form_invalid(self, form):
        print(form.errors, "form.errors===================")
        return super().form_invalid(form)


class EmailLoginView(LoginView):
    form_class = EmailLoginForm
    template_name = "registration/login.html"

    def form_valid(self, form):
        device_timezone = form.cleaned_data.get("device_timezone", "UTC")

        response = super().form_valid(form)

        LoginHistory.create_login_record(
            user=self.request.user,
            request=self.request,
            device_timezone=device_timezone,
            success=True,
        )

        messages.success(
            self.request,
            f"Welcome back, {self.request.user.first_name or self.request.user.email}!",
        )
        return response

    def form_invalid(self, form):
        """Handle failed login attempt"""
        response = super().form_invalid(form)

        # Try to get user from email if provided
        email = form.data.get("username")
        if email:
            try:
                user = CustomUser.objects.get(email=email)
                device_timezone = form.data.get("device_timezone", "UTC")

                LoginHistory.create_login_record(
                    user=user,
                    request=self.request,
                    device_timezone=device_timezone,
                    success=False,
                )
            except CustomUser.DoesNotExist:
                pass

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
    """Display note detail"""

    model = Note
    template_name = "notes/detail.html"
    context_object_name = "note"

    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user).select_related("color")


class PublicNoteListView(ListView):
    """Display public list of notes"""

    model = Note
    template_name = "notes/public_list.html"
    context_object_name = "notes"

    def get_queryset(self):
        queryset = Note.objects.filter(is_public=True)
        return queryset


class PublicNoteDetailView(DetailView):
    """Display public note detail"""

    model = Note
    template_name = "notes/public_detail.html"
    context_object_name = "note"

    def get_queryset(self):
        return Note.objects.filter(is_public=True)


class NoteCreateView(LoginRequiredMixin, CreateView):
    """Create new note or checklist"""

    model = Note
    fields = ["title", "content", "color"]
    template_name = "notes/create.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if self.request.user.is_superuser:
            form.fields["is_public"] = BooleanField(
                required=False,
                label="Public",
                initial=False,
                help_text="Make this note public",
            )
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["colors"] = Color.objects.filter(owner=self.request.user)
        context["note_type"] = self.kwargs.get("note_type", "note")
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.note_type = self.kwargs.get("note_type", "note")

        if not self.request.user.is_superuser:
            form.instance.is_public = False

        response = super().form_valid(form)
        messages.success(
            self.request, f"{form.instance.note_type.title()} created successfully!"
        )
        return response

    def get_success_url(self):
        return reverse_lazy("notes:detail", kwargs={"pk": self.object.pk})


@login_required
@require_POST
def update_note(request, pk):
    try:
        logger.debug(request.user, "----------------", pk)
        note = Note.objects.get(pk=pk, owner=request.user)
        data = json.loads(request.body)
        note.content = data.get("content", note.content)
        note.save()
        return JsonResponse({"success": True, "message": "Data updated."})
    except Note.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Data not found."}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


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
