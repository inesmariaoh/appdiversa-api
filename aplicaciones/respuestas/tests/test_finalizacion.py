"""
Pruebas de validacion final y finalizacion de formularios anonimos.
"""

import uuid
from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.models import RegistroAuditoria
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
    FormularioYaFinalizadoError,
    SesionRespuestaNoExisteError,
)
from aplicaciones.respuestas.models import Respuesta
from aplicaciones.respuestas.servicios import (
    finalizar_formulario_sesion,
    guardar_o_actualizar_respuesta,
    resumen_respuestas_sesion,
    validar_formulario_sesion,
)
from aplicaciones.respuestas.validacion_util import validar_respuesta_util
from aplicaciones.notificaciones.constantes import CodigoPlantillaCorreo, EstadoNotificacion
from aplicaciones.notificaciones.models import Notificacion
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima
from aplicaciones.sesiones_anonimas.seguridad import generar_token_cliente_seguro
from aplicaciones.usuarios.tests.helpers import inicializar_entorno_usuarios

URL_VALIDAR = "/api/v1/sesiones/{uuid}/validar-finalizacion/"
URL_FINALIZAR = "/api/v1/sesiones/{uuid}/finalizar/"
URL_RESUMEN = "/api/v1/sesiones/{uuid}/resumen/"


def crear_contexto_finalizacion(
    codigo_pregunta: str = "P1",
    tipo_pregunta: str = TipoPregunta.NUMERO,
    es_obligatoria: bool = True,
    seccion_codigo: str = "CAP-I",
    seccion_titulo: str = "Capitulo I - Identificacion",
) -> tuple[SesionAnonima, Pregunta]:
    """Crea sesion con una pregunta configurable para pruebas de finalizacion."""
    formulario = Formulario.objects.create(
        codigo="form_fin",
        nombre="Formulario finalizacion",
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
        estado=EstadoSesionAnonima.EN_PROCESO,
        token_cliente=generar_token_cliente_seguro(),
    )
    seccion = SeccionFormulario.objects.create(
        formulario_version=version,
        codigo=seccion_codigo,
        titulo=seccion_titulo,
        orden=1,
    )
    pregunta = Pregunta.objects.create(
        seccion=seccion,
        codigo=codigo_pregunta,
        texto="Pregunta de prueba",
        tipo_pregunta=tipo_pregunta,
        es_obligatoria=es_obligatoria,
        orden=1,
    )
    return sesion, pregunta


def crear_respuesta_vacia(sesion: SesionAnonima, pregunta: Pregunta) -> Respuesta:
    """Crea una respuesta sin valor util para pruebas."""
    return Respuesta.objects.create(sesion=sesion, pregunta=pregunta)


class ValidarRespuestaUtilTests(TestCase):
    """Pruebas de validacion de respuesta util por tipo."""

    def test_texto_vacio_no_es_util(self) -> None:
        sesion, pregunta = crear_contexto_finalizacion(
            tipo_pregunta=TipoPregunta.TEXTO_CORTO,
        )
        respuesta = crear_respuesta_vacia(sesion, pregunta)
        self.assertFalse(validar_respuesta_util(pregunta, respuesta))

    def test_numero_cero_es_util(self) -> None:
        sesion, pregunta = crear_contexto_finalizacion()
        respuesta = crear_respuesta_vacia(sesion, pregunta)
        respuesta.valor_numero = Decimal("0")
        self.assertTrue(validar_respuesta_util(pregunta, respuesta))

    def test_checkbox_lista_vacia_no_es_util(self) -> None:
        sesion, pregunta = crear_contexto_finalizacion(
            codigo_pregunta="P_CHK",
            tipo_pregunta=TipoPregunta.CHECKBOX,
        )
        respuesta = crear_respuesta_vacia(sesion, pregunta)
        respuesta.valor_json = []
        self.assertFalse(validar_respuesta_util(pregunta, respuesta))

    def test_checkbox_con_valores_es_util(self) -> None:
        sesion, pregunta = crear_contexto_finalizacion(
            codigo_pregunta="P_CHK",
            tipo_pregunta=TipoPregunta.CHECKBOX,
        )
        respuesta = crear_respuesta_vacia(sesion, pregunta)
        respuesta.valor_json = ["opc_1"]
        self.assertTrue(validar_respuesta_util(pregunta, respuesta))

    def test_geolocalizacion_sin_coordenadas_no_es_util(self) -> None:
        sesion, pregunta = crear_contexto_finalizacion(
            codigo_pregunta="P_GEO",
            tipo_pregunta=TipoPregunta.GEOLOCALIZACION,
        )
        respuesta = crear_respuesta_vacia(sesion, pregunta)
        respuesta.latitud = Decimal("4.6")
        self.assertFalse(validar_respuesta_util(pregunta, respuesta))


class ValidacionFinalizacionServicioTests(TestCase):
    """Pruebas de servicios de validacion y finalizacion."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def test_validacion_exitosa_sin_pendientes(self) -> None:
        sesion, pregunta = crear_contexto_finalizacion()
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=25,
        )
        resultado = validar_formulario_sesion(sesion.uuid_sesion)
        self.assertTrue(resultado["es_valido"])
        self.assertEqual(resultado["total_pendientes"], 0)

    def test_validacion_con_pregunta_obligatoria_pendiente(self) -> None:
        sesion, _ = crear_contexto_finalizacion()
        resultado = validar_formulario_sesion(sesion.uuid_sesion)
        self.assertFalse(resultado["es_valido"])
        self.assertEqual(resultado["total_pendientes"], 1)

    def test_pregunta_opcional_no_bloquea_finalizacion(self) -> None:
        sesion, pregunta = crear_contexto_finalizacion(es_obligatoria=False)
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=10,
        )
        resultado = validar_formulario_sesion(sesion.uuid_sesion)
        self.assertTrue(resultado["es_valido"])

    def test_finalizar_sesion_correctamente(self) -> None:
        sesion, pregunta = crear_contexto_finalizacion()
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=30,
        )
        resultado = finalizar_formulario_sesion(sesion.uuid_sesion)
        self.assertEqual(resultado["estado"], EstadoSesionAnonima.FINALIZADA)
        sesion.refresh_from_db()
        self.assertEqual(sesion.estado, EstadoSesionAnonima.FINALIZADA)

    def test_finalizar_con_correo_envia_notificacion(self) -> None:
        sesion, pregunta = crear_contexto_finalizacion()
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=15,
        )
        finalizar_formulario_sesion(
            sesion.uuid_sesion,
            correo_notificacion="finalizado@example.com",
        )
        notificacion = Notificacion.objects.filter(
            destinatario="finalizado@example.com",
            plantilla__codigo=CodigoPlantillaCorreo.FORMULARIO_FINALIZADO,
        ).first()
        self.assertIsNotNone(notificacion)
        self.assertEqual(notificacion.estado, EstadoNotificacion.ENVIADA)

    def test_no_finalizar_si_hay_pendientes(self) -> None:
        sesion, _ = crear_contexto_finalizacion()
        resultado = finalizar_formulario_sesion(sesion.uuid_sesion)
        self.assertFalse(resultado["es_valido"])
        sesion.refresh_from_db()
        self.assertNotEqual(sesion.estado, EstadoSesionAnonima.FINALIZADA)

    def test_no_finalizar_dos_veces(self) -> None:
        sesion, pregunta = crear_contexto_finalizacion()
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=5,
        )
        finalizar_formulario_sesion(sesion.uuid_sesion)
        with self.assertRaises(FormularioYaFinalizadoError):
            finalizar_formulario_sesion(sesion.uuid_sesion)

    def test_resumen_retorna_seccion_y_pregunta(self) -> None:
        sesion, pregunta = crear_contexto_finalizacion()
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=25,
        )
        resumen = resumen_respuestas_sesion(sesion.uuid_sesion)
        self.assertEqual(len(resumen["respuestas"]), 1)
        item = resumen["respuestas"][0]
        self.assertEqual(item["seccion_codigo"], "CAP-I")
        self.assertEqual(item["pregunta_codigo"], pregunta.codigo)

    def test_error_si_sesion_no_existe(self) -> None:
        with self.assertRaises(SesionRespuestaNoExisteError):
            validar_formulario_sesion(uuid.uuid4())

    def test_auditoria_al_finalizar(self) -> None:
        sesion, pregunta = crear_contexto_finalizacion()
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=12,
        )
        RegistroAuditoria.objects.all().delete()
        finalizar_formulario_sesion(sesion.uuid_sesion)
        registro = RegistroAuditoria.objects.filter(
            accion=AccionAuditoria.FINALIZAR_FORMULARIO,
        ).first()
        self.assertIsNotNone(registro)
        self.assertEqual(registro.entidad, SesionAnonima.__name__)


class FinalizacionApiTests(TestCase):
    """Pruebas de endpoints de validacion y finalizacion."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.sesion, self.pregunta = crear_contexto_finalizacion()
        self.headers_sesion = {
            "HTTP_X_SESION_ANONIMA": str(self.sesion.uuid_sesion),
            "HTTP_X_TOKEN_SESION": self.sesion.token_cliente,
        }

    def test_endpoint_validar_finalizacion_200(self) -> None:
        guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta=self.pregunta.codigo,
            valor=20,
        )
        respuesta = self.cliente.post(
            URL_VALIDAR.format(uuid=self.sesion.uuid_sesion),
            **self.headers_sesion,
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertTrue(respuesta.json()["es_valido"])

    def test_endpoint_finalizar_400_con_pendientes(self) -> None:
        respuesta = self.cliente.post(
            URL_FINALIZAR.format(uuid=self.sesion.uuid_sesion),
            **self.headers_sesion,
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(respuesta.json()["es_valido"])

    def test_endpoint_finalizar_200_si_completo(self) -> None:
        guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta=self.pregunta.codigo,
            valor=18,
        )
        respuesta = self.cliente.post(
            URL_FINALIZAR.format(uuid=self.sesion.uuid_sesion),
            **self.headers_sesion,
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            respuesta.json()["mensaje"],
            MensajesRespuestaApi.FORMULARIO_FINALIZADO_OK,
        )

    def test_endpoint_resumen_200(self) -> None:
        guardar_o_actualizar_respuesta(
            uuid_sesion=self.sesion.uuid_sesion,
            codigo_pregunta=self.pregunta.codigo,
            valor=22,
        )
        respuesta = self.cliente.get(
            URL_RESUMEN.format(uuid=self.sesion.uuid_sesion),
            **self.headers_sesion,
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.json()["respuestas"]), 1)

    def test_endpoint_resumen_403_sesion_inexistente(self) -> None:
        respuesta = self.cliente.get(
            URL_RESUMEN.format(uuid=uuid.uuid4()),
            HTTP_X_SESION_ANONIMA=str(uuid.uuid4()),
            HTTP_X_TOKEN_SESION="token-invalido",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
