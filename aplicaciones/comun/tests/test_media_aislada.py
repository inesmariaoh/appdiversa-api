"""
Pruebas de aislamiento del almacenamiento media durante tests.
"""

from pathlib import Path

from django.conf import settings
from django.test import TestCase

from aplicaciones.archivos.constantes import OrigenArchivo, TipoArchivo
from aplicaciones.archivos.servicios import guardar_archivo

CONTENIDO_PNG_MINIMO = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


class MediaAisladaTests(TestCase):
    """Verifica que los tests no escriban en media/ del proyecto."""

    def test_media_root_no_es_el_directorio_del_proyecto(self) -> None:
        media_proyecto = Path(settings.BASE_DIR) / "media"
        self.assertNotEqual(
            Path(settings.MEDIA_ROOT).resolve(),
            media_proyecto.resolve(),
        )

    def test_guardar_archivo_usa_media_root_aislado(self) -> None:
        archivo = guardar_archivo(
            contenido=CONTENIDO_PNG_MINIMO,
            nombre_original="aislado.png",
            mime_type="image/png",
            tipo_archivo=TipoArchivo.IMAGEN,
            origen=OrigenArchivo.OTRO,
        )
        ruta_absoluta = Path(settings.MEDIA_ROOT) / archivo.ruta_relativa
        media_proyecto = Path(settings.BASE_DIR) / "media" / archivo.ruta_relativa

        self.assertTrue(ruta_absoluta.exists())
        self.assertFalse(media_proyecto.exists())
