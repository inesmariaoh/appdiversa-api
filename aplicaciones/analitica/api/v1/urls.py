"""
Rutas de la API de analitica v1.
"""

from django.urls import path

from aplicaciones.analitica.api.v1.views import ListarRespuestasAnaliticasView

urlpatterns = [
    path(
        "respuestas/",
        ListarRespuestasAnaliticasView.as_view(),
        name="listar-respuestas-analiticas",
    ),
]
