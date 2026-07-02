"""
Pruebas de la API administrativa de formularios.
"""

import uuid

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.models import RegistroAuditoria
from aplicaciones.formularios.constantes_admin import MensajesFormularioAdmin
from aplicaciones.formularios.models import (
    AccionRegla,
    EstadoFormulario,
    OperadorRegla,
    TipoPregunta,
    TipoTextoFormulario,
)
from aplicaciones.formularios.tests.helpers_admin import (
    URL_ADMIN_FORMULARIOS,
    crear_formulario_admin_prueba,
    crear_pregunta_prueba,
    crear_seccion_prueba,
    preparar_entorno_admin,
)
from aplicaciones.respuestas.models import Respuesta
from aplicaciones.sesiones_anonimas.models import SesionAnonima
from aplicaciones.usuarios.tests.helpers import (
    GRUPO_EDITOR,
    GRUPO_GESTOR,
    GRUPO_LECTOR,
    autenticar_cliente,
    crear_usuario_prueba,
)


class FormulariosAdminApiTests(TestCase):
    """Pruebas de endpoints administrativos de formularios."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        preparar_entorno_admin()

    def setUp(self) -> None:
        self.cliente = APIClient()
        self.gestor = crear_usuario_prueba("gestor_form", grupo=GRUPO_GESTOR)
        self.editor = crear_usuario_prueba("editor_form", grupo=GRUPO_EDITOR)
        self.lector = crear_usuario_prueba("lector_form", grupo=GRUPO_LECTOR)

    def test_gestor_crea_formulario(self) -> None:
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.post(
            URL_ADMIN_FORMULARIOS,
            {
                "codigo": "nuevo_form",
                "nombre": "Nuevo formulario",
                "tipo_formulario": "encuesta",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

    def test_editor_no_publica(self) -> None:
        formulario = crear_formulario_admin_prueba("editor_pub")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        crear_pregunta_prueba(seccion)
        autenticar_cliente(self.cliente, "editor_form")
        respuesta = self.cliente.post(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/versiones/{version.pk}/publicar/",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_gestor_publica(self) -> None:
        formulario = crear_formulario_admin_prueba("gestor_pub")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        crear_pregunta_prueba(seccion)
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.post(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/versiones/{version.pk}/publicar/",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertTrue(respuesta.data["es_publicada"])

    def test_lector_solo_consulta(self) -> None:
        crear_formulario_admin_prueba("solo_lectura")
        autenticar_cliente(self.cliente, "lector_form")
        respuesta_get = self.cliente.get(URL_ADMIN_FORMULARIOS)
        self.assertEqual(respuesta_get.status_code, status.HTTP_200_OK)
        respuesta_post = self.cliente.post(
            URL_ADMIN_FORMULARIOS,
            {
                "codigo": "bloqueado",
                "nombre": "Bloqueado",
                "tipo_formulario": "encuesta",
            },
            format="json",
        )
        self.assertEqual(respuesta_post.status_code, status.HTTP_403_FORBIDDEN)

    def test_gestor_obtiene_estructura_admin(self) -> None:
        formulario = crear_formulario_admin_prueba("estructura_admin")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        crear_pregunta_prueba(seccion)
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.get(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/estructura/",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        datos = respuesta.json()
        self.assertEqual(datos["codigo"], "estructura_admin")
        self.assertEqual(datos["version"]["numero_version"], 1)
        self.assertEqual(len(datos["secciones"]), 1)
        self.assertEqual(datos["secciones"][0]["codigo"], "sec1")

    def test_gestor_obtiene_estructura_formulario_publicado(self) -> None:
        formulario = crear_formulario_admin_prueba("estructura_pub")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        crear_pregunta_prueba(seccion)
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta_publicar = self.cliente.post(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/versiones/{version.pk}/publicar/",
        )
        self.assertEqual(respuesta_publicar.status_code, status.HTTP_200_OK)
        respuesta = self.cliente.get(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/estructura/",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.json()["codigo"], "estructura_pub")

    def test_estructura_admin_formulario_inexistente(self) -> None:
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.get(f"{URL_ADMIN_FORMULARIOS}99999/estructura/")
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

    def test_actualizar_pregunta_por_codigo_en_formulario(self) -> None:
        formulario = crear_formulario_admin_prueba("preg_codigo")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        crear_pregunta_prueba(seccion, "P7")
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.patch(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/preguntas/P7/",
            {
                "codigo": "P7",
                "texto": "Texto actualizado",
                "descripcion": "Descripcion actualizada",
                "tipo_pregunta": TipoPregunta.RADIO,
                "es_obligatoria": True,
                "orden": 1,
                "seccion_codigo": seccion.codigo,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["texto"], "Texto actualizado")

    def test_listar_reglas_formulario_admin(self) -> None:
        formulario = crear_formulario_admin_prueba("reglas_form")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        origen = crear_pregunta_prueba(seccion, "origen")
        destino = crear_pregunta_prueba(seccion, "destino")
        destino.orden = 2
        destino.save(update_fields=["orden"])
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta_crear = self.cliente.post(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/reglas/",
            {
                "pregunta_origen": origen.codigo,
                "operador": OperadorRegla.EQUALS,
                "valor_esperado": {"valor": "si"},
                "accion": AccionRegla.MOSTRAR,
                "pregunta_destino": destino.codigo,
            },
            format="json",
        )
        self.assertEqual(respuesta_crear.status_code, status.HTTP_201_CREATED)
        respuesta_lista = self.cliente.get(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/reglas/",
        )
        self.assertEqual(respuesta_lista.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta_lista.data), 1)
        self.assertEqual(respuesta_lista.data[0]["pregunta_origen"], "origen")

    def test_no_autenticado_recibe_401_o_403(self) -> None:
        respuesta = self.cliente.get(URL_ADMIN_FORMULARIOS)
        self.assertIn(
            respuesta.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_soft_delete(self) -> None:
        formulario = crear_formulario_admin_prueba("soft_del")
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.delete(f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertTrue(respuesta.data["esta_eliminado"])

    def test_duplicar_pregunta(self) -> None:
        formulario = crear_formulario_admin_prueba("dup_preg")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        pregunta = crear_pregunta_prueba(seccion)
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.post(
            f"/api/v1/admin/preguntas/{pregunta.pk}/duplicar/",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(respuesta.data["codigo"], pregunta.codigo)

    def test_reordenar_preguntas(self) -> None:
        formulario = crear_formulario_admin_prueba("reorden")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        p1 = crear_pregunta_prueba(seccion, "p1")
        p2 = crear_pregunta_prueba(seccion, "p2")
        p2.orden = 2
        p2.save(update_fields=["orden"])
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.post(
            "/api/v1/admin/preguntas/reordenar/",
            {"preguntas": [{"id": p1.pk, "orden": 2}, {"id": p2.pk, "orden": 1}]},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_crear_regla_valida(self) -> None:
        formulario = crear_formulario_admin_prueba("regla_ok")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        origen = crear_pregunta_prueba(seccion, "origen")
        destino = crear_pregunta_prueba(seccion, "destino")
        destino.orden = 2
        destino.save(update_fields=["orden"])
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.post(
            f"/api/v1/admin/preguntas/{origen.pk}/reglas/",
            {
                "operador": OperadorRegla.EQUALS,
                "valor_esperado": {"valor": "si"},
                "pregunta_destino": destino.pk,
                "accion": AccionRegla.MOSTRAR,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

    def test_regla_invalida_retorna_400(self) -> None:
        formulario = crear_formulario_admin_prueba("regla_bad")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        origen = crear_pregunta_prueba(seccion)
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.post(
            f"/api/v1/admin/preguntas/{origen.pk}/reglas/",
            {
                "operador": OperadorRegla.EQUALS,
                "valor_esperado": {"valor": "si"},
                "accion": AccionRegla.MOSTRAR,
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_publicar_sin_secciones_retorna_400(self) -> None:
        formulario = crear_formulario_admin_prueba("pub_vacio")
        version = formulario.versiones.first()
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.post(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/versiones/{version.pk}/publicar/",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            respuesta.data["detalle"],
            MensajesFormularioAdmin.VERSION_SIN_SECCIONES,
        )

    def test_gestor_cierra_version_publicada(self) -> None:
        formulario = crear_formulario_admin_prueba("cerrar_ver")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        crear_pregunta_prueba(seccion)
        autenticar_cliente(self.cliente, "gestor_form")
        self.cliente.post(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/versiones/{version.pk}/publicar/",
        )
        respuesta = self.cliente.post(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/versiones/{version.pk}/cerrar/",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["estado"], EstadoFormulario.CERRADO)

    def test_crud_seccion_pregunta_opcion_texto(self) -> None:
        formulario = crear_formulario_admin_prueba("crud_full")
        version = formulario.versiones.first()
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta_seccion = self.cliente.post(
            f"/api/v1/admin/versiones/{version.pk}/secciones/",
            {"codigo": "s_crud", "titulo": "Seccion CRUD", "orden": 1},
            format="json",
        )
        self.assertEqual(respuesta_seccion.status_code, status.HTTP_201_CREATED)
        seccion_id = respuesta_seccion.data["id"]
        respuesta_pregunta = self.cliente.post(
            f"/api/v1/admin/secciones/{seccion_id}/preguntas/",
            {
                "codigo": "p_sel",
                "texto": "Seleccione",
                "tipo_pregunta": TipoPregunta.RADIO,
                "orden": 1,
            },
            format="json",
        )
        self.assertEqual(respuesta_pregunta.status_code, status.HTTP_201_CREATED)
        pregunta_id = respuesta_pregunta.data["id"]
        respuesta_opcion = self.cliente.post(
            f"/api/v1/admin/preguntas/{pregunta_id}/opciones/",
            {
                "codigo": "op1",
                "etiqueta": "Opcion 1",
                "valor": "1",
                "orden": 1,
            },
            format="json",
        )
        self.assertEqual(respuesta_opcion.status_code, status.HTTP_201_CREATED)
        respuesta_texto = self.cliente.post(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/textos/",
            {
                "tipo": TipoTextoFormulario.INTRODUCCION,
                "titulo": "Intro",
                "contenido": "Texto introductorio",
                "orden": 1,
            },
            format="json",
        )
        self.assertEqual(respuesta_texto.status_code, status.HTTP_201_CREATED)

    def test_patch_formulario(self) -> None:
        formulario = crear_formulario_admin_prueba("patch_form")
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.patch(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/",
            {"nombre": "Nombre actualizado"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["nombre"], "Nombre actualizado")

    def test_auditoria_al_publicar(self) -> None:
        formulario = crear_formulario_admin_prueba("audit_pub")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        crear_pregunta_prueba(seccion)
        RegistroAuditoria.objects.all().delete()
        autenticar_cliente(self.cliente, "gestor_form")
        self.cliente.post(
            f"{URL_ADMIN_FORMULARIOS}{formulario.pk}/versiones/{version.pk}/publicar/",
        )
        registro = RegistroAuditoria.objects.filter(
            accion=AccionAuditoria.PUBLICAR,
        ).first()
        self.assertIsNotNone(registro)

    def test_no_editar_version_publicada_con_respuestas(self) -> None:
        formulario = crear_formulario_admin_prueba("resp_edit")
        version = formulario.versiones.first()
        version.estado = EstadoFormulario.PUBLICADO
        version.es_publicada = True
        version.save(update_fields=["estado", "es_publicada"])
        seccion = crear_seccion_prueba(version)
        pregunta = crear_pregunta_prueba(seccion)
        sesion = SesionAnonima.objects.create(
            uuid_sesion=uuid.UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"),
            token_cliente="token",
            formulario=formulario,
            version_formulario=version,
        )
        Respuesta.objects.create(sesion=sesion, pregunta=pregunta, valor_texto="x")
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.patch(
            f"/api/v1/admin/preguntas/{pregunta.pk}/",
            {"texto": "Cambio bloqueado"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tooltip_activo_requiere_texto_en_pregunta(self) -> None:
        formulario = crear_formulario_admin_prueba("tooltip_preg")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.post(
            f"/api/v1/admin/secciones/{seccion.pk}/preguntas/",
            {
                "codigo": "p_tooltip",
                "texto": "Pregunta con tooltip",
                "tipo_pregunta": TipoPregunta.RADIO,
                "orden": 1,
                "tiene_tooltip": True,
                "tooltip": "",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            respuesta.data["detalle"],
            MensajesFormularioAdmin.TOOLTIP_TEXTO_OBLIGATORIO,
        )

    def test_tooltip_activo_requiere_texto_en_opcion(self) -> None:
        formulario = crear_formulario_admin_prueba("tooltip_opc")
        version = formulario.versiones.first()
        seccion = crear_seccion_prueba(version)
        pregunta = crear_pregunta_prueba(seccion, "p_radio")
        pregunta.tipo_pregunta = TipoPregunta.RADIO
        pregunta.save(update_fields=["tipo_pregunta"])
        autenticar_cliente(self.cliente, "gestor_form")
        respuesta = self.cliente.post(
            f"/api/v1/admin/preguntas/{pregunta.pk}/opciones/",
            {
                "codigo": "op_tooltip",
                "etiqueta": "Area urbana",
                "valor": "urbana",
                "orden": 1,
                "tiene_tooltip": True,
                "tooltip": "   ",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            respuesta.data["detalle"],
            MensajesFormularioAdmin.TOOLTIP_TEXTO_OBLIGATORIO,
        )
