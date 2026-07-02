"""
Rutas de la API v1 de sincronizacion.
"""

from django.urls import path

from aplicaciones.sincronizacion.api.v1.views import SincronizarBatchView

urlpatterns = [
    path("", SincronizarBatchView.as_view(), name="sincronizar-batch"),
]
