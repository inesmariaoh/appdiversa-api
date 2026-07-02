"""
Rutas de la API de contenidos.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.contenidos.api.v1.urls")),
]
