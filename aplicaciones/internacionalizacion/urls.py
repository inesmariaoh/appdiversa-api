"""
Rutas del modulo de internacionalizacion.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.internacionalizacion.api.v1.urls")),
]
