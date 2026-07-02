"""
Rutas de la API publica de exportaciones v1.
"""

from django.urls import path

from aplicaciones.exportaciones.api.v1.views import (
    DetalleExportacionView,
    ExportarAnaliticaView,
    ExportarCatalogosView,
    ExportarRespuestasView,
)

urlpatterns = [
    path(
        "respuestas/",
        ExportarRespuestasView.as_view(),
        name="exportar-respuestas",
    ),
    path(
        "catalogos/",
        ExportarCatalogosView.as_view(),
        name="exportar-catalogos",
    ),
    path(
        "analitica/",
        ExportarAnaliticaView.as_view(),
        name="exportar-analitica",
    ),
    path(
        "<uuid:uuid_exportacion>/",
        DetalleExportacionView.as_view(),
        name="detalle-exportacion",
    ),
]
