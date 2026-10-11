"""
Django settings for the Employee Management System backend.

All secrets and environment-specific values are read from environment
variables (optionally loaded from a `.env` file in the project root).
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # .../backend
PROJECT_ROOT = BASE_DIR.parent

# Variables already present in the real environment always win over .env.
load_dotenv(PROJECT_ROOT / ".env")


def env(name, default=None, required=False):
    value = os.environ.get(name, default)
    if required and (value is None or str(value).strip() == ""):
        raise ImproperlyConfigured(f"Missing required environment variable: {name}")
    return value


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    return [item.strip() for item in env(name, default).split(",") if item.strip()]


# --- Core -------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", required=True)
DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "corsheaders",
    "rest_framework",
    "employees",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Endpoints are defined without trailing slashes; never redirect API calls.
APPEND_SLASH = False

# --- Database (PostgreSQL) --------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", required=True),
        "USER": env("DB_USER", required=True),
        "PASSWORD": env("DB_PASSWORD", required=True),
        "HOST": env("DB_HOST", "localhost"),
        "PORT": env("DB_PORT", "5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Internationalisation ---------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = env("DJANGO_TIME_ZONE", "Asia/Kolkata")
USE_I18N = False
USE_TZ = True

# --- CORS: only the configured frontend origin is allowed -------------------
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [env("FRONTEND_ORIGIN", required=True).rstrip("/")]

# --- Django REST Framework --------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    # The assignment defines no authentication requirement.
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "UNAUTHENTICATED_USER": None,
    "EXCEPTION_HANDLER": "employees.exceptions.custom_exception_handler",
}

# --- Logging ----------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
