"""
Rutas del modulo de exportaciones transversal.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.exportaciones.api.v1.urls")),
]
