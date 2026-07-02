"""
Rutas de la API de auditoria.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.auditoria.api.v1.urls")),
]
