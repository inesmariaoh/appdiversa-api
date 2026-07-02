"""
Rutas del modulo de repositorio documental.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.archivos.api.v1.urls")),
]
