"""
Rutas de la API publica del repositorio documental v1.
"""

from django.urls import path

from aplicaciones.archivos.api.v1.views import (
    ArchivoDetalleView,
    DescargarArchivoView,
    SubirArchivoView,
)

urlpatterns = [
    path("", SubirArchivoView.as_view(), name="subir-archivo"),
    path(
        "<uuid:uuid_archivo>/",
        ArchivoDetalleView.as_view(),
        name="detalle-archivo",
    ),
    path(
        "<uuid:uuid_archivo>/descargar/",
        DescargarArchivoView.as_view(),
        name="descargar-archivo",
    ),
]
