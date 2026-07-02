"""
Rutas de la API publica de catalogos v1.
"""

from django.urls import path

from aplicaciones.catalogos.api.v1.views import (
    ListarCatalogosView,
    ListarHijosItemCatalogoView,
    ListarItemsCatalogoView,
)

urlpatterns = [
    path(
        "",
        ListarCatalogosView.as_view(),
        name="listar-catalogos",
    ),
    path(
        "<str:codigo_catalogo>/items/",
        ListarItemsCatalogoView.as_view(),
        name="listar-items-catalogo",
    ),
    path(
        "<str:codigo_catalogo>/items/<str:codigo_item>/hijos/",
        ListarHijosItemCatalogoView.as_view(),
        name="listar-hijos-item-catalogo",
    ),
]
