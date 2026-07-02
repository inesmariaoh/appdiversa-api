"""
Pruebas del motor transversal de notificaciones.
"""

import uuid

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.notificaciones.constantes import (
    EstadoNotificacion,
    MensajesNotificacionApi,
    TipoNotificacion,
)
from aplicaciones.notificaciones.excepciones import (
    NotificacionNoEncontradaError,
    PlantillaNotificacionNoEncontradaError,
)
from aplicaciones.notificaciones.models import Notificacion, PlantillaNotificacion
from aplicaciones.notificaciones.plantillas import renderizar_plantilla
from aplicaciones.notificaciones.proveedores import (
    ProveedorCorreoSMTP,
    ProveedorDummy,
    obtener_proveedor_notificacion,
)
from aplicaciones.notificaciones.servicios import (
    generar_notificacion,
    marcar_enviada,
    marcar_fallida,
    obtener_notificacion,
    probar_notificacion,
    registrar_notificacion,
)
from aplicaciones.comun.tests.helpers_seguridad import (
    TOKEN_API_INTERNA_PRUEBA,
    headers_api_interna,
)

URL_NOTIFICACIONES = "/api/v1/notificaciones/"


def crear_plantilla_prueba() -> PlantillaNotificacion:
    """Crea una plantilla de correo con variables para pruebas."""
    return PlantillaNotificacion.objects.create(
        codigo="bienvenida_correo",
        nombre="Bienvenida por correo",
        tipo=TipoNotificacion.CORREO,
        asunto="Hola {{nombre}}",
        contenido_html="<p>Correo: {{correo}} Formulario: {{formulario}}</p>",
        contenido_texto="Codigo: {{codigo}} Fecha: {{fecha}} Sesion: {{uuid_sesion}}",
        variables_disponibles=[
            "nombre",
            "correo",
            "formulario",
            "fecha",
            "codigo",
            "uuid_sesion",
        ],
        esta_activa=True,
    )


class NotificacionesPlantillasTests(TestCase):
    """Pruebas de renderizado de plantillas."""

    def test_renderizar_variables(self) -> None:
        contenido = "Hola {{nombre}}, tu correo es {{correo}}"
        variables = {"nombre": "Ana", "correo": "ana@ejemplo.com"}
        resultado = renderizar_plantilla(contenido, variables)
        self.assertEqual(resultado, "Hola Ana, tu correo es ana@ejemplo.com")

    def test_renderizar_variables_faltantes(self) -> None:
        resultado = renderizar_plantilla("{{codigo}}", {})
        self.assertEqual(resultado, "")


class NotificacionesServiciosTests(TestCase):
    """Pruebas de servicios del motor de notificaciones."""

    def setUp(self) -> None:
        self.plantilla = crear_plantilla_prueba()

    def test_crear_plantilla(self) -> None:
        self.assertEqual(self.plantilla.codigo, "bienvenida_correo")
        self.assertTrue(self.plantilla.esta_activa)

    def test_generar_notificacion(self) -> None:
        variables = {
            "nombre": "Carlos",
            "correo": "carlos@ejemplo.com",
            "formulario": "encuesta_01",
            "fecha": "2026-06-28",
            "codigo": "ABC123",
            "uuid_sesion": "sesion-uuid-001",
        }
        notificacion = generar_notificacion(
            codigo_plantilla="bienvenida_correo",
            destinatario="carlos@ejemplo.com",
            variables=variables,
        )
        self.assertEqual(notificacion.estado, EstadoNotificacion.PENDIENTE)
        self.assertEqual(notificacion.asunto_generado, "Hola Carlos")
        self.assertIn("carlos@ejemplo.com", notificacion.contenido_generado)
        self.assertIn("encuesta_01", notificacion.contenido_generado)
        self.assertIn("carlos@ejemplo.com", notificacion.contenido_texto_generado)
        self.assertIn("encuesta_01", notificacion.contenido_html_generado)
        self.assertEqual(notificacion.variables_utilizadas["codigo"], "ABC123")

    def test_registrar_notificacion(self) -> None:
        notificacion = generar_notificacion(
            codigo_plantilla="bienvenida_correo",
            destinatario="registro@ejemplo.com",
            variables={"nombre": "Laura"},
        )
        registrada = registrar_notificacion(notificacion)
        self.assertIsNotNone(registrada.pk)
        self.assertTrue(
            Notificacion.objects.filter(uuid=registrada.uuid).exists(),
        )

    def test_marcar_enviada(self) -> None:
        notificacion = registrar_notificacion(
            generar_notificacion(
                codigo_plantilla="bienvenida_correo",
                destinatario="enviada@ejemplo.com",
            ),
        )
        actualizada = marcar_enviada(
            notificacion,
            respuesta_proveedor={"proveedor": "dummy"},
        )
        self.assertEqual(actualizada.estado, EstadoNotificacion.ENVIADA)
        self.assertIsNotNone(actualizada.fecha_envio)
        self.assertEqual(actualizada.numero_intentos, 1)

    def test_marcar_fallida(self) -> None:
        notificacion = registrar_notificacion(
            generar_notificacion(
                codigo_plantilla="bienvenida_correo",
                destinatario="fallida@ejemplo.com",
            ),
        )
        actualizada = marcar_fallida(
            notificacion,
            error_envio="No fue posible completar el envio.",
        )
        self.assertEqual(actualizada.estado, EstadoNotificacion.FALLIDA)
        self.assertEqual(actualizada.numero_intentos, 1)

    def test_plantilla_inexistente(self) -> None:
        with self.assertRaises(PlantillaNotificacionNoEncontradaError):
            generar_notificacion(
                codigo_plantilla="no_existe",
                destinatario="test@ejemplo.com",
            )

    def test_obtener_notificacion_inexistente(self) -> None:
        with self.assertRaises(NotificacionNoEncontradaError):
            obtener_notificacion(uuid.uuid4())


class ProveedorDummyTests(TestCase):
    """Pruebas del proveedor simulado de notificaciones."""

    def test_proveedor_dummy_registra_sin_envio_externo(self) -> None:
        plantilla = crear_plantilla_prueba()
        notificacion = Notificacion(
            plantilla=plantilla,
            canal=plantilla.tipo,
            destinatario="dummy@ejemplo.com",
            estado=EstadoNotificacion.PENDIENTE,
        )
        proveedor = ProveedorDummy()
        respuesta = proveedor.enviar(notificacion)
        self.assertEqual(respuesta["proveedor"], "dummy")
        self.assertEqual(respuesta["estado"], "registrado")


class ProveedorSmtpTests(TestCase):
    """Pruebas del proveedor SMTP de notificaciones."""

    @override_settings(NOTIFICACIONES_PROVEEDOR="dummy")
    def test_factory_usa_dummy_por_defecto(self) -> None:
        proveedor = obtener_proveedor_notificacion()
        self.assertIsInstance(proveedor, ProveedorDummy)

    @override_settings(NOTIFICACIONES_PROVEEDOR="smtp")
    def test_factory_usa_smtp_cuando_configurado(self) -> None:
        proveedor = obtener_proveedor_notificacion()
        self.assertIsInstance(proveedor, ProveedorCorreoSMTP)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        EMAIL_DEFAULT_FROM="test@appdiversa.local",
    )
    def test_proveedor_smtp_usa_email_multi_alternatives(self) -> None:
        from django.core import mail

        plantilla = crear_plantilla_prueba()
        notificacion = Notificacion(
            plantilla=plantilla,
            canal=plantilla.tipo,
            destinatario="smtp@ejemplo.com",
            asunto_generado="Asunto prueba",
            contenido_texto_generado="Texto plano de prueba",
            contenido_html_generado="<p>Contenido HTML</p>",
            estado=EstadoNotificacion.PENDIENTE,
        )
        proveedor = ProveedorCorreoSMTP()
        respuesta = proveedor.enviar(notificacion)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["smtp@ejemplo.com"])
        self.assertEqual(mail.outbox[0].body, "Texto plano de prueba")
        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual(respuesta["proveedor"], "smtp")
        self.assertEqual(respuesta["estado"], "enviado")


class PlantillasCorreoBaseTests(TestCase):
    """Pruebas del comando de plantillas base de correo."""

    def test_renderizar_variables_contacto(self) -> None:
        from django.core.management import call_command

        call_command("crear_plantillas_correo_base")
        plantilla = PlantillaNotificacion.objects.get(codigo="contacto_recibido")
        variables = {
            "nombre": "Ana",
            "correo": "ana@ejemplo.com",
            "asunto": "Consulta",
            "mensaje": "Necesito ayuda",
        }
        asunto = renderizar_plantilla(plantilla.asunto, variables)
        contenido = renderizar_plantilla(plantilla.contenido_texto, variables)
        self.assertIn("Consulta", asunto)
        self.assertIn("Necesito ayuda", contenido)

    def test_plantillas_base_tienen_ortografia_correcta(self) -> None:
        from django.core.management import call_command

        call_command("crear_plantillas_correo_base")
        restaurar = PlantillaNotificacion.objects.get(codigo="restaurar_password")
        bienvenida = PlantillaNotificacion.objects.get(codigo="usuario_creado")
        self.assertEqual(restaurar.nombre, "Restaurar contraseña")
        self.assertIn("contraseña", restaurar.asunto)
        self.assertIn("Iniciar sesión", bienvenida.contenido_html)

    def test_plantillas_base_creadas(self) -> None:
        from django.core.management import call_command

        call_command("crear_plantillas_correo_base")
        codigos_esperados = (
            "restaurar_password",
            "usuario_creado",
            "confirmacion_registro",
            "formulario_finalizado",
            "copia_respuestas_formulario",
            "contacto_recibido",
        )
        for codigo in codigos_esperados:
            self.assertTrue(
                PlantillaNotificacion.objects.filter(codigo=codigo, esta_activa=True).exists(),
            )


@override_settings(API_INTERNA_TOKEN=TOKEN_API_INTERNA_PRUEBA)
class NotificacionesApiTests(TestCase):
    """Pruebas de endpoints de la API de notificaciones."""

    def setUp(self) -> None:
        self.cliente = APIClient()
        crear_plantilla_prueba()

    def test_listar_notificaciones(self) -> None:
        probar_notificacion(
            codigo_plantilla="bienvenida_correo",
            destinatario="lista@ejemplo.com",
            variables={"nombre": "Usuario"},
        )
        respuesta = self.cliente.get(URL_NOTIFICACIONES, **headers_api_interna())
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(respuesta.data), 1)

    def test_detalle_notificacion(self) -> None:
        notificacion = probar_notificacion(
            codigo_plantilla="bienvenida_correo",
            destinatario="detalle@ejemplo.com",
        )
        url = f"{URL_NOTIFICACIONES}{notificacion.uuid}/"
        respuesta = self.cliente.get(url, **headers_api_interna())
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["destinatario"], "detalle@ejemplo.com")

    def test_detalle_notificacion_inexistente(self) -> None:
        url = f"{URL_NOTIFICACIONES}{uuid.uuid4()}/"
        respuesta = self.cliente.get(url, **headers_api_interna())
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            respuesta.data["detalle"],
            MensajesNotificacionApi.NOTIFICACION_NO_ENCONTRADA,
        )

    def test_probar_notificacion_endpoint(self) -> None:
        respuesta = self.cliente.post(
            f"{URL_NOTIFICACIONES}probar/",
            {
                "codigo_plantilla": "bienvenida_correo",
                "destinatario": "probar@ejemplo.com",
                "variables": {"nombre": "Prueba"},
            },
            format="json",
            **headers_api_interna(),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data["estado"], EstadoNotificacion.ENVIADA)

    def test_probar_notificacion_plantilla_invalida(self) -> None:
        respuesta = self.cliente.post(
            f"{URL_NOTIFICACIONES}probar/",
            {
                "codigo_plantilla": "invalida",
                "destinatario": "error@ejemplo.com",
            },
            format="json",
            **headers_api_interna(),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            respuesta.data["detalle"],
            MensajesNotificacionApi.PLANTILLA_NO_ENCONTRADA,
        )
