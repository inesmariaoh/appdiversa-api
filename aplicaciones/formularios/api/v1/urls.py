"""
Rutas de la API publica de formularios v1.
"""

from django.urls import path

from aplicaciones.formularios.api.v1.views import (
    FormularioEstructuraView,
    FormulariosDisponiblesView,
)

urlpatterns = [
    path(
        "disponibles/",
        FormulariosDisponiblesView.as_view(),
        name="formularios-disponibles",
    ),
    path(
        "<uuid:uuid_formulario>/estructura/",
        FormularioEstructuraView.as_view(),
        name="formulario-estructura",
    ),
]
