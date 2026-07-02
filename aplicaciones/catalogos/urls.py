"""
Rutas del modulo de catalogos parametrizables.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.catalogos.api.v1.urls")),
]
