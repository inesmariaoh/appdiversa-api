"""
Rutas de la API de sesiones anonimas.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.sesiones_anonimas.api.v1.urls")),
]
