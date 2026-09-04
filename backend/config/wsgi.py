"""WSGI config for the Key Django project."""

import os

from django.core.wsgi import get_wsgi_application

# Vercel runs the production configuration; manage.py still defaults to development.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
