"""
Rutas del modulo de notificaciones transversal.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.notificaciones.api.v1.urls")),
]
