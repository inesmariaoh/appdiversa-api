"""
Configuracion de la aplicacion Celery para tareas asincronas.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appdiversa_core.settings.local")

app = Celery("appdiversa")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
