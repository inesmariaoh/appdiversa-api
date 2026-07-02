"""
Pruebas de la API publica de formularios.
"""

from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.formularios.constantes import (
    EstadoDisponibilidadFormulario,
    EtiquetaEstadoFormulario,
    MensajesFormularioApi,
)
from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    OpcionRespuesta,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
    TipoTextoFormulario,
    TextoFormulario,
)

URL_DISPONIBLES = "/api/v1/formularios/disponibles/"
URL_ESTRUCTURA = "/api/v1/formularios/{uuid}/estructura/"


def crear_formulario_base(
    codigo: str,
    estado: str = EstadoFormulario.BORRADOR,
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
) -> Formulario:
    """Crea un formulario base para pruebas."""
    return Formulario.objects.create(
        codigo=codigo,
        nombre=f"Nombre {codigo}",
        descripcion=f"Descripcion {codigo}",
        tipo_formulario=TipoFormulario.ENCUESTA,
        estado=estado,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


def crear_version_publicada(formulario: Formulario, numero_version: int = 1) -> FormularioVersion:
    """Crea una version publicada asociada al formulario."""
    return FormularioVersion.objects.create(
        formulario=formulario,
        numero_version=numero_version,
        estado=EstadoFormulario.PUBLICADO,
        es_publicada=True,
        fecha_publicacion=timezone.now(),
    )


def crear_estructura_minima(version: FormularioVersion) -> SeccionFormulario:
    """Crea seccion, pregunta y opcion minimas para pruebas de estructura."""
    TextoFormulario.objects.create(
        formulario_version=version,
        tipo=TipoTextoFormulario.INTRODUCCION,
        contenido="Texto de introduccion",
        orden=1,
    )
    seccion = SeccionFormulario.objects.create(
        formulario_version=version,
        codigo="capitulo_i",
        titulo="Capitulo I",
        descripcion="Descripcion seccion",
        orden=1,
    )
    pregunta = Pregunta.objects.create(
        seccion=seccion,
        codigo="p1",
        texto="Pregunta uno",
        tipo_pregunta=TipoPregunta.NUMERO,
        es_obligatoria=True,
        es_pregunta_filtro=True,
        orden=1,
    )
    OpcionRespuesta.objects.create(
        pregunta=pregunta,
        codigo="opc_1",
        etiqueta="Opcion uno",
        valor="1",
        orden=1,
    )
    return seccion


class FormulariosDisponiblesApiTests(TestCase):
    """Pruebas del endpoint de formularios disponibles."""

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_lista_vacia_sin_formularios_publicados(self) -> None:
        crear_formulario_base(codigo="borrador", estado=EstadoFormulario.BORRADOR)

        respuesta = self.cliente.get(URL_DISPONIBLES)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json(), [])

    def test_lista_con_formulario_publicado_vigente(self) -> None:
        formulario = crear_formulario_base(
            codigo="pub_vigente",
            estado=EstadoFormulario.PUBLICADO,
        )
        crear_version_publicada(formulario)

        respuesta = self.cliente.get(URL_DISPONIBLES)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]["codigo"], "pub_vigente")
        self.assertEqual(datos[0]["uuid"], str(formulario.uuid))
        self.assertEqual(
            datos[0]["estado_disponibilidad"],
            EstadoDisponibilidadFormulario.DISPONIBLE,
        )
        self.assertTrue(datos[0]["puede_iniciar"])
        self.assertEqual(
            datos[0]["etiqueta_estado"],
            EtiquetaEstadoFormulario.DISPONIBLE,
        )

    def test_lista_formulario_publicado_futuro_como_proximamente(self) -> None:
        ahora = timezone.now()
        formulario = crear_formulario_base(
            codigo="futuro",
            estado=EstadoFormulario.PUBLICADO,
            fecha_inicio=ahora + timedelta(days=1),
        )
        crear_version_publicada(formulario)

        respuesta = self.cliente.get(URL_DISPONIBLES)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]["codigo"], "futuro")
        self.assertEqual(
            datos[0]["estado_disponibilidad"],
            EstadoDisponibilidadFormulario.PROXIMAMENTE,
        )
        self.assertFalse(datos[0]["puede_iniciar"])
        self.assertEqual(
            datos[0]["etiqueta_estado"],
            EtiquetaEstadoFormulario.PROXIMAMENTE,
        )

    def test_no_lista_formulario_vencido(self) -> None:
        ahora = timezone.now()
        crear_formulario_base(
            codigo="expirado",
            estado=EstadoFormulario.PUBLICADO,
            fecha_fin=ahora - timedelta(days=1),
        )

        respuesta = self.cliente.get(URL_DISPONIBLES)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json(), [])

    def test_no_lista_formulario_archivado(self) -> None:
        crear_formulario_base(codigo="archivado", estado=EstadoFormulario.ARCHIVADO)

        respuesta = self.cliente.get(URL_DISPONIBLES)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json(), [])

    def test_no_lista_formulario_inactivo(self) -> None:
        crear_formulario_base(codigo="inactivo", estado=EstadoFormulario.INACTIVO)

        respuesta = self.cliente.get(URL_DISPONIBLES)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json(), [])

    def test_no_lista_formulario_borrador(self) -> None:
        crear_formulario_base(codigo="solo_borrador", estado=EstadoFormulario.BORRADOR)

        respuesta = self.cliente.get(URL_DISPONIBLES)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json(), [])

    def test_no_lista_formulario_cerrado(self) -> None:
        crear_formulario_base(codigo="cerrado", estado=EstadoFormulario.CERRADO)

        respuesta = self.cliente.get(URL_DISPONIBLES)

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json(), [])


class FormularioEstructuraApiTests(TestCase):
    """Pruebas del endpoint de estructura de formulario."""

    def setUp(self) -> None:
        self.cliente = APIClient()

    def test_obtener_estructura_formulario_publicado(self) -> None:
        formulario = crear_formulario_base(
            codigo="estructura_ok",
            estado=EstadoFormulario.PUBLICADO,
        )
        version = crear_version_publicada(formulario)
        crear_estructura_minima(version)

        respuesta = self.cliente.get(URL_ESTRUCTURA.format(uuid=formulario.uuid))

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertEqual(datos["codigo"], "estructura_ok")
        self.assertEqual(datos["version"]["numero_version"], 1)
        self.assertEqual(len(datos["textos"]), 1)
        self.assertEqual(len(datos["secciones"]), 1)
        self.assertEqual(datos["secciones"][0]["codigo"], "capitulo_i")
        self.assertEqual(len(datos["secciones"][0]["preguntas"]), 1)
        self.assertEqual(datos["secciones"][0]["preguntas"][0]["codigo"], "p1")
        self.assertEqual(len(datos["secciones"][0]["preguntas"][0]["opciones"]), 1)

    def test_error_404_formulario_futuro_sin_estructura(self) -> None:
        ahora = timezone.now()
        formulario = crear_formulario_base(
            codigo="estructura_futuro",
            estado=EstadoFormulario.PUBLICADO,
            fecha_inicio=ahora + timedelta(days=1),
        )
        version = crear_version_publicada(formulario)
        crear_estructura_minima(version)

        respuesta = self.cliente.get(URL_ESTRUCTURA.format(uuid=formulario.uuid))

        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            respuesta.json()["detalle"],
            MensajesFormularioApi.FORMULARIO_NO_DISPONIBLE,
        )

    def test_error_404_formulario_no_existe(self) -> None:
        uuid_inexistente = "00000000-0000-0000-0000-000000000099"
        respuesta = self.cliente.get(URL_ESTRUCTURA.format(uuid=uuid_inexistente))

        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            respuesta.json()["detalle"],
            MensajesFormularioApi.FORMULARIO_NO_DISPONIBLE,
        )

    def test_error_404_sin_version_publicada(self) -> None:
        formulario = crear_formulario_base(
            codigo="sin_version",
            estado=EstadoFormulario.PUBLICADO,
        )
        FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
            estado=EstadoFormulario.BORRADOR,
            es_publicada=False,
        )

        respuesta = self.cliente.get(URL_ESTRUCTURA.format(uuid=formulario.uuid))

        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            respuesta.json()["detalle"],
            MensajesFormularioApi.VERSION_NO_DISPONIBLE,
        )