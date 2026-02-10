from .base import *  # noqa
import os

DEBUG = False

# -------------------------
# Proxy / Render (important)
# -------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# -------------------------
# HTTPS & Cookies
# -------------------------
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "True").lower() == "true"

SESSION_COOKIE_SECURE = os.environ.get("DJANGO_SESSION_COOKIE_SECURE", "True").lower() == "true"
CSRF_COOKIE_SECURE = os.environ.get("DJANGO_CSRF_COOKIE_SECURE", "True").lower() == "true"

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = os.environ.get("DJANGO_SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = os.environ.get("DJANGO_CSRF_COOKIE_SAMESITE", "Lax")

# -------------------------
# HSTS (gradual by default)
# -------------------------
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "3600"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", "True").lower() == "true"
SECURE_HSTS_PRELOAD = os.environ.get("DJANGO_SECURE_HSTS_PRELOAD", "True").lower() == "true"

# -------------------------
# Security headers
# -------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = os.environ.get(
    "DJANGO_SECURE_REFERRER_POLICY",
    "strict-origin-when-cross-origin"
)

# Note: SECURE_BROWSER_XSS_FILTER is obsolete in modern browsers,
# but leaving it doesn't usually hurt if you already had it.
SECURE_BROWSER_XSS_FILTER = True

# -------------------------
# Password hashers
# -------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# -------------------------
# CSRF trusted origins (behind proxy/custom domain)
# -------------------------
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

# -------------------------
# Upload limits
# -------------------------
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("DJANGO_DATA_UPLOAD_MAX_MEMORY_SIZE", str(5 * 1024 * 1024)))
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("DJANGO_FILE_UPLOAD_MAX_MEMORY_SIZE", str(5 * 1024 * 1024)))

# -------------------------
# DRF: keep JWT + add throttling
# IMPORTANT: don't overwrite REST_FRAMEWORK fully, merge instead.
# -------------------------
REST_FRAMEWORK = dict(REST_FRAMEWORK)  # from base.py

# keep JWT; optionally add SessionAuth for admin web browsing if you use it
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
    "rest_framework_simplejwt.authentication.JWTAuthentication",
    "rest_framework.authentication.SessionAuthentication",
)

REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = (
    "rest_framework.permissions.IsAuthenticated",
)

REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = [
    "rest_framework.throttling.AnonRateThrottle",
    "rest_framework.throttling.UserRateThrottle",
]

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
    # hour-based throttles are more meaningful vs brute force
    "anon": os.environ.get("DRF_THROTTLE_ANON", "100/hour"),
    "user": os.environ.get("DRF_THROTTLE_USER", "1000/hour"),
}

# If you have login/otp endpoints, apply scoped throttling in those views:
# throttle_scope = "login" then add:
# REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login"] = os.environ.get("DRF_THROTTLE_LOGIN", "20/hour")

# -------------------------
# CSP (django-csp 4.x) - strict defaults
# Adjust only if you really need external CDNs.
# -------------------------
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
