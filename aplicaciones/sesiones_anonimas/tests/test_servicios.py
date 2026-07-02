"""
Pruebas de servicios de sesiones anonimas.
"""

import uuid

from django.test import TestCase

from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    TipoFormulario,
)
from aplicaciones.sesiones_anonimas.constantes import MensajesSesionApi
from aplicaciones.sesiones_anonimas.excepciones import (
    FormularioSesionNoDisponibleError,
    VersionSesionNoDisponibleError,
)
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima
from aplicaciones.sesiones_anonimas.servicios import crear_o_obtener_sesion_anonima


def crear_formulario_publicado(codigo: str = "form_sesion") -> Formulario:
    """Crea un formulario publicado para pruebas de sesion."""
    return Formulario.objects.create(
        codigo=codigo,
        nombre=f"Nombre {codigo}",
        tipo_formulario=TipoFormulario.ENCUESTA,
        estado=EstadoFormulario.PUBLICADO,
    )


def crear_version_publicada(formulario: Formulario) -> FormularioVersion:
    """Crea una version publicada para pruebas de sesion."""
    return FormularioVersion.objects.create(
        formulario=formulario,
        numero_version=1,
        estado=EstadoFormulario.PUBLICADO,
        es_publicada=True,
    )


class CrearSesionAnonimaServicioTests(TestCase):
    """Pruebas del servicio crear_o_obtener_sesion_anonima."""

    def setUp(self) -> None:
        self.formulario = crear_formulario_publicado()
        crear_version_publicada(self.formulario)
        self.uuid_sesion = uuid.uuid4()

    def test_crear_sesion_anonima(self) -> None:
        resultado = crear_o_obtener_sesion_anonima(
            uuid_sesion=self.uuid_sesion,
            uuid_formulario=self.formulario.uuid,
            idioma="es-CO",
            zona_horaria="America/Bogota",
            es_offline=True,
        )

        self.assertTrue(resultado.fue_creada)
        self.assertEqual(resultado.sesion.estado, EstadoSesionAnonima.INICIADA)
        self.assertEqual(resultado.sesion.idioma, "es-CO")
        self.assertTrue(resultado.sesion.es_offline)

    def test_reutilizar_sesion_existente_sin_duplicar(self) -> None:
        crear_o_obtener_sesion_anonima(
            uuid_sesion=self.uuid_sesion,
            uuid_formulario=self.formulario.uuid,
        )
        resultado = crear_o_obtener_sesion_anonima(
            uuid_sesion=self.uuid_sesion,
            uuid_formulario=self.formulario.uuid,
        )

        self.assertFalse(resultado.fue_creada)
        self.assertEqual(SesionAnonima.objects.count(), 1)

    def test_error_formulario_no_publicado(self) -> None:
        formulario_borrador = Formulario.objects.create(
            codigo="borrador",
            nombre="Formulario borrador",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.BORRADOR,
        )

        with self.assertRaises(FormularioSesionNoDisponibleError) as contexto:
            crear_o_obtener_sesion_anonima(
                uuid_sesion=uuid.uuid4(),
                uuid_formulario=formulario_borrador.uuid,
            )

        self.assertEqual(
            contexto.exception.mensaje,
            MensajesSesionApi.FORMULARIO_NO_DISPONIBLE,
        )

    def test_error_sin_version_publicada(self) -> None:
        formulario = crear_formulario_publicado(codigo="sin_version")
        FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
            estado=EstadoFormulario.BORRADOR,
            es_publicada=False,
        )

        with self.assertRaises(VersionSesionNoDisponibleError):
            crear_o_obtener_sesion_anonima(
                uuid_sesion=uuid.uuid4(),
                uuid_formulario=formulario.uuid,
            )

    def test_error_formulario_no_existe(self) -> None:
        with self.assertRaises(FormularioSesionNoDisponibleError):
            crear_o_obtener_sesion_anonima(
                uuid_sesion=uuid.uuid4(),
                uuid_formulario=uuid.uuid4(),
            )
