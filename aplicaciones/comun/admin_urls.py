"""
Rutas administrativas unificadas bajo /api/v1/admin/.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("aplicaciones.usuarios.api.v1.urls_admin")),
    path("", include("aplicaciones.formularios.urls_admin")),
    path("", include("aplicaciones.exportaciones.urls_admin")),
    path("", include("aplicaciones.sincronizacion.urls_admin")),
]
