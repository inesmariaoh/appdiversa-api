"""
Pruebas de utilidades para URLs de archivos media.
"""

from django.test import RequestFactory, TestCase

from aplicaciones.comun.utilidades_media import (
    construir_url_absoluta_desde_solicitud,
    normalizar_url_relativa,
)


class UtilidadesMediaTests(TestCase):
    """Pruebas de normalizacion y construccion de URLs media."""

    def test_normalizar_url_relativa_sin_barra_inicial(self) -> None:
        self.assertEqual(
            normalizar_url_relativa("media/formularios/portadas/logo.png"),
            "/media/formularios/portadas/logo.png",
        )

    def test_construir_url_absoluta_desde_solicitud(self) -> None:
        factory = RequestFactory()
        solicitud = factory.get("/api/v1/formularios/disponibles/")
        url = construir_url_absoluta_desde_solicitud(
            "media/formularios/portadas/logo.png",
            solicitud,
        )
        self.assertEqual(
            url,
            "http://testserver/media/formularios/portadas/logo.png",
        )
