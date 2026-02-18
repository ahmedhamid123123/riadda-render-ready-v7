import os
from django.core.asgi import get_asgi_application

# Do not auto-switch settings here.
# Settings must be explicitly provided by the environment (Render, Docker, CI).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_asgi_application()
