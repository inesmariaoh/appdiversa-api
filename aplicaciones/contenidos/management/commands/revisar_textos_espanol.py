"""
Comando para revisar y corregir textos parametrizables en espanol.
"""

from django.core.management.base import BaseCommand

from aplicaciones.contenidos.revision_textos_espanol import (
    ejecutar_revision_textos,
    formatear_reporte_revision,
)


class Command(BaseCommand):
    """Revisa textos parametrizables y aplica correcciones seguras de espanol."""

    help = (
        "Revisa textos parametrizables en la base de datos y aplica "
        "correcciones ortograficas seguras."
    )

    def add_arguments(self, parser) -> None:
        """Registra los modos de ejecucion del comando."""
        grupo = parser.add_mutually_exclusive_group(required=True)
        grupo.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra las correcciones propuestas sin modificar la base de datos.",
        )
        grupo.add_argument(
            "--aplicar",
            action="store_true",
            help="Aplica las correcciones seguras detectadas en la base de datos.",
        )

    def handle(self, *args, **options) -> None:
        """Ejecuta la revision de textos en modo simulacion o aplicacion."""
        aplicar = bool(options.get("aplicar"))
        reporte = ejecutar_revision_textos(aplicar=aplicar)
        resumen = formatear_reporte_revision(reporte)
        self.stdout.write(resumen)

        if aplicar and reporte.total_cambios:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Se aplicaron {reporte.total_cambios} correcciones en la base de datos.",
                ),
            )
        elif not aplicar and reporte.total_cambios:
            self.stdout.write(
                self.style.WARNING(
                    "Modo simulacion: use --aplicar para persistir los cambios.",
                ),
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Revision completada sin cambios pendientes."),
            )
