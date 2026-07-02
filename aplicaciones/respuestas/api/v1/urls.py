"""
Rutas de la API de respuestas v1.
"""

from django.urls import path

from aplicaciones.respuestas.api.v1.views import GuardarRespuestaView

urlpatterns = [
    path("", GuardarRespuestaView.as_view(), name="guardar-respuesta"),
]
