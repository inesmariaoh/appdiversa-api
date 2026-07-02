"""
Rutas de la API publica de contenidos v1.
"""

from django.urls import path

from aplicaciones.contenidos.api.v1.views import ConfiguracionInterfazView

urlpatterns = [
    path(
        "configuracion/",
        ConfiguracionInterfazView.as_view(),
        name="interfaz-configuracion",
    ),
]
