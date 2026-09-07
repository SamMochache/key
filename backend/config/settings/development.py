from .base import *

# Local development defaults. Production settings remain strict.
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

# Django Admin and other built-in templates reference static assets during
# local development. Use Django's normal static storage so `runserver` does
# not require a production `collectstatic` manifest to exist.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
