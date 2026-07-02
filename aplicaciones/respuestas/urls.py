"""
Rutas de la API de respuestas.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.respuestas.api.v1.urls")),
]
