"""
Pruebas de la validacion del texto libre obligatorio en opciones tipo otro.
"""

import uuid

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    OpcionRespuesta,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.respuestas.constantes import (
    MENSAJES_MOTIVO_PENDIENTE,
    MotivoPreguntaPendiente,
)
from aplicaciones.respuestas.servicios import (
    guardar_o_actualizar_respuesta,
    validar_formulario_sesion,
)

URL_VALIDAR = "/api/v1/sesiones/{uuid}/validar-finalizacion/"
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima
from aplicaciones.sesiones_anonimas.seguridad import generar_token_cliente_seguro
from aplicaciones.usuarios.tests.helpers import inicializar_entorno_usuarios

CODIGO_OPCION_OTRO = "OP_OTRO"
CODIGO_OPCION_NORMAL = "OP_UNO"


def crear_contexto_opcion_otro(
    tipo_pregunta: str = TipoPregunta.RADIO,
    texto_otro_obligatorio: bool = True,
) -> tuple[SesionAnonima, Pregunta]:
    """Crea una sesion con pregunta que expone una opcion tipo otro configurable."""
    formulario = Formulario.objects.create(
        codigo="form_otro",
        nombre="Formulario otro",
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
        codigo="SEC-1",
        titulo="Seccion",
        orden=1,
    )
    pregunta = Pregunta.objects.create(
        seccion=seccion,
        codigo="P_OTRO",
        texto="Su vivienda se encuentra ubicada en",
        tipo_pregunta=tipo_pregunta,
        es_obligatoria=False,
        permite_otro=True,
        texto_otro_obligatorio=texto_otro_obligatorio,
        orden=1,
    )
    OpcionRespuesta.objects.create(
        pregunta=pregunta,
        codigo=CODIGO_OPCION_NORMAL,
        etiqueta="Resguardo indigena",
        valor="resguardo",
        orden=1,
    )
    OpcionRespuesta.objects.create(
        pregunta=pregunta,
        codigo=CODIGO_OPCION_OTRO,
        etiqueta="Otro, ¿cual?",
        valor="otro",
        orden=2,
        activa_otro=True,
    )
    return sesion, pregunta


class TextoOtroObligatorioValidacionTests(TestCase):
    """Verifica el bloqueo de finalizacion cuando falta el texto de una opcion otro."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def test_opcion_otro_sin_texto_bloquea_finalizacion(self) -> None:
        sesion, pregunta = crear_contexto_opcion_otro()
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=CODIGO_OPCION_OTRO,
        )
        resultado = validar_formulario_sesion(sesion.uuid_sesion)
        self.assertFalse(resultado["es_valido"])
        self.assertEqual(resultado["total_pendientes"], 1)
        pendiente = resultado["preguntas_pendientes"][0]
        self.assertEqual(pendiente["codigo"], pregunta.codigo)
        self.assertEqual(
            pendiente["motivo"],
            MotivoPreguntaPendiente.TEXTO_OTRO_REQUERIDO,
        )

    def test_opcion_otro_con_texto_permite_finalizacion(self) -> None:
        sesion, pregunta = crear_contexto_opcion_otro()
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=CODIGO_OPCION_OTRO,
            observacion="Zona rural dispersa",
        )
        resultado = validar_formulario_sesion(sesion.uuid_sesion)
        self.assertTrue(resultado["es_valido"])

    def test_opcion_normal_no_exige_texto(self) -> None:
        sesion, pregunta = crear_contexto_opcion_otro()
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=CODIGO_OPCION_NORMAL,
        )
        resultado = validar_formulario_sesion(sesion.uuid_sesion)
        self.assertTrue(resultado["es_valido"])

    def test_flag_desactivado_no_exige_texto(self) -> None:
        sesion, pregunta = crear_contexto_opcion_otro(texto_otro_obligatorio=False)
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=CODIGO_OPCION_OTRO,
        )
        resultado = validar_formulario_sesion(sesion.uuid_sesion)
        self.assertTrue(resultado["es_valido"])

    def test_seleccion_multiple_con_otro_sin_texto_bloquea(self) -> None:
        sesion, pregunta = crear_contexto_opcion_otro(
            tipo_pregunta=TipoPregunta.CHECKBOX,
        )
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=[CODIGO_OPCION_NORMAL, CODIGO_OPCION_OTRO],
        )
        resultado = validar_formulario_sesion(sesion.uuid_sesion)
        self.assertFalse(resultado["es_valido"])

    def test_endpoint_expone_motivo_y_mensaje_de_pendiente(self) -> None:
        sesion, pregunta = crear_contexto_opcion_otro()
        guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor=CODIGO_OPCION_OTRO,
        )
        cliente = APIClient()
        respuesta = cliente.post(
            URL_VALIDAR.format(uuid=sesion.uuid_sesion),
            HTTP_X_SESION_ANONIMA=str(sesion.uuid_sesion),
            HTTP_X_TOKEN_SESION=sesion.token_cliente,
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        pendiente = respuesta.json()["preguntas_pendientes"][0]
        self.assertEqual(
            pendiente["motivo"],
            MotivoPreguntaPendiente.TEXTO_OTRO_REQUERIDO,
        )
        self.assertEqual(
            pendiente["mensaje"],
            MENSAJES_MOTIVO_PENDIENTE[MotivoPreguntaPendiente.TEXTO_OTRO_REQUERIDO],
        )
