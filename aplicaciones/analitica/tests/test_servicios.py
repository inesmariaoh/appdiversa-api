"""
Pruebas de servicios de analitica.
"""

from decimal import Decimal

from django.test import TestCase

from aplicaciones.analitica.servicios import (
    listar_respuestas_analiticas,
    normalizar_respuesta_analitica,
)
from aplicaciones.analitica.tests.helpers import crear_datos_analitica
from aplicaciones.formularios.models import Pregunta, SeccionFormulario, TipoPregunta
from aplicaciones.respuestas.models import Respuesta
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima


class NormalizarRespuestaAnaliticaTests(TestCase):
    """Pruebas de normalizacion de respuestas analiticas."""

    def test_normaliza_respuesta_numerica(self) -> None:
        _, _, respuesta = crear_datos_analitica()
        resultado = normalizar_respuesta_analitica(respuesta)
        self.assertEqual(resultado["respuesta_valor"], 25.0)
        self.assertEqual(resultado["respuesta_numero"], "25.0000")

    def test_normaliza_respuesta_texto(self) -> None:
        sesion, pregunta, respuesta = crear_datos_analitica()
        pregunta.tipo_pregunta = TipoPregunta.TEXTO_CORTO
        pregunta.save(update_fields=["tipo_pregunta"])
        respuesta.valor_numero = None
        respuesta.valor_texto = "respuesta texto"
        respuesta.save(update_fields=["valor_numero", "valor_texto"])
        resultado = normalizar_respuesta_analitica(respuesta)
        self.assertEqual(resultado["respuesta_valor"], "respuesta texto")

    def test_normaliza_respuesta_json(self) -> None:
        sesion, _, _ = crear_datos_analitica()
        pregunta_checkbox = Pregunta.objects.create(
            seccion=SeccionFormulario.objects.get(
                formulario_version=sesion.version_formulario,
            ),
            codigo="P_CHK",
            texto="Pregunta checkbox",
            tipo_pregunta=TipoPregunta.CHECKBOX,
            orden=2,
        )
        valor_json = ["opc_1", "opc_2"]
        respuesta = Respuesta.objects.create(
            sesion=sesion,
            pregunta=pregunta_checkbox,
            valor_json=valor_json,
        )
        resultado = normalizar_respuesta_analitica(respuesta)
        self.assertEqual(resultado["respuesta_valor"], valor_json)

    def test_normaliza_geolocalizacion(self) -> None:
        sesion, _, _ = crear_datos_analitica()
        pregunta_geo = Pregunta.objects.create(
            seccion=SeccionFormulario.objects.get(
                formulario_version=sesion.version_formulario,
            ),
            codigo="P_GEO",
            texto="Pregunta geolocalizacion",
            tipo_pregunta=TipoPregunta.GEOLOCALIZACION,
            orden=2,
        )
        respuesta = Respuesta.objects.create(
            sesion=sesion,
            pregunta=pregunta_geo,
            latitud=Decimal("4.60971000"),
            longitud=Decimal("-74.08175000"),
            precision_metros=Decimal("10.00"),
        )
        resultado = normalizar_respuesta_analitica(respuesta)
        self.assertEqual(resultado["respuesta_valor"]["latitud"], 4.60971)

    def test_no_incluye_respuestas_eliminadas_logicamente(self) -> None:
        sesion, pregunta, respuesta = crear_datos_analitica()
        respuesta.eliminar_logicamente()
        resultados = listar_respuestas_analiticas(formulario_codigo="DISC-001")
        self.assertEqual(len(resultados), 0)

    def test_filtra_por_formulario_codigo(self) -> None:
        crear_datos_analitica(codigo_formulario="DISC-001")
        crear_datos_analitica(codigo_formulario="OTRO-002")
        resultados = listar_respuestas_analiticas(formulario_codigo="DISC-001")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["formulario_codigo"], "DISC-001")

    def test_filtra_por_estado_sesion(self) -> None:
        crear_datos_analitica(
            codigo_formulario="DISC-FIN",
            estado_sesion=EstadoSesionAnonima.FINALIZADA,
        )
        crear_datos_analitica(
            codigo_formulario="DISC-PROC",
            estado_sesion=EstadoSesionAnonima.EN_PROCESO,
        )
        resultados = listar_respuestas_analiticas(
            estado_sesion=EstadoSesionAnonima.FINALIZADA,
        )
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["estado_sesion"], EstadoSesionAnonima.FINALIZADA)

    def test_incluye_catalogo_cuando_usa_catalogo(self) -> None:
        from aplicaciones.catalogos.constantes import TiposCatalogo
        from aplicaciones.catalogos.models import Catalogo

        sesion, pregunta, respuesta = crear_datos_analitica()
        catalogo = Catalogo.objects.create(
            codigo="sexos_nacimiento",
            nombre="Sexos al nacer",
            tipo_catalogo=TiposCatalogo.DEMOGRAFICO,
        )
        pregunta.usa_catalogo = True
        pregunta.catalogo_asociado = catalogo
        pregunta.tipo_pregunta = TipoPregunta.SELECT
        pregunta.save(update_fields=[
            "usa_catalogo",
            "catalogo_asociado",
            "tipo_pregunta",
        ])
        respuesta.refresh_from_db()

        resultado = normalizar_respuesta_analitica(
            Respuesta.objects.select_related(
                "pregunta__catalogo_asociado",
            ).get(pk=respuesta.pk),
        )
        self.assertTrue(resultado["usa_catalogo"])
        self.assertEqual(resultado["catalogo_codigo"], "sexos_nacimiento")
        self.assertEqual(resultado["catalogo_nombre"], "Sexos al nacer")

    def test_catalogo_null_cuando_no_usa_catalogo(self) -> None:
        _, _, respuesta = crear_datos_analitica()
        resultado = normalizar_respuesta_analitica(respuesta)
        self.assertFalse(resultado["usa_catalogo"])
        self.assertIsNone(resultado["catalogo_codigo"])
        self.assertIsNone(resultado["catalogo_nombre"])