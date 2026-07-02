"""
Pruebas del motor transversal de exportaciones.
"""

import csv
import io
import json
import uuid
from decimal import Decimal

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.catalogos.constantes import TiposCatalogo
from aplicaciones.catalogos.servicios import (
    crear_catalogo_si_no_existe,
    crear_item_catalogo_si_no_existe,
)
from aplicaciones.comun.tests.helpers_seguridad import (
    TOKEN_API_INTERNA_PRUEBA,
    headers_api_interna,
)
from aplicaciones.exportaciones.constantes import (
    EstadoExportacion,
    FormatoExportacion,
    MensajesExportacionApi,
    TipoExportacion,
)
from aplicaciones.exportaciones.excepciones import (
    ExportacionNoEncontradaError,
    FormatoExportacionNoSoportadoError,
)
from aplicaciones.exportaciones.generadores import (
    CsvExportador,
    OdsExportador,
    PdfExportador,
    generar_csv,
    generar_excel,
    generar_json,
    generar_sql,
)
from aplicaciones.exportaciones.servicios import (
    exportar_analitica,
    exportar_catalogos,
    exportar_respuestas,
    obtener_exportacion,
)
from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.respuestas.models import Respuesta
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima

URL_EXPORTACIONES = "/api/v1/exportaciones/"
REGISTROS_PRUEBA = [
    {"nombre": "Ana", "edad": 30, "activo": True},
    {"nombre": "Luis", "edad": 25, "activo": False},
]


def crear_contexto_respuesta_exportacion() -> tuple[SesionAnonima, Pregunta, Respuesta]:
    """Crea formulario, sesion, pregunta y respuesta para pruebas de exportacion."""
    formulario = Formulario.objects.create(
        codigo="form_export",
        nombre="Formulario exportacion",
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
        estado=EstadoSesionAnonima.FINALIZADA,
        idioma="es-CO",
    )
    seccion = SeccionFormulario.objects.create(
        formulario_version=version,
        codigo="sec_export",
        titulo="Seccion export",
        orden=1,
    )
    pregunta = Pregunta.objects.create(
        seccion=seccion,
        codigo="P_EXPORT",
        texto="Pregunta export",
        tipo_pregunta=TipoPregunta.NUMERO,
        orden=1,
    )
    respuesta = Respuesta.objects.create(
        sesion=sesion,
        pregunta=pregunta,
        valor_numero=Decimal("42"),
    )
    return sesion, pregunta, respuesta


class ExportacionesGeneradoresTests(TestCase):
    """Pruebas de generadores de archivos de exportacion."""

    def test_generar_csv(self) -> None:
        contenido = generar_csv(REGISTROS_PRUEBA)
        texto = contenido.decode("utf-8-sig")
        lector = csv.DictReader(io.StringIO(texto))
        filas = list(lector)
        self.assertEqual(len(filas), 2)
        self.assertEqual(filas[0]["nombre"], "Ana")

    def test_generar_json(self) -> None:
        contenido = generar_json(REGISTROS_PRUEBA)
        datos = json.loads(contenido.decode("utf-8"))
        self.assertEqual(len(datos), 2)
        self.assertEqual(datos[0]["nombre"], "Ana")

    def test_generar_sql(self) -> None:
        contenido = generar_sql(
            REGISTROS_PRUEBA,
            {"tabla": "personas_export"},
        )
        texto = contenido.decode("utf-8")
        self.assertIn("INSERT INTO personas_export", texto)
        self.assertIn("'Ana'", texto)

    def test_generar_excel(self) -> None:
        contenido = generar_excel(REGISTROS_PRUEBA)
        self.assertGreater(len(contenido), 0)
        self.assertEqual(contenido[:2], b"PK")

    def test_csv_vacio(self) -> None:
        contenido = CsvExportador().generar([], {})
        self.assertEqual(contenido, b"")

    def test_pdf_y_ods_no_soportados(self) -> None:
        with self.assertRaises(FormatoExportacionNoSoportadoError):
            PdfExportador().generar(REGISTROS_PRUEBA, {})
        with self.assertRaises(FormatoExportacionNoSoportadoError):
            OdsExportador().generar(REGISTROS_PRUEBA, {})


class ExportacionesServiciosTests(TestCase):
    """Pruebas de servicios de exportacion."""

    def setUp(self) -> None:
        self.sesion, _, _ = crear_contexto_respuesta_exportacion()

    def test_exportar_catalogos_csv(self) -> None:
        catalogo = crear_catalogo_si_no_existe(
            codigo="export_cat",
            nombre="Catalogo export",
            tipo_catalogo=TiposCatalogo.DEMOGRAFICO,
        )
        crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="01",
            nombre="Item export",
            valor="01",
        )
        exportacion = exportar_catalogos(
            formato=FormatoExportacion.CSV,
            parametros={"catalogo_codigo": "export_cat"},
        )
        self.assertEqual(exportacion.estado, EstadoExportacion.FINALIZADA)
        self.assertEqual(exportacion.tipo, TipoExportacion.CATALOGOS)
        self.assertGreaterEqual(exportacion.registros_exportados, 1)
        self.assertIsNotNone(exportacion.archivo_id)

    def test_exportar_respuestas_json(self) -> None:
        exportacion = exportar_respuestas(
            formato=FormatoExportacion.JSON,
            parametros={
                "formulario_codigo": "form_export",
                "estado_sesion": EstadoSesionAnonima.FINALIZADA,
                "idioma": "es-CO",
            },
        )
        self.assertEqual(exportacion.estado, EstadoExportacion.FINALIZADA)
        self.assertEqual(exportacion.tipo, TipoExportacion.RESPUESTAS)
        self.assertEqual(exportacion.registros_exportados, 1)

    def test_filtro_idioma_excluye_otras_sesiones(self) -> None:
        formulario = self.sesion.formulario
        version = self.sesion.version_formulario
        sesion_otro_idioma = SesionAnonima.objects.create(
            uuid_sesion=uuid.uuid4(),
            formulario=formulario,
            version_formulario=version,
            estado=EstadoSesionAnonima.FINALIZADA,
            idioma="en-US",
        )
        seccion = SeccionFormulario.objects.create(
            formulario_version=version,
            codigo="sec_otro",
            titulo="Seccion otro",
            orden=2,
        )
        pregunta = Pregunta.objects.create(
            seccion=seccion,
            codigo="P_OTRO",
            texto="Otra pregunta",
            tipo_pregunta=TipoPregunta.NUMERO,
            orden=1,
        )
        Respuesta.objects.create(
            sesion=sesion_otro_idioma,
            pregunta=pregunta,
            valor_numero=Decimal("10"),
        )

        exportacion = exportar_respuestas(
            formato=FormatoExportacion.CSV,
            parametros={"idioma": "es-CO"},
        )
        self.assertEqual(exportacion.registros_exportados, 1)

    def test_exportar_analitica(self) -> None:
        exportacion = exportar_analitica(
            formato=FormatoExportacion.JSON,
            parametros={"formulario_codigo": "form_export"},
        )
        self.assertEqual(exportacion.tipo, TipoExportacion.ANALITICA)
        self.assertIn(
            exportacion.estado,
            {EstadoExportacion.FINALIZADA, EstadoExportacion.FALLIDA},
        )

    def test_exportar_pdf_fallida(self) -> None:
        exportacion = exportar_catalogos(
            formato=FormatoExportacion.PDF,
            parametros={},
        )
        self.assertEqual(exportacion.estado, EstadoExportacion.FALLIDA)
        self.assertEqual(
            exportacion.error,
            MensajesExportacionApi.FORMATO_NO_SOPORTADO,
        )

    def test_obtener_exportacion_inexistente(self) -> None:
        with self.assertRaises(ExportacionNoEncontradaError):
            obtener_exportacion(uuid.uuid4())


@override_settings(API_INTERNA_TOKEN=TOKEN_API_INTERNA_PRUEBA)
class ExportacionesApiTests(TestCase):
    """Pruebas de endpoints de la API de exportaciones."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        crear_contexto_respuesta_exportacion()
        catalogo = crear_catalogo_si_no_existe(
            codigo="api_cat",
            nombre="Catalogo API",
            tipo_catalogo=TiposCatalogo.DEMOGRAFICO,
        )
        crear_item_catalogo_si_no_existe(
            catalogo=catalogo,
            codigo="A1",
            nombre="Item API",
        )

    def test_endpoint_exportar_respuestas(self) -> None:
        respuesta = self.cliente.post(
            f"{URL_EXPORTACIONES}respuestas/",
            {
                "formato": FormatoExportacion.CSV,
                "parametros": {"formulario_codigo": "form_export"},
            },
            format="json",
            **headers_api_interna(),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.json()["tipo"], TipoExportacion.RESPUESTAS)

    def test_endpoint_exportar_catalogos(self) -> None:
        respuesta = self.cliente.post(
            f"{URL_EXPORTACIONES}catalogos/",
            {
                "formato": FormatoExportacion.JSON,
                "parametros": {"catalogo_codigo": "api_cat"},
            },
            format="json",
            **headers_api_interna(),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.json()["tipo"], TipoExportacion.CATALOGOS)

    def test_endpoint_exportar_analitica(self) -> None:
        respuesta = self.cliente.post(
            f"{URL_EXPORTACIONES}analitica/",
            {
                "formato": FormatoExportacion.JSON,
                "parametros": {"formulario_codigo": "form_export"},
            },
            format="json",
            **headers_api_interna(),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.json()["tipo"], TipoExportacion.ANALITICA)

    def test_endpoint_detalle_exportacion(self) -> None:
        creada = exportar_respuestas(
            formato=FormatoExportacion.JSON,
            parametros={"formulario_codigo": "form_export"},
        )
        url = f"{URL_EXPORTACIONES}{creada.uuid}/"
        respuesta = self.cliente.get(url, **headers_api_interna())
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()["uuid"], str(creada.uuid))

    def test_endpoint_detalle_exportacion_inexistente(self) -> None:
        url = f"{URL_EXPORTACIONES}{uuid.uuid4()}/"
        respuesta = self.cliente.get(url, **headers_api_interna())
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            respuesta.json()["detalle"],
            MensajesExportacionApi.EXPORTACION_NO_ENCONTRADA,
        )
