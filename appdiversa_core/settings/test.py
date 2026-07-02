"""
Configuracion para ejecucion de pruebas automatizadas.

Los archivos subidos durante los tests se almacenan en un directorio
temporal del sistema, no en media/ del proyecto.
"""

import tempfile
from pathlib import Path

from .local import *  # noqa: F403

MEDIA_ROOT = Path(tempfile.mkdtemp(prefix="appdiversa_test_media_"))
