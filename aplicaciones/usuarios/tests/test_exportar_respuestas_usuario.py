"""
Pruebas de la descarga del historial de respuestas del usuario autenticado.
"""

import uuid
from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.exportaciones.constantes import FormatoExportacion
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
from aplicaciones.usuarios.tests.helpers import (
    CONTRASENA_PRUEBA,
    URL_LOGIN,
    crear_usuario_prueba,
    inicializar_entorno_usuarios,
)


def _crear_sesion_con_respuesta(usuario) -> SesionAnonima:
    """Crea una sesion vinculada al usuario con una respuesta."""
    sufijo = uuid.uuid4().hex[:8]
    formulario = Formulario.objects.create(
        codigo=f"form_hist_{sufijo}",
        nombre="Formulario historial",
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
        usuario=usuario,
    )
    seccion = SeccionFormulario.objects.create(
        formulario_version=version,
        codigo=f"sec_hist_{sufijo}",
        titulo="Seccion historial",
        orden=1,
    )
    pregunta = Pregunta.objects.create(
        seccion=seccion,
        codigo=f"P_HIST_{sufijo}",
        texto="Pregunta historial",
        tipo_pregunta=TipoPregunta.NUMERO,
        orden=1,
    )
    Respuesta.objects.create(sesion=sesion, pregunta=pregunta, valor_numero=Decimal("7"))
    return sesion


class ExportarRespuestasUsuarioTests(TestCase):
    """Pruebas del endpoint de descarga del historial del usuario."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.usuario = crear_usuario_prueba("usuario_hist")
        self.sesion = _crear_sesion_con_respuesta(self.usuario)

    def _autenticar(self) -> None:
        self.cliente.post(
            URL_LOGIN,
            {"username": self.usuario.username, "password": CONTRASENA_PRUEBA},
            format="json",
        )

    def _url(self, uuid_sesion, formato: str) -> str:
        return f"/api/v1/auth/mis-respuestas/{uuid_sesion}/exportar/?formato={formato}"

    def test_descarga_pdf_de_sesion_propia(self) -> None:
        self._autenticar()
        respuesta = self.cliente.get(
            self._url(self.sesion.uuid_sesion, FormatoExportacion.PDF),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta["Content-Type"], "application/pdf")
        self.assertEqual(respuesta.content[:4], b"%PDF")

    def test_descarga_requiere_autenticacion(self) -> None:
        respuesta = self.cliente.get(
            self._url(self.sesion.uuid_sesion, FormatoExportacion.XLSX),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_formato_no_soportado(self) -> None:
        self._autenticar()
        respuesta = self.cliente.get(
            self._url(self.sesion.uuid_sesion, FormatoExportacion.SQL),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sesion_ajena_retorna_404(self) -> None:
        otro = crear_usuario_prueba("usuario_ajeno")
        sesion_ajena = _crear_sesion_con_respuesta(otro)
        self._autenticar()
        respuesta = self.cliente.get(
            self._url(sesion_ajena.uuid_sesion, FormatoExportacion.PDF),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
