"""
Pruebas de la API administrativa de catalogos parametrizables.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from aplicaciones.catalogos.models import Catalogo, ItemCatalogo
from aplicaciones.usuarios.tests.helpers import (
    GRUPO_ADMIN,
    GRUPO_ENCUESTADO,
    autenticar_cliente,
    crear_usuario_prueba,
    inicializar_entorno_usuarios,
)

URL_CATALOGOS = "/api/v1/admin/catalogos/"


def _url_catalogo(catalogo_id: int) -> str:
    return f"{URL_CATALOGOS}{catalogo_id}/"


def _url_items(catalogo_id: int) -> str:
    return f"{URL_CATALOGOS}{catalogo_id}/items/"


def _url_item(item_id: int) -> str:
    return f"{URL_CATALOGOS}items/{item_id}/"


class CatalogosAdminTests(TestCase):
    """Pruebas del CRUD administrativo de catalogos."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        inicializar_entorno_usuarios()

    def setUp(self) -> None:
        self.cliente = APIClient()

    def _autenticar_admin(self) -> None:
        crear_usuario_prueba("admin_catalogos", grupo=GRUPO_ADMIN)
        autenticar_cliente(self.cliente, "admin_catalogos")

    def _crear_catalogo(self, codigo: str = "ocupaciones") -> Catalogo:
        return Catalogo.objects.create(
            codigo=codigo,
            nombre="Ocupaciones",
            tipo_catalogo="general",
        )

    def test_listado_requiere_autenticacion(self) -> None:
        respuesta = self.cliente.get(URL_CATALOGOS)
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rol_sin_permiso_no_accede(self) -> None:
        crear_usuario_prueba("encuestado_cat", grupo=GRUPO_ENCUESTADO)
        autenticar_cliente(self.cliente, "encuestado_cat")
        respuesta = self.cliente.get(URL_CATALOGOS)
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_crear_catalogo(self) -> None:
        self._autenticar_admin()
        respuesta = self.cliente.post(
            URL_CATALOGOS,
            {"codigo": "estratos", "nombre": "Estratos", "tipo_catalogo": "socioeconomico"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Catalogo.objects.filter(codigo="estratos").exists())

    def test_crear_catalogo_duplicado(self) -> None:
        self._autenticar_admin()
        self._crear_catalogo()
        respuesta = self.cliente.post(
            URL_CATALOGOS,
            {"codigo": "ocupaciones", "nombre": "Otro", "tipo_catalogo": "general"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_listar_catalogos_paginado(self) -> None:
        self._autenticar_admin()
        self._crear_catalogo()
        respuesta = self.cliente.get(URL_CATALOGOS)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(respuesta.data["count"], 1)

    def test_actualizar_catalogo(self) -> None:
        self._autenticar_admin()
        catalogo = self._crear_catalogo()
        respuesta = self.cliente.patch(
            _url_catalogo(catalogo.pk),
            {"nombre": "Ocupaciones actualizadas"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        catalogo.refresh_from_db()
        self.assertEqual(catalogo.nombre, "Ocupaciones actualizadas")

    def test_eliminar_catalogo(self) -> None:
        self._autenticar_admin()
        catalogo = self._crear_catalogo()
        respuesta = self.cliente.delete(_url_catalogo(catalogo.pk))
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        catalogo.refresh_from_db()
        self.assertTrue(catalogo.esta_eliminado)

    def test_eliminar_catalogo_sistema_protegido(self) -> None:
        self._autenticar_admin()
        catalogo = Catalogo.objects.create(
            codigo="sistema_cat",
            nombre="Sistema",
            tipo_catalogo="general",
            es_sistema=True,
        )
        respuesta = self.cliente.delete(_url_catalogo(catalogo.pk))
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crear_item(self) -> None:
        self._autenticar_admin()
        catalogo = self._crear_catalogo()
        respuesta = self.cliente.post(
            _url_items(catalogo.pk),
            {"codigo": "medico", "nombre": "Médico"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ItemCatalogo.objects.filter(catalogo=catalogo, codigo="medico").exists())

    def test_crear_item_duplicado(self) -> None:
        self._autenticar_admin()
        catalogo = self._crear_catalogo()
        ItemCatalogo.objects.create(catalogo=catalogo, codigo="medico", nombre="Médico")
        respuesta = self.cliente.post(
            _url_items(catalogo.pk),
            {"codigo": "medico", "nombre": "Otro"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crear_item_con_padre_inexistente(self) -> None:
        self._autenticar_admin()
        catalogo = self._crear_catalogo()
        respuesta = self.cliente.post(
            _url_items(catalogo.pk),
            {"codigo": "hijo", "nombre": "Hijo", "codigo_padre": "inexistente"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

    def test_actualizar_item(self) -> None:
        self._autenticar_admin()
        catalogo = self._crear_catalogo()
        item = ItemCatalogo.objects.create(catalogo=catalogo, codigo="medico", nombre="Médico")
        respuesta = self.cliente.patch(
            _url_item(item.pk),
            {"nombre": "Médico general"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.nombre, "Médico general")

    def test_eliminar_item(self) -> None:
        self._autenticar_admin()
        catalogo = self._crear_catalogo()
        item = ItemCatalogo.objects.create(catalogo=catalogo, codigo="medico", nombre="Médico")
        respuesta = self.cliente.delete(_url_item(item.pk))
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        item.refresh_from_db()
        self.assertTrue(item.esta_eliminado)
