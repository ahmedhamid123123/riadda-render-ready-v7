"""
WSGI config for apps.core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Default safely on platforms like Render where a settings module might not be
# explicitly set. Local dev can keep using config.settings.dev.
default_settings = "config.settings.prod" if (os.environ.get("RENDER") or os.environ.get("DJANGO_ENV") == "production") else "config.settings.dev"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings)

application = get_wsgi_application()
