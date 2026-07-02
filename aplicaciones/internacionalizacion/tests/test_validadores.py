"""
Pruebas de validadores de archivos multimedia.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from aplicaciones.internacionalizacion.validadores import (
    EXTENSIONES_AUDIO,
    EXTENSIONES_VIDEO,
    MensajesValidacionArchivoMultimedia,
    validar_archivo_multimedia,
    validar_extension_archivo,
)


class ValidadoresArchivoMultimediaTests(TestCase):
    """Pruebas de validacion de extensiones de archivos multimedia."""

    def test_archivo_audio_extension_no_permitida_genera_error(self) -> None:
        with self.assertRaises(ValidationError) as contexto:
            validar_archivo_multimedia(
                "audio.exe",
                EXTENSIONES_AUDIO,
                MensajesValidacionArchivoMultimedia.EXTENSION_AUDIO_NO_PERMITIDA,
            )
        self.assertIn(
            MensajesValidacionArchivoMultimedia.EXTENSION_AUDIO_NO_PERMITIDA,
            str(contexto.exception),
        )

    def test_archivo_video_extension_permitida_pasa_validacion(self) -> None:
        self.assertTrue(
            validar_extension_archivo("video.mp4", EXTENSIONES_VIDEO),
        )
