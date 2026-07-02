"""
Pruebas de servicios y mapeo de respuestas.
"""

import uuid
from datetime import date, datetime, time
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.respuestas.constantes import MensajesRespuestaApi
from aplicaciones.respuestas.excepciones import (
    PreguntaNoExisteError,
    SesionRespuestaNoExisteError,
    ValorInvalidoError,
)
from aplicaciones.respuestas.models import OrigenRespuesta, Respuesta
from aplicaciones.respuestas.servicios import guardar_o_actualizar_respuesta
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima


def crear_contexto_respuesta() -> tuple[SesionAnonima, Pregunta]:
    """Crea formulario, sesion y pregunta numerica para pruebas."""
    formulario = Formulario.objects.create(
        codigo="form_resp",
        nombre="Formulario respuestas",
        tipo_formulario=TipoFormulario.ENCUESTA,
        estado=EstadoFormulario.PUBLICADO,
    )
    version = FormularioVersion.objects.create(
        formulario=formulario,
        numero_version=1,
        estado=EstadoFormulario.PUBLICADO,
        es_publicada=True,
    )
    sesion = SesionAnonima.objects.create(
        uuid_sesion=uuid.uuid4(),
        formulario=formulario,
        version_formulario=version,
        estado=EstadoSesionAnonima.INICIADA,
    )
    seccion = SeccionFormulario.objects.create(
        formulario_version=version,
        codigo="sec_01",
        titulo="Seccion",
        orden=1,
    )
    pregunta = Pregunta.objects.create(
        seccion=seccion,
        codigo="P1",
        texto="Pregunta numero",
        tipo_pregunta=TipoPregunta.NUMERO,
        orden=1,
    )
    return sesion, pregunta


def crear_pregunta_adicional(
    sesion: SesionAnonima,
    codigo: str,
    tipo_pregunta: str,
    orden: int,
) -> Pregunta:
    """Crea una pregunta adicional en la version de la sesion."""
    seccion = SeccionFormulario.objects.create(
        formulario_version=sesion.version_formulario,
        codigo=f"sec_{codigo}",
        titulo=f"Seccion {codigo}",
        orden=orden,
    )
    return Pregunta.objects.create(
        seccion=seccion,
        codigo=codigo,
        texto=f"Pregunta {codigo}",
        tipo_pregunta=tipo_pregunta,
        orden=orden,
    )


class GuardarRespuestaServicioTests(TestCase):
    """Pruebas del servicio guardar_o_actualizar_respuesta."""

    def setUp(self) -> None:
        self.sesion, self.pregunta = crear_contexto_respuesta()

    def test_guardar_respuesta_nueva(self) -> None:
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P1",
            valor=25,
        )

        self.assertTrue(resultado.fue_creada)
        self.assertEqual(resultado.respuesta.valor_numero, Decimal("25"))
        self.assertEqual(resultado.respuesta.version_respuesta, 1)

    def test_actualizar_respuesta_incrementa_version(self) -> None:
        guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P1",
            valor=25,
        )
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P1",
            valor=30,
        )

        self.assertFalse(resultado.fue_creada)
        self.assertEqual(resultado.respuesta.version_respuesta, 2)
        self.assertEqual(resultado.respuesta.valor_numero, Decimal("30"))

    def test_actualiza_estado_sesion_a_en_proceso(self) -> None:
        guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P1",
            valor=10,
        )
        self.sesion.refresh_from_db()
        self.assertEqual(self.sesion.estado, EstadoSesionAnonima.EN_PROCESO)

    def test_guardar_texto(self) -> None:
        crear_pregunta_adicional(self.sesion, "P_TXT", TipoPregunta.TEXTO_CORTO, 2)
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P_TXT",
            valor="texto de respuesta",
        )
        self.assertEqual(resultado.respuesta.valor_texto, "texto de respuesta")

    def test_guardar_boolean(self) -> None:
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P1",
            valor=True,
        )
        self.assertTrue(resultado.respuesta.valor_booleano)

    def test_guardar_fecha(self) -> None:
        crear_pregunta_adicional(self.sesion, "P_FEC", TipoPregunta.FECHA, 3)
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P_FEC",
            valor="2026-01-15",
        )
        self.assertEqual(resultado.respuesta.valor_fecha, date(2026, 1, 15))

    def test_guardar_fecha_desde_componentes_frontend(self) -> None:
        crear_pregunta_adicional(self.sesion, "P_FEC2", TipoPregunta.FECHA, 7)
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P_FEC2",
            valor={"anio": "1990", "mes": "6", "dia": "15"},
        )
        self.assertEqual(resultado.respuesta.valor_fecha, date(1990, 6, 15))

    def test_guardar_hora(self) -> None:
        crear_pregunta_adicional(self.sesion, "P_HOR", TipoPregunta.HORA, 4)
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P_HOR",
            valor="10:30:00",
        )
        self.assertEqual(resultado.respuesta.valor_hora, time(10, 30, 0))

    def test_guardar_fecha_hora(self) -> None:
        crear_pregunta_adicional(self.sesion, "P_FH", TipoPregunta.FECHA_HORA, 5)
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P_FH",
            valor="2026-01-01T10:00:00-05:00",
        )
        self.assertIsNotNone(resultado.respuesta.valor_fecha_hora)

    def test_guardar_json(self) -> None:
        crear_pregunta_adicional(self.sesion, "P_CHK", TipoPregunta.CHECKBOX, 6)
        valor_json = ["opc_1", "opc_2"]
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P_CHK",
            valor=valor_json,
        )
        self.assertEqual(resultado.respuesta.valor_json, valor_json)

    def test_guardar_geolocalizacion(self) -> None:
        crear_pregunta_adicional(
            self.sesion,
            "P_GEO",
            TipoPregunta.GEOLOCALIZACION,
            7,
        )
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P_GEO",
            valor={
                "latitud": 4.60971,
                "longitud": -74.08175,
                "precision_metros": 10,
            },
        )
        self.assertEqual(resultado.respuesta.latitud, Decimal("4.60971"))

    def test_guardar_origen_offline(self) -> None:
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P1",
            valor=5,
            origen_respuesta=OrigenRespuesta.OFFLINE,
        )
        self.assertEqual(resultado.respuesta.origen_respuesta, OrigenRespuesta.OFFLINE)
        self.assertTrue(resultado.respuesta.requiere_sincronizacion)

    def test_guardar_fecha_respuesta_cliente(self) -> None:
        fecha_cliente = timezone.make_aware(datetime(2026, 1, 1, 10, 0, 0))
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P1",
            valor=7,
            fecha_respuesta_cliente=fecha_cliente,
        )
        self.assertEqual(resultado.respuesta.fecha_respuesta_cliente, fecha_cliente)

    def test_error_sesion_no_existe(self) -> None:
        with self.assertRaises(SesionRespuestaNoExisteError) as contexto:
            guardar_o_actualizar_respuesta(
                uuid_sesion=uuid.uuid4(),
                codigo_pregunta="P1",
                valor=1,
            )
        self.assertEqual(
            contexto.exception.mensaje,
            MensajesRespuestaApi.SESION_NO_EXISTE,
        )

    def test_error_pregunta_no_existe(self) -> None:
        with self.assertRaises(PreguntaNoExisteError):
            guardar_o_actualizar_respuesta(
                uuid_sesion=self.sesion.uuid_sesion,
                codigo_pregunta="INEXISTENTE",
                valor=1,
            )

    def test_error_valor_invalido(self) -> None:
        with self.assertRaises(ValorInvalidoError):
            guardar_o_actualizar_respuesta(
                uuid_sesion=self.sesion.uuid_sesion,
                codigo_pregunta="P1",
                valor="no_es_numero",
            )

    def test_no_duplicar_respuesta_por_sesion_y_pregunta(self) -> None:
        guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta="P1",
            valor=1,
        )

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Respuesta.objects.create(
                    sesion=self.sesion,
                    pregunta=self.pregunta,
                    valor_numero=Decimal("99"),
                )
