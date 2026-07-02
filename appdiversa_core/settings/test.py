"""
Configuracion para ejecucion de pruebas automatizadas.

Los archivos subidos durante los tests se almacenan en un directorio
temporal del sistema, no en media/ del proyecto.
"""

import tempfile
from pathlib import Path

from .local import *  # noqa: F403

MEDIA_ROOT = Path(tempfile.mkdtemp(prefix="appdiversa_test_media_"))

# Desactiva la limitacion de tasa durante las pruebas para no interferir
# con escenarios que ejecutan multiples solicitudes consecutivas.
REST_FRAMEWORK = {  # noqa: F405
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_THROTTLE_RATES": {
        "login": None,
        "registro": None,
        "contacto": None,
        "restaurar_password": None,
    },
}
