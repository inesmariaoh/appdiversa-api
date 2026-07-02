"""
Pruebas de modelos de internacionalizacion.
"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from aplicaciones.internacionalizacion.constantes import DireccionTexto
from aplicaciones.internacionalizacion.models import (
    Idioma,
    MensajesValidacionIdioma,
    TraduccionContenido,
)


class IdiomaModelTests(TestCase):
    """Pruebas del modelo Idioma."""

    def test_crear_idioma(self) -> None:
        idioma = Idioma.objects.create(
            codigo_iso="en",
            nombre="Ingles",
            nombre_nativo="English",
            direccion_texto=DireccionTexto.LTR,
        )
        self.assertEqual(idioma.codigo_iso, "en")
        self.assertTrue(idioma.esta_activo)

    def test_no_duplicar_codigo_iso(self) -> None:
        Idioma.objects.create(
            codigo_iso="pt",
            nombre="Portugues",
            nombre_nativo="Portugues",
        )
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Idioma.objects.create(
                    codigo_iso="pt",
                    nombre="Portugues duplicado",
                    nombre_nativo="Portugues",
                )

    def test_solo_un_idioma_predeterminado(self) -> None:
        Idioma.objects.create(
            codigo_iso="es",
            nombre="Espanol",
            nombre_nativo="Espanol",
            es_predeterminado=True,
        )
        otro = Idioma(
            codigo_iso="en",
            nombre="Ingles",
            nombre_nativo="English",
            es_predeterminado=True,
        )
        with self.assertRaises(ValidationError) as contexto:
            otro.full_clean()
        self.assertEqual(
            contexto.exception.message_dict["es_predeterminado"][0],
            MensajesValidacionIdioma.SOLO_UN_IDIOMA_PREDETERMINADO,
        )


class TraduccionContenidoModelTests(TestCase):
    """Pruebas del modelo TraduccionContenido."""

    def setUp(self) -> None:
        self.idioma = Idioma.objects.create(
            codigo_iso="en",
            nombre="Ingles",
            nombre_nativo="English",
        )

    def test_crear_traduccion(self) -> None:
        traduccion = TraduccionContenido.objects.create(
            idioma=self.idioma,
            entidad="Formulario",
            entidad_uuid="11111111-1111-1111-1111-111111111111",
            campo="nombre",
            valor_traducido="Survey",
        )
        self.assertEqual(traduccion.valor_traducido, "Survey")

    def test_no_duplicar_traduccion(self) -> None:
        TraduccionContenido.objects.create(
            idioma=self.idioma,
            entidad="Pregunta",
            entidad_uuid="22222222-2222-2222-2222-222222222222",
            campo="texto",
            valor_traducido="Question",
        )
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                TraduccionContenido.objects.create(
                    idioma=self.idioma,
                    entidad="Pregunta",
                    entidad_uuid="22222222-2222-2222-2222-222222222222",
                    campo="texto",
                    valor_traducido="Duplicada",
                )

    def test_permite_lectura_facil(self) -> None:
        traduccion = TraduccionContenido.objects.create(
            idioma=self.idioma,
            entidad="Pregunta",
            entidad_uuid="33333333-3333-3333-3333-333333333333",
            campo="texto",
            valor_traducido="Question",
            lectura_facil="Pregunta en lectura facil",
        )
        self.assertEqual(traduccion.lectura_facil, "Pregunta en lectura facil")

    def test_permite_texto_alternativo(self) -> None:
        traduccion = TraduccionContenido.objects.create(
            idioma=self.idioma,
            entidad="Pregunta",
            entidad_uuid="44444444-4444-4444-4444-444444444444",
            campo="texto",
            valor_traducido="Question",
            texto_alternativo="Texto alternativo de la pregunta",
        )
        self.assertEqual(
            traduccion.texto_alternativo,
            "Texto alternativo de la pregunta",
        )

    def test_permite_transcripcion(self) -> None:
        traduccion = TraduccionContenido.objects.create(
            idioma=self.idioma,
            entidad="Pregunta",
            entidad_uuid="55555555-5555-5555-5555-555555555555",
            campo="texto",
            valor_traducido="Question",
            transcripcion="Transcripcion del audio",
        )
        self.assertEqual(traduccion.transcripcion, "Transcripcion del audio")

    def test_permite_metadatos(self) -> None:
        metadatos = {"duracion_segundos": 120, "idioma_origen": "es"}
        traduccion = TraduccionContenido.objects.create(
            idioma=self.idioma,
            entidad="Pregunta",
            entidad_uuid="66666666-6666-6666-6666-666666666666",
            campo="texto",
            valor_traducido="Question",
            metadatos=metadatos,
        )
        self.assertEqual(traduccion.metadatos, metadatos)
