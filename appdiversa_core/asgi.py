"""
Punto de entrada ASGI para despliegue con servidores compatibles.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appdiversa_core.settings.local")

application = get_asgi_application()
