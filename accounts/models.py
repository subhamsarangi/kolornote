import threading

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from django.db import transaction
from django.utils import timezone
import pytz
import requests


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    timezone = models.CharField(
        max_length=50,
        default="UTC",
        choices=[(tz, tz) for tz in pytz.all_timezones],
        help_text="User's timezone",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_local_time(self, utc_datetime=None):
        """Convert UTC datetime to user's local timezone"""
        if utc_datetime is None:
            utc_datetime = timezone.now()

        user_tz = pytz.timezone(self.timezone)
        return utc_datetime.astimezone(user_tz)


class LoginHistory(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="login_history"
    )
    login_time = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)

    # Device timezone
    device_timezone = models.CharField(max_length=50, default="UTC")

    # IP-based timezone & other info
    ip_country = models.CharField(max_length=100, blank=True)
    ip_city = models.CharField(max_length=100, blank=True)
    ip_timezone = models.CharField(max_length=50, blank=True)

    login_successful = models.BooleanField(default=True)

    class Meta:
        ordering = ["-login_time"]
        verbose_name = "Login History"
        verbose_name_plural = "Login Histories"

    def __str__(self):
        return f"{self.user.email} - {self.login_time.strftime('%Y-%m-%d %H:%M:%S')}"

    @classmethod
    def create_login_record(cls, user, request, device_timezone=None, success=True):
        """Create a login history record"""
        ip_address = cls.get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]

        login_record = cls.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            device_timezone=device_timezone or "UTC",
            login_successful=success,
        )

        # Get IP info asynchronously
        def update_ip_info():
            print("thread job -----------------------------")
            try:
                location_info = cls.get_ip_location(ip_address)
                if location_info:
                    # Use select_for_update to prevent race conditions
                    with transaction.atomic():
                        record = cls.objects.select_for_update().get(id=login_record.id)
                        record.ip_country = location_info.get("country", "")
                        record.ip_city = location_info.get("city", "")
                        record.ip_timezone = location_info.get("timezone", "")
                        record.save()
            except Exception as e:
                # Log the error but don't fail the login
                print(f"Error getting IP location: {e}")

        # Start background thread
        thread = threading.Thread(target=update_ip_info)
        thread.daemon = True
        thread.start()

        return login_record

    @staticmethod
    def get_client_ip(request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    @staticmethod
    def get_ip_location(ip_address):
        """Get location info from IP address using a free service"""
        if ip_address in ["127.0.0.1", "localhost"]:
            return {"country": "Local", "city": "Local", "timezone": "UTC"}

        try:
            # Free service, no API key
            response = requests.get(
                f"http://ip-api.com/json/{ip_address}?fields=country,city,timezone",
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "country": data.get("country", ""),
                    "city": data.get("city", ""),
                    "timezone": data.get("timezone", ""),
                }
        except Exception as e:
            print(f"Error fetching IP location: {e}")

        return None
