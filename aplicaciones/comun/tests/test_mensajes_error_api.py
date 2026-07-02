"""
Pruebas de normalizacion de mensajes de error y respuesta CSRF.
"""

import json

from django.test import Client, RequestFactory, SimpleTestCase, override_settings
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView

from aplicaciones.comun.constantes_seguridad import MensajesAccesoApi, MensajesErrorApi
from aplicaciones.comun.excepciones_api import manejador_excepciones_api
from aplicaciones.comun.utilidades_mensajes_error import normalizar_mensaje_error_cliente
from aplicaciones.comun.vistas_csrf import respuesta_csrf_fallida


class NormalizarMensajeErrorTests(SimpleTestCase):
    """Pruebas de sanitizacion de mensajes expuestos al cliente."""

    def test_oculta_error_csrf_tecnico(self) -> None:
        mensaje = (
            "CSRF Failed: Origin checking failed - "
            "http://localhost:3000 does not match any trusted origins."
        )
        resultado = normalizar_mensaje_error_cliente(mensaje)
        self.assertEqual(resultado, MensajesErrorApi.SOLICITUD_NO_VALIDA)

    def test_preserva_mensaje_funcional(self) -> None:
        mensaje = "Las credenciales proporcionadas no son válidas."
        resultado = normalizar_mensaje_error_cliente(mensaje)
        self.assertEqual(resultado, mensaje)


class ManejadorExcepcionesApiTests(SimpleTestCase):
    """Pruebas del manejador global de excepciones de la API."""

    def test_permission_denied_csrf_se_sanitiza(self) -> None:
        vista = APIView()
        solicitud = RequestFactory().post("/api/v1/auth/login/")
        respuesta = manejador_excepciones_api(
            PermissionDenied(
                detail="CSRF Failed: CSRF token missing or incorrect.",
            ),
            {"view": vista, "request": solicitud},
        )
        self.assertIsNotNone(respuesta)
        assert respuesta is not None
        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(
            respuesta.data["detalle"],
            MensajesErrorApi.SOLICITUD_NO_VALIDA,
        )


class RespuestaCsrfFallidaTests(SimpleTestCase):
    """Pruebas de la vista de fallo CSRF."""

    def test_respuesta_json_amigable(self) -> None:
        cliente = Client(enforce_csrf_checks=True)
        respuesta = respuesta_csrf_fallida(
            cliente.request().wsgi_request,
            reason="Origin checking failed",
        )
        self.assertEqual(respuesta.status_code, 403)
        cuerpo = json.loads(respuesta.content)
        self.assertEqual(
            cuerpo["detalle"],
            MensajesErrorApi.SOLICITUD_NO_VALIDA,
        )


class ConfiguracionCsrfTests(SimpleTestCase):
    """Pruebas de configuracion CSRF para SPA local."""

    @override_settings(
        CORS_ALLOWED_ORIGINS=["http://localhost:3000"],
        FRONTEND_URL="http://localhost:3000",
        CSRF_TRUSTED_ORIGINS=["http://localhost:3000"],
    )
    def test_origen_frontend_en_confianza_csrf(self) -> None:
        from django.conf import settings

        self.assertIn("http://localhost:3000", settings.CSRF_TRUSTED_ORIGINS)
