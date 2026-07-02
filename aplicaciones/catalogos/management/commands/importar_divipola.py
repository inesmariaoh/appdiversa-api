"""
Comando de gestion para importar catalogos DIVIPOLA (departamentos y municipios).
"""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandError

from aplicaciones.catalogos.importacion_divipola import (
    ResumenImportacionDivipola,
    cargar_datos_desde_api,
    cargar_datos_desde_archivo,
    importar_divipola,
)


class Command(BaseCommand):
    """Importa departamentos y municipios desde DIVIPOLA a catalogos parametrizables."""

    help = (
        "Importa departamentos y municipios de Colombia desde DIVIPOLA "
        "(Datos Abiertos Colombia) hacia los catalogos parametrizables."
    )

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--archivo",
            type=str,
            help="Ruta a archivo local JSON o CSV con datos DIVIPOLA.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula la importacion sin persistir cambios en la base de datos.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        archivo = options.get("archivo")
        dry_run = options.get("dry_run", False)

        try:
            filas = self._cargar_filas(archivo)
            resumen = importar_divipola(filas, dry_run=dry_run)
        except (ConnectionError, FileNotFoundError, ValueError) as error:
            raise CommandError(str(error)) from error

        self._mostrar_resumen(resumen, dry_run)

    def _cargar_filas(self, archivo: str | None) -> list[dict[str, Any]]:
        if archivo:
            self.stdout.write(f"Cargando datos DIVIPOLA desde archivo: {archivo}")
            return cargar_datos_desde_archivo(archivo)

        self.stdout.write("Consultando API DIVIPOLA en Datos Abiertos Colombia...")
        return cargar_datos_desde_api()

    def _mostrar_resumen(
        self,
        resumen: ResumenImportacionDivipola,
        dry_run: bool,
    ) -> None:
        if dry_run:
            self.stdout.write(self.style.WARNING("Modo dry-run: no se persistieron cambios."))

        self.stdout.write(self.style.SUCCESS("Importacion DIVIPOLA finalizada."))
        self.stdout.write(f"  Departamentos creados: {resumen.departamentos_creados}")
        self.stdout.write(f"  Departamentos actualizados: {resumen.departamentos_actualizados}")
        self.stdout.write(f"  Municipios creados: {resumen.municipios_creados}")
        self.stdout.write(f"  Municipios actualizados: {resumen.municipios_actualizados}")
        self.stdout.write(f"  Errores: {len(resumen.errores)}")

        for mensaje in resumen.errores:
            self.stdout.write(self.style.ERROR(f"    - {mensaje}"))
