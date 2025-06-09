from .base import *

DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(",")

MEDIA_ROOT = "/home/kolornote/kolornote/media/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"


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
