"""
Utilidades para detectar opciones que activan un campo de texto libre (otro).
"""

import re
import unicodedata

_PATRON_ETIQUETA_CAMPO_OTRO = re.compile(
    r"(?i)"
    r"^(otro|otros|otra|otras)\b"
    r"|"
    r"(?:\?\s*|\b)(cu[aá]l|cu[aá]les)\b"
    r"|"
    r"¿\s*(cu[aá]l|cu[aá]les)\b",
)


def _normalizar_etiqueta(etiqueta: str) -> str:
    """Normaliza la etiqueta eliminando acentos para comparaciones consistentes."""
    texto = unicodedata.normalize("NFD", etiqueta.strip().lower())
    return "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")


def etiqueta_activa_campo_otro(etiqueta: str) -> bool:
    """Indica si la etiqueta sugiere que la opcion requiere texto adicional."""
    if not etiqueta.strip():
        return False
    return _PATRON_ETIQUETA_CAMPO_OTRO.search(_normalizar_etiqueta(etiqueta)) is not None


def resolver_activa_otro(opcion_activa_otro: bool, permite_otro: bool, etiqueta: str) -> bool:
    """Resuelve si una opcion debe activar el campo otro en la interfaz."""
    if not permite_otro:
        return False
    if opcion_activa_otro:
        return True
    return etiqueta_activa_campo_otro(etiqueta)
