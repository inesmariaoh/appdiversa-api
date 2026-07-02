"""
Pruebas del comando y servicio de importacion DIVIPOLA.
"""

from __future__ import annotations

import json
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from aplicaciones.catalogos.constantes import DivipolaConstantes, TiposCatalogo
from aplicaciones.catalogos.importacion_divipola import (
    cargar_datos_desde_archivo,
    importar_divipola,
    normalizar_fila_divipola,
)
from aplicaciones.catalogos.models import Catalogo, ItemCatalogo

FILAS_DIVIPOLA_MUESTRA = [
    {
        "cod_dpto": "05",
        "dpto": "ANTIOQUIA",
        "cod_mpio": "05001",
        "nom_mpio": "MEDELLIN",
    },
    {
        "cod_dpto": "05",
        "dpto": "ANTIOQUIA",
        "cod_mpio": "05002",
        "nom_mpio": "ABEJORRAL",
    },
    {
        "cod_dpto": "11",
        "dpto": "BOGOTA D.C.",
        "cod_mpio": "11001",
        "nom_mpio": "BOGOTA D.C.",
    },
]

FILAS_DIVIPOLA_NOMBRES_ALTERNATIVOS = [
    {
        "codigo_departamento": "08",
        "nombre_departamento": "ATLANTICO",
        "codigo_municipio": "08001",
        "nombre_municipio": "BARRANQUILLA",
    },
]


class ImportarDivipolaServicioTests(TestCase):
    """Pruebas del servicio de importacion DIVIPOLA."""

    def test_normaliza_campos_api_oficial(self) -> None:
        fila = normalizar_fila_divipola(FILAS_DIVIPOLA_MUESTRA[0])
        self.assertIsNotNone(fila)
        assert fila is not None
        self.assertEqual(fila.codigo_departamento, "05")
        self.assertEqual(fila.nombre_departamento, "ANTIOQUIA")
        self.assertEqual(fila.codigo_municipio, "05001")
        self.assertEqual(fila.nombre_municipio, "MEDELLIN")

    def test_normaliza_campos_alternativos(self) -> None:
        fila = normalizar_fila_divipola(FILAS_DIVIPOLA_NOMBRES_ALTERNATIVOS[0])
        self.assertIsNotNone(fila)
        assert fila is not None
        self.assertEqual(fila.codigo_departamento, "08")
        self.assertEqual(fila.codigo_municipio, "08001")

    def test_crea_catalogos(self) -> None:
        importar_divipola(FILAS_DIVIPOLA_MUESTRA)

        catalogo_departamentos = Catalogo.objects.get(
            codigo=DivipolaConstantes.CODIGO_CATALOGO_DEPARTAMENTOS,
        )
        catalogo_municipios = Catalogo.objects.get(
            codigo=DivipolaConstantes.CODIGO_CATALOGO_MUNICIPIOS,
        )

        self.assertEqual(catalogo_departamentos.nombre, "Departamentos")
        self.assertEqual(catalogo_departamentos.tipo_catalogo, TiposCatalogo.JERARQUICO)
        self.assertTrue(catalogo_departamentos.esta_activo)
        self.assertTrue(catalogo_departamentos.es_sistema)
        self.assertEqual(catalogo_municipios.tipo_catalogo, TiposCatalogo.JERARQUICO)
        self.assertTrue(catalogo_municipios.es_sistema)

    def test_crea_departamentos(self) -> None:
        importar_divipola(FILAS_DIVIPOLA_MUESTRA)

        departamentos = ItemCatalogo.objects.filter(
            catalogo__codigo=DivipolaConstantes.CODIGO_CATALOGO_DEPARTAMENTOS,
        )
        self.assertEqual(departamentos.count(), 2)
        antioquia = departamentos.get(codigo="05")
        self.assertEqual(antioquia.nombre, "ANTIOQUIA")
        self.assertEqual(antioquia.valor, "05")
        self.assertEqual(antioquia.codigo_externo, "05")
        self.assertEqual(
            antioquia.metadatos,
            {"fuente": "DIVIPOLA", "recurso": "gdxc-w37w"},
        )

    def test_crea_municipios(self) -> None:
        importar_divipola(FILAS_DIVIPOLA_MUESTRA)

        municipios = ItemCatalogo.objects.filter(
            catalogo__codigo=DivipolaConstantes.CODIGO_CATALOGO_MUNICIPIOS,
        )
        self.assertEqual(municipios.count(), 3)
        medellin = municipios.get(codigo="05001")
        self.assertEqual(medellin.nombre, "MEDELLIN")
        self.assertEqual(medellin.valor, "05001")

    def test_relaciona_municipio_con_departamento(self) -> None:
        importar_divipola(FILAS_DIVIPOLA_MUESTRA)

        departamento = ItemCatalogo.objects.get(
            catalogo__codigo=DivipolaConstantes.CODIGO_CATALOGO_DEPARTAMENTOS,
            codigo="05",
        )
        municipio = ItemCatalogo.objects.get(
            catalogo__codigo=DivipolaConstantes.CODIGO_CATALOGO_MUNICIPIOS,
            codigo="05001",
        )
        self.assertEqual(municipio.item_padre, departamento)
        self.assertEqual(municipio.metadatos["codigo_departamento"], "05")
        self.assertEqual(municipio.metadatos["nombre_departamento"], "ANTIOQUIA")

    def test_ejecucion_idempotente(self) -> None:
        primera = importar_divipola(FILAS_DIVIPOLA_MUESTRA)
        segunda = importar_divipola(FILAS_DIVIPOLA_MUESTRA)

        self.assertEqual(primera.departamentos_creados, 2)
        self.assertEqual(primera.municipios_creados, 3)
        self.assertEqual(segunda.departamentos_creados, 0)
        self.assertEqual(segunda.departamentos_actualizados, 0)
        self.assertEqual(segunda.municipios_creados, 0)
        self.assertEqual(segunda.municipios_actualizados, 0)
        self.assertEqual(
            ItemCatalogo.objects.filter(
                catalogo__codigo=DivipolaConstantes.CODIGO_CATALOGO_MUNICIPIOS,
            ).count(),
            3,
        )

    def test_dry_run_no_persiste(self) -> None:
        resumen = importar_divipola(FILAS_DIVIPOLA_MUESTRA, dry_run=True)

        self.assertEqual(resumen.departamentos_creados, 2)
        self.assertEqual(resumen.municipios_creados, 3)
        self.assertFalse(
            Catalogo.objects.filter(
                codigo=DivipolaConstantes.CODIGO_CATALOGO_DEPARTAMENTOS,
            ).exists(),
        )
        self.assertFalse(ItemCatalogo.objects.exists())

    def test_archivo_local_json_funciona(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            encoding="utf-8",
            delete=False,
        ) as archivo:
            json.dump(FILAS_DIVIPOLA_MUESTRA, archivo)
            ruta = archivo.name

        try:
            filas = cargar_datos_desde_archivo(ruta)
            importar_divipola(filas)
        finally:
            Path(ruta).unlink(missing_ok=True)

        self.assertTrue(
            ItemCatalogo.objects.filter(
                catalogo__codigo=DivipolaConstantes.CODIGO_CATALOGO_MUNICIPIOS,
            ).exists(),
        )

    def test_archivo_local_csv_funciona(self) -> None:
        contenido_csv = (
            "cod_dpto,dpto,cod_mpio,nom_mpio\n"
            "05,ANTIOQUIA,05001,MEDELLIN\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            encoding="utf-8",
            delete=False,
        ) as archivo:
            archivo.write(contenido_csv)
            ruta = archivo.name

        try:
            filas = cargar_datos_desde_archivo(ruta)
            resumen = importar_divipola(filas)
        finally:
            Path(ruta).unlink(missing_ok=True)

        self.assertEqual(resumen.municipios_creados, 1)
        self.assertTrue(
            ItemCatalogo.objects.filter(
                catalogo__codigo=DivipolaConstantes.CODIGO_CATALOGO_MUNICIPIOS,
                codigo="05001",
            ).exists(),
        )

    def test_manejo_filas_invalidas(self) -> None:
        filas = FILAS_DIVIPOLA_MUESTRA + [{"cod_dpto": "99"}]
        resumen = importar_divipola(filas)

        self.assertEqual(len(resumen.errores), 1)
        self.assertIn("Fila 4", resumen.errores[0])
        self.assertEqual(resumen.municipios_creados, 3)


class ImportarDivipolaComandoTests(TestCase):
    """Pruebas del management command importar_divipola."""

    def test_comando_con_archivo_local(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            encoding="utf-8",
            delete=False,
        ) as archivo:
            json.dump(FILAS_DIVIPOLA_MUESTRA, archivo)
            ruta = archivo.name

        salida = StringIO()
        try:
            call_command("importar_divipola", archivo=ruta, stdout=salida)
        finally:
            Path(ruta).unlink(missing_ok=True)

        self.assertIn("Importacion DIVIPOLA finalizada", salida.getvalue())
        self.assertTrue(
            Catalogo.objects.filter(
                codigo=DivipolaConstantes.CODIGO_CATALOGO_DEPARTAMENTOS,
            ).exists(),
        )

    def test_comando_dry_run(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            encoding="utf-8",
            delete=False,
        ) as archivo:
            json.dump(FILAS_DIVIPOLA_MUESTRA, archivo)
            ruta = archivo.name

        salida = StringIO()
        try:
            call_command(
                "importar_divipola",
                archivo=ruta,
                dry_run=True,
                stdout=salida,
            )
        finally:
            Path(ruta).unlink(missing_ok=True)

        self.assertIn("dry-run", salida.getvalue().lower())
        self.assertFalse(Catalogo.objects.exists())

    @patch(
        "aplicaciones.catalogos.management.commands.importar_divipola.cargar_datos_desde_api",
    )
    def test_comando_sin_archivo_usa_api(self, mock_cargar_api: object) -> None:
        mock_cargar_api.return_value = FILAS_DIVIPOLA_MUESTRA
        salida = StringIO()
        call_command("importar_divipola", stdout=salida)

        mock_cargar_api.assert_called_once()
        self.assertIn("Importacion DIVIPOLA finalizada", salida.getvalue())

    def test_comando_archivo_inexistente(self) -> None:
        with self.assertRaises(CommandError):
            call_command("importar_divipola", archivo="ruta/inexistente.json")
