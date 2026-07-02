"""
Rutas de la API publica de internacionalizacion v1.
"""

from django.urls import path

from aplicaciones.internacionalizacion.api.v1.views import ListarTraduccionesView

urlpatterns = [
    path(
        "traducciones/",
        ListarTraduccionesView.as_view(),
        name="listar-traducciones",
    ),
]
