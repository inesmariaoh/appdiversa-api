"""
Rutas del modulo de analitica.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.analitica.api.v1.urls")),
]
