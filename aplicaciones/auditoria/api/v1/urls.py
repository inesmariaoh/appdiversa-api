"""
Rutas de la API de consulta de auditoria v1.
"""

from django.urls import path

from aplicaciones.auditoria.api.v1.views import (
    RegistroAuditoriaDetalleView,
    RegistrosAuditoriaListView,
)

urlpatterns = [
    path(
        "registros/",
        RegistrosAuditoriaListView.as_view(),
        name="auditoria-registros-list",
    ),
    path(
        "registros/<int:registro_id>/",
        RegistroAuditoriaDetalleView.as_view(),
        name="auditoria-registro-detalle",
    ),
]
