"""
Punto de entrada WSGI para despliegue con servidores compatibles.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appdiversa_core.settings.local")

application = get_wsgi_application()
