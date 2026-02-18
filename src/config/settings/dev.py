from .base import *

DEBUG = False  # Set to False to test error pages in development

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["http://localhost:8000"]

# أخفّف القيود للتطوير فقط
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Throttling أخف للتجربة
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
