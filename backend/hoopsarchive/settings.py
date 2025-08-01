"""
Minimal Django settings scaffold for HoopsArchive.

Traceability:
- docs/specs/gherkin/bdd-duckdb_ingest_api_ui.md
  Section 3) API Expectations (Players and Play-by-Play endpoints)

This is a minimal, non-functional settings placeholder to enable imports in Red phase.
No actual Django runtime configuration is guaranteed here.
"""

import os
from pathlib import Path

import sys
# Base directory (placeholder)


BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Development-friendly defaults
DEBUG = True
SECRET_KEY = "stub-secret-key-not-for-production"
ALLOWED_HOSTS: list[str] = ["*"]

# Installed apps (DRF not included yet; to be added during Red/Green)
INSTALLED_APPS: list[str] = [
    # "django.contrib.admin",
    # "django.contrib.auth",
    # "django.contrib.contenttypes",
    # "django.contrib.sessions",
    # "django.contrib.messages",
    # "django.contrib.staticfiles",
    "rest_framework",  # Enabled for DRF APIs
    "players",  # app scaffold
]

MIDDLEWARE: list[str] = [
    # Placeholder middleware list
]

ROOT_URLCONF = "hoopsarchive.urls"

TEMPLATES: list[dict] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [],
        },
    }
]

WSGI_APPLICATION = "hoopsarchive.wsgi.application"  # Not provided; placeholder reference

# Database - placeholder SQLite config (no migrations required at this time)
DATABASES: dict = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db.sqlite3"),
    }
}

# REST Framework placeholders (to be set by Red phase)
REST_FRAMEWORK: dict = {
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    # "PAGE_SIZE": 50,
}

# Internationalization placeholders
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"