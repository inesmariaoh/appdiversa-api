"""
Rutas administrativas de catalogos parametrizables.
"""

from django.urls import path

from aplicaciones.catalogos.api.v1.admin_views import (
    CatalogoAdminDetalleView,
    CatalogosAdminListCreateView,
    ItemCatalogoAdminDetalleView,
    ItemsCatalogoAdminListCreateView,
)

urlpatterns = [
    path(
        "catalogos/",
        CatalogosAdminListCreateView.as_view(),
        name="admin-catalogos-list",
    ),
    path(
        "catalogos/<int:catalogo_id>/",
        CatalogoAdminDetalleView.as_view(),
        name="admin-catalogos-detalle",
    ),
    path(
        "catalogos/<int:catalogo_id>/items/",
        ItemsCatalogoAdminListCreateView.as_view(),
        name="admin-catalogos-items",
    ),
    path(
        "catalogos/items/<int:item_id>/",
        ItemCatalogoAdminDetalleView.as_view(),
        name="admin-catalogos-item-detalle",
    ),
]
