from pathlib import Path
import os
import secrets
import logging

import dj_database_url

logger = logging.getLogger(__name__)

# Optionally load a local .env file for development (python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[3] / ".env")
except Exception as exc:
    logger.debug("python-dotenv not available or failed to load: %s", exc)

# Project root (where manage.py lives)
BASE_DIR = Path(__file__).resolve().parents[3]

# ---------------------
# Core Security
# ---------------------
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

if not SECRET_KEY:
    if DEBUG:
        # Development fallback: generate a random key to avoid committing a hardcoded secret
        SECRET_KEY = secrets.token_urlsafe(50)
    else:
        raise RuntimeError("DJANGO_SECRET_KEY environment variable is required in production")

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

# HMAC key used to sign receipt snapshots (tamper-evident).
RECEIPT_HMAC_KEY = os.environ.get("DJANGO_RECEIPT_HMAC_KEY")
if not RECEIPT_HMAC_KEY:
    if DEBUG:
        # Dev default only.
        RECEIPT_HMAC_KEY = SECRET_KEY
    else:
        raise RuntimeError("DJANGO_RECEIPT_HMAC_KEY environment variable is required in production")

# ---------------------
# Applications
# ---------------------
INSTALLED_APPS = [
    # Local apps
    "apps.accounts",
    "apps.sales",
    "apps.billing",
    "apps.commissions",
    "apps.core",

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "csp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    "csp.middleware.CSPMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.accounts.context_processors.system_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------
# Database
# ---------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

if DATABASE_URL:
    # Render Postgres usually uses SSL when DEBUG=False
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=int(os.environ.get("DJANGO_DB_CONN_MAX_AGE", "600")),
            ssl_require=(
                os.environ.get("DJANGO_DB_SSL_REQUIRE", "True").lower() == "true"
                if not DEBUG
                else False
            ),
        )
    }
else:
    DB_ENGINE = os.environ.get("DJANGO_DB_ENGINE", "django.db.backends.sqlite3")
    if "postgres" in DB_ENGINE or DB_ENGINE.endswith("postgresql"):
        DATABASES = {
            "default": {
                "ENGINE": os.environ.get("DJANGO_DB_ENGINE", "django.db.backends.postgresql"),
                "NAME": os.environ.get("DJANGO_DB_NAME", "riadda"),
                "USER": os.environ.get("DJANGO_DB_USER", "riadda_user"),
                "PASSWORD": os.environ.get("DJANGO_DB_PASS", ""),
                "HOST": os.environ.get("DJANGO_DB_HOST", "localhost"),
                "PORT": os.environ.get("DJANGO_DB_PORT", "5432"),
                "CONN_MAX_AGE": int(os.environ.get("DJANGO_DB_CONN_MAX_AGE", "600")),
            }
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": os.environ.get("DJANGO_DB_NAME", str(BASE_DIR / "db.sqlite3")),
            }
        }

AUTH_USER_MODEL = "accounts.User"

# ---------------------
# Auth / Passwords
# ---------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------
# I18N
# ---------------------
LANGUAGE_CODE = "ar"
TIME_ZONE = "Asia/Baghdad"
USE_I18N = True
USE_TZ = True

# ---------------------
# Static / Media
# ---------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------
# Proxy / Render correctness
# ---------------------
# Render terminates TLS at the proxy, Django should treat request as HTTPS via header.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# ---------------------
# Security hardening — enabled when DEBUG is False
# ---------------------
if not DEBUG:
    # Cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get("DJANGO_SESSION_COOKIE_SAMESITE", "Lax")
    CSRF_COOKIE_SAMESITE = os.environ.get("DJANGO_CSRF_COOKIE_SAMESITE", "Lax")

    # HTTPS redirect
    SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "True").lower() == "true"

    # HSTS gradual
    SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "3600"))
    SECURE_HSTS_PRELOAD = os.environ.get("DJANGO_SECURE_HSTS_PRELOAD", "True").lower() == "true"
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", "True").lower() == "true"

    # Headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_REFERRER_POLICY = os.environ.get("DJANGO_SECURE_REFERRER_POLICY", "strict-origin-when-cross-origin")

# Trusted origins (needed behind proxies / custom domains)
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

# Upload limits (optional hardening)
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("DJANGO_DATA_UPLOAD_MAX_MEMORY_SIZE", str(5 * 1024 * 1024)))  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("DJANGO_FILE_UPLOAD_MAX_MEMORY_SIZE", str(5 * 1024 * 1024)))  # 5MB

# ---------------------
# DRF / JWT / Schema
# ---------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    # IMPORTANT: day-based throttles are weak against brute force.
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.environ.get("DRF_THROTTLE_ANON", "60/hour"),
        "user": os.environ.get("DRF_THROTTLE_USER", "1000/hour"),
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Riadda API",
    "DESCRIPTION": "POS + Admin Web API",
    "VERSION": "1.0.0",
}

# ---------------------
# django-csp 4.x (Correct way)
# ---------------------
# Keep it strict by default; only add sources you truly need.
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'",),
        "style-src": ("'self'",),  # add "'unsafe-inline'" only if required
        "img-src": ("'self'", "data:"),
        "font-src": ("'self'", "data:"),
        "connect-src": ("'self'",),
        "base-uri": ("'self'",),
        "frame-ancestors": ("'none'",),
    }
}

# If you REALLY must allow inline styles (not recommended), use:
# CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
