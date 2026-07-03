"""
Rutas administrativas de exportaciones bajo /api/v1/admin/.
"""

from django.urls import path

from aplicaciones.exportaciones.api.v1.admin_views import (
    AdminDescargarExportacionView,
    AdminExportarRespuestasView,
)

urlpatterns = [
    path(
        "exportaciones/respuestas/",
        AdminExportarRespuestasView.as_view(),
        name="admin-exportar-respuestas",
    ),
    path(
        "exportaciones/<uuid:uuid_exportacion>/descargar/",
        AdminDescargarExportacionView.as_view(),
        name="admin-descargar-exportacion",
    ),
]
