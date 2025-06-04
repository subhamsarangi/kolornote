from .base import *

DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(",")

STATIC_ROOT = BASE_DIR / "static"
MEDIA_ROOT = "/home/kolornote/kolornote/media/"  # BASE_DIR / "media"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "OPTIONS": {
            "sql_mode": "traditional",
            "charset": "utf8mb4",
        },
    }
}
