"""
Rutas de la API publica de notificaciones v1.
"""

from django.urls import path

from aplicaciones.notificaciones.api.v1.views import (
    DetalleNotificacionView,
    ListarNotificacionesView,
    ProbarNotificacionView,
)

urlpatterns = [
    path("", ListarNotificacionesView.as_view(), name="listar-notificaciones"),
    path("probar/", ProbarNotificacionView.as_view(), name="probar-notificacion"),
    path(
        "<uuid:uuid_notificacion>/",
        DetalleNotificacionView.as_view(),
        name="detalle-notificacion",
    ),
]
