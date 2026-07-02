"""
Rutas de la API de sincronizacion.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.sincronizacion.api.v1.urls")),
]
