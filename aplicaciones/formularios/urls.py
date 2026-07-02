"""
Rutas de la API de formularios.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.formularios.api.v1.urls")),
]
