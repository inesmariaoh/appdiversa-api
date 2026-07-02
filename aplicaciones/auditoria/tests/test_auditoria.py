"""
Pruebas del modulo de auditoria transversal.
"""

import uuid

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from aplicaciones.contenidos.models import ConfiguracionInterfaz

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.contexto import (
    ContextoAuditoria,
    establecer_contexto_auditoria,
    limpiar_contexto_auditoria,
    obtener_contexto_auditoria,
)
from aplicaciones.auditoria.middleware import AuditoriaContextoMiddleware
from aplicaciones.auditoria.models import RegistroAuditoria
from aplicaciones.auditoria.servicios import crear_snapshot_modelo, registrar_auditoria
from aplicaciones.formularios.models import EstadoFormulario, Formulario, TipoFormulario


class RegistroAuditoriaTests(TestCase):
    """Pruebas de registro de auditoria."""

    def test_crear_registro_auditoria(self) -> None:
        registrar_auditoria(
            entidad="Formulario",
            entidad_id="1",
            accion=AccionAuditoria.CREAR,
            valor_nuevo={"codigo": "demo"},
            descripcion="Creacion de prueba",
        )

        registro = RegistroAuditoria.objects.first()
        self.assertIsNotNone(registro)
        self.assertEqual(registro.entidad, "Formulario")
        self.assertEqual(registro.accion, AccionAuditoria.CREAR)


class SnapshotModeloTests(TestCase):
    """Pruebas de snapshot seguro de modelos."""

    def test_snapshot_excluye_campos_sensibles(self) -> None:
        formulario = Formulario(
            codigo="snap",
            nombre="Snapshot",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.BORRADOR,
        )
        snapshot = crear_snapshot_modelo(formulario)

        self.assertIn("codigo", snapshot)
        self.assertNotIn("password", snapshot)

    def test_snapshot_serializa_campos_archivo(self) -> None:
        logo = SimpleUploadedFile(
            "logo_institucional.png",
            b"contenido-imagen-falsa",
            content_type="image/png",
        )
        configuracion = ConfiguracionInterfaz.objects.create(
            nombre_aplicativo="App prueba",
            logo_institucional=logo,
        )
        snapshot = crear_snapshot_modelo(configuracion)

        self.assertIn("logo_institucional", snapshot)
        ruta_logo = snapshot["logo_institucional"]
        self.assertIsInstance(ruta_logo, str)
        self.assertTrue(ruta_logo.startswith("interfaz/logos/"))
        self.assertIn("logo_institucional", ruta_logo)
        self.assertTrue(ruta_logo.endswith(".png"))

        registrar_auditoria(
            entidad="ConfiguracionInterfaz",
            entidad_id=str(configuracion.pk),
            accion=AccionAuditoria.EDITAR,
            valor_anterior={"logo_institucional": None},
            valor_nuevo=snapshot,
        )
        self.assertEqual(RegistroAuditoria.objects.count(), 1)


class ContextoAuditoriaTests(TestCase):
    """Pruebas del contexto de auditoria."""

    def test_establecer_y_limpiar_contexto(self) -> None:
        uuid_sesion = str(uuid.uuid4())
        establecer_contexto_auditoria(
            uuid_sesion_anonima=uuid_sesion,
            ip="127.0.0.1",
            user_agent="pytest",
        )

        contexto = obtener_contexto_auditoria()
        self.assertIsNotNone(contexto)
        self.assertEqual(contexto.uuid_sesion_anonima, uuid_sesion)

        limpiar_contexto_auditoria()
        self.assertIsNone(obtener_contexto_auditoria())


class SoftDeleteTests(TestCase):
    """Pruebas de eliminacion logica y restauracion."""

    def setUp(self) -> None:
        self.formulario = Formulario.objects.create(
            codigo="soft_delete",
            nombre="Soft delete",
            tipo_formulario=TipoFormulario.ENCUESTA,
            estado=EstadoFormulario.BORRADOR,
        )

    def test_eliminar_logicamente_marca_esta_eliminado(self) -> None:
        self.formulario.eliminar_logicamente()
        self.formulario.refresh_from_db()

        self.assertTrue(self.formulario.esta_eliminado)
        self.assertIsNotNone(self.formulario.fecha_eliminacion)
        self.assertFalse(Formulario.objects.filter(pk=self.formulario.pk).exists())
        self.assertTrue(Formulario.todos.filter(pk=self.formulario.pk).exists())

    def test_restaurar_marca_esta_eliminado_false(self) -> None:
        self.formulario.eliminar_logicamente()
        instancia = Formulario.todos.get(pk=self.formulario.pk)
        instancia.restaurar()

        self.assertFalse(instancia.esta_eliminado)
        self.assertIsNone(instancia.fecha_eliminacion)
        self.assertTrue(Formulario.objects.filter(pk=self.formulario.pk).exists())


class AuditoriaContextoMiddlewareTests(TestCase):
    """Pruebas del middleware de contexto de auditoria."""

    def test_middleware_registra_uuid_sesion_anonima(self) -> None:
        factory = RequestFactory()
        uuid_sesion = str(uuid.uuid4())
        solicitud = factory.get(
            "/api/v1/sesiones/",
            HTTP_X_SESION_ANONIMA=uuid_sesion,
            HTTP_USER_AGENT="middleware-test",
        )
        solicitud.user = get_user_model()()
        contexto_capturado: list[ContextoAuditoria | None] = []

        def respuesta_dummy(request):
            contexto_capturado.append(obtener_contexto_auditoria())
            from django.http import HttpResponse

            return HttpResponse("ok")

        middleware = AuditoriaContextoMiddleware(respuesta_dummy)
        middleware(solicitud)

        self.assertEqual(len(contexto_capturado), 1)
        self.assertEqual(contexto_capturado[0].uuid_sesion_anonima, uuid_sesion)
        self.assertIsNone(obtener_contexto_auditoria())


class AuditoriaUsuarioTests(TestCase):
    """Pruebas de auditoria con usuario Django."""

    def test_registrar_auditoria_con_usuario(self) -> None:
        usuario = get_user_model().objects.create_user(
            username="auditor",
            password="clave-segura-123",
        )
        establecer_contexto_auditoria(usuario=usuario, ip="10.0.0.1")

        registrar_auditoria(
            entidad="SesionAnonima",
            entidad_id="99",
            accion=AccionAuditoria.INICIAR_SESION,
        )

        registro = RegistroAuditoria.objects.first()
        self.assertEqual(registro.usuario, usuario)
        self.assertEqual(registro.ip, "10.0.0.1")
        limpiar_contexto_auditoria()
