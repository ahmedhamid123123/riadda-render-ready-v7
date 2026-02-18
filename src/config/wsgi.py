import os
from django.core.wsgi import get_wsgi_application

# DO NOT auto-switch settings here.
# The environment (Render / Docker / CI) must explicitly define DJANGO_SETTINGS_MODULE.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()
