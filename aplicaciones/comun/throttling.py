"""
Ambitos de limitacion de tasa reutilizables para la API publica.
"""


class ScopeThrottle:
    """Nombres de ambitos de throttling parametrizados en settings."""

    LOGIN = "login"
    REGISTRO = "registro"
    CONTACTO = "contacto"
    RESTAURAR_PASSWORD = "restaurar_password"
