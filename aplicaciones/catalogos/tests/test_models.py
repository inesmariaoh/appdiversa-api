"""
Pruebas de modelos de catalogos parametrizables.
"""

from django.db import IntegrityError
from django.test import TestCase

from aplicaciones.catalogos.constantes import TiposCatalogo
from aplicaciones.catalogos.models import Catalogo, ItemCatalogo


class CatalogoModelTests(TestCase):
    """Pruebas del modelo Catalogo."""

    def test_crear_catalogo(self) -> None:
        catalogo = Catalogo.objects.create(
            codigo="paises",
            nombre="Paises",
            tipo_catalogo=TiposCatalogo.GEOGRAFICO,
        )
        self.assertEqual(catalogo.codigo, "paises")
        self.assertTrue(catalogo.esta_activo)

    def test_no_duplicar_catalogo_por_codigo(self) -> None:
        Catalogo.objects.create(
            codigo="ocupaciones",
            nombre="Ocupaciones",
            tipo_catalogo=TiposCatalogo.GENERAL,
        )
        with self.assertRaises(IntegrityError):
            Catalogo.objects.create(
                codigo="ocupaciones",
                nombre="Ocupaciones duplicadas",
                tipo_catalogo=TiposCatalogo.GENERAL,
            )


class ItemCatalogoModelTests(TestCase):
    """Pruebas del modelo ItemCatalogo."""

    def setUp(self) -> None:
        self.catalogo = Catalogo.objects.create(
            codigo="departamentos",
            nombre="Departamentos",
            tipo_catalogo=TiposCatalogo.GEOGRAFICO,
        )

    def test_crear_item(self) -> None:
        item = ItemCatalogo.objects.create(
            catalogo=self.catalogo,
            codigo="15",
            nombre="Boyaca",
        )
        self.assertEqual(item.codigo, "15")
        self.assertTrue(item.esta_activo)

    def test_no_duplicar_item_por_catalogo_y_codigo(self) -> None:
        ItemCatalogo.objects.create(
            catalogo=self.catalogo,
            codigo="15",
            nombre="Boyaca",
        )
        with self.assertRaises(IntegrityError):
            ItemCatalogo.objects.create(
                catalogo=self.catalogo,
                codigo="15",
                nombre="Boyaca duplicada",
            )

    def test_jerarquia_item_padre(self) -> None:
        padre = ItemCatalogo.objects.create(
            catalogo=self.catalogo,
            codigo="15",
            nombre="Boyaca",
        )
        hijo = ItemCatalogo.objects.create(
            catalogo=self.catalogo,
            codigo="15001",
            nombre="Tunja",
            item_padre=padre,
        )
        self.assertEqual(hijo.item_padre, padre)
        self.assertEqual(padre.items_hijos.count(), 1)
