"""
Inicializacion del paquete principal.
Expone la aplicacion Celery para el registro de tareas compartidas.
"""

from appdiversa_core.celery import app as celery_app

__all__ = ("celery_app",)
