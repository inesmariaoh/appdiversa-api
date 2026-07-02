#!/usr/bin/env python
"""Punto de entrada de comandos de administracion de Django."""

import os
import sys


def main() -> None:
    """Ejecuta tareas de administracion de Django."""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        os.environ["DJANGO_SETTINGS_MODULE"] = "appdiversa_core.settings.test"
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appdiversa_core.settings.local")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Verifique que este instalado y "
            "disponible en el entorno virtual activo."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
