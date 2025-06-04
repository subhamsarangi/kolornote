from django.contrib import admin
from .models import Note, Color


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "note_type", "color", "created_at"]
    list_filter = ["note_type", "created_at", "color"]
    search_fields = ["title", "content"]
    readonly_fields = ["created_at", "modified_at"]


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ["name", "hex_value", "owner", "is_default"]
    list_filter = ["is_default", "created_at"]
    search_fields = ["name", "hex_value"]
