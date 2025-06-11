from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, LoginHistory


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email",)
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "timezone")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "login_time",
        "ip_address",
        "device_timezone",
        "ip_country",
        "ip_city",
        "login_successful",
    )
    list_filter = ("login_successful", "device_timezone", "ip_country", "login_time")
    search_fields = ("user__email", "ip_address", "ip_country", "ip_city")
    readonly_fields = ("login_time",)
    ordering = ("-login_time",)

    def has_add_permission(self, request):
        return False  # Prevent manual addition

    def has_change_permission(self, request, obj=None):
        return False  # Make read-only
