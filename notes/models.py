import secrets

from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings


User = settings.AUTH_USER_MODEL


class Color(models.Model):
    """Represents a color with hex value and optional name"""

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="colors")
    name = models.CharField(max_length=100, blank=True)
    hex_value = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(regex=r"^#[0-9A-Fa-f]{6}$", message="Invalid hex color")
        ],
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["owner", "hex_value"]

    def __str__(self):
        return f"{self.name or 'Unnamed'} ({self.hex_value})"

    @classmethod
    def create_default_color(cls, user):
        """Create default white color for user"""
        return cls.objects.create(
            owner=user, name="Default", hex_value="#eeeeee", is_default=True
        )

    @classmethod
    def generate_random_hex(cls):
        """Generate random hex color"""
        return f"#{secrets.token_hex(3)}"


class Note(models.Model):
    """Represents a note or checklist"""

    TYPE_CHOICES = [
        ("note", "Note"),
        ("checklist", "Checklist"),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=200)
    content = models.TextField()
    note_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="note")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name="notes")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["-modified_at"]

    def __str__(self):
        return self.title
