"""
Pruebas de respuestas con catalogos parametrizables.
"""

import uuid

from django.test import TestCase

from aplicaciones.catalogos.constantes import TiposCatalogo
from aplicaciones.catalogos.models import Catalogo, ItemCatalogo
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
from aplicaciones.respuestas.excepciones import ValorNoPerteneceCatalogoError
from aplicaciones.respuestas.servicios import guardar_o_actualizar_respuesta
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima


def crear_contexto_catalogo_respuesta(
    tipo_pregunta: str = TipoPregunta.SELECT,
    codigo_pregunta: str = "P_CAT",
) -> tuple[SesionAnonima, Pregunta, Catalogo]:
    """Crea sesion y pregunta con catalogo asociado."""
    catalogo = Catalogo.objects.create(
        codigo="departamentos",
        nombre="Departamentos",
        tipo_catalogo=TiposCatalogo.GEOGRAFICO,
    )
    ItemCatalogo.objects.create(
        catalogo=catalogo,
        codigo="15",
        nombre="Boyaca",
        valor="15",
    )
    ItemCatalogo.objects.create(
        catalogo=catalogo,
        codigo="11",
        nombre="Bogota",
        valor="11",
    )

    formulario = Formulario.objects.create(
        codigo="form_resp_cat",
        nombre="Formulario respuesta catalogo",
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
        codigo="sec_cat",
        titulo="Seccion",
        orden=1,
    )
    pregunta = Pregunta.objects.create(
        seccion=seccion,
        codigo=codigo_pregunta,
        texto="Seleccione departamento",
        tipo_pregunta=tipo_pregunta,
        orden=1,
        usa_catalogo=True,
        catalogo_asociado=catalogo,
    )
    return sesion, pregunta, catalogo


class RespuestaCatalogoServiciosTests(TestCase):
    """Pruebas de guardado de respuestas con catalogo."""

    def test_guardar_respuesta_valida_con_catalogo(self) -> None:
        sesion, pregunta, _ = crear_contexto_catalogo_respuesta()
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta=pregunta.codigo,
            valor="15",
        )
        self.assertEqual(resultado.respuesta.valor_texto, "15")

    def test_rechazar_valor_no_pertenece_al_catalogo(self) -> None:
        sesion, pregunta, _ = crear_contexto_catalogo_respuesta()
        with self.assertRaises(ValorNoPerteneceCatalogoError) as contexto:
            guardar_o_actualizar_respuesta(
                uuid_sesion=sesion.uuid_sesion,
                codigo_pregunta=pregunta.codigo,
                valor="99",
            )
        self.assertEqual(
            contexto.exception.mensaje,
            MensajesRespuestaApi.VALOR_NO_PERTENECE_CATALOGO,
        )

    def test_guardar_lista_valida_checkbox_catalogo(self) -> None:
        sesion, _, _ = crear_contexto_catalogo_respuesta(
            tipo_pregunta=TipoPregunta.CHECKBOX,
            codigo_pregunta="P_CHK",
        )
        resultado = guardar_o_actualizar_respuesta(
            uuid_sesion=sesion.uuid_sesion,
            codigo_pregunta="P_CHK",
            valor=["15", "11"],
        )
        self.assertEqual(resultado.respuesta.valor_json, ["15", "11"])

    def test_rechazar_lista_con_item_inexistente(self) -> None:
        sesion, _, _ = crear_contexto_catalogo_respuesta(
            tipo_pregunta=TipoPregunta.CHECKBOX,
            codigo_pregunta="P_CHK_ERR",
        )
        with self.assertRaises(ValorNoPerteneceCatalogoError):
            guardar_o_actualizar_respuesta(
                uuid_sesion=sesion.uuid_sesion,
                codigo_pregunta="P_CHK_ERR",
                valor=["15", "99"],
            )
