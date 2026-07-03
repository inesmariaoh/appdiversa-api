"""
Rutas administrativas del motor de sincronizacion.
"""

from django.urls import path

from aplicaciones.sincronizacion.api.v1.admin_views import (
    ConflictosListView,
    ResolverConflictoView,
)

urlpatterns = [
    path(
        "sincronizacion/conflictos/",
        ConflictosListView.as_view(),
        name="admin-sincronizacion-conflictos",
    ),
    path(
        "sincronizacion/conflictos/<uuid:conflicto_uuid>/resolver/",
        ResolverConflictoView.as_view(),
        name="admin-sincronizacion-conflictos-resolver",
    ),
]
