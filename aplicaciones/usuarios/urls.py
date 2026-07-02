"""
Rutas del modulo de usuarios.
"""

from django.urls import include, path

urlpatterns = [
    path("auth/", include("aplicaciones.usuarios.api.v1.urls_auth")),
]
