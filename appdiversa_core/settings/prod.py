"""
Configuracion para entorno de produccion.

Hereda todos los ajustes de base (CORS, CSRF, correo, base de datos) y solo
sobrescribe seguridad y almacenamiento de estaticos para el despliegue.
"""

from .base import *  # noqa: F403
from .base import MIDDLEWARE

# WhiteNoise sirve estaticos del admin y DRF cuando no hay CDN delante.
_MIDDLEWARE_SIN_SEGURIDAD = [
    middleware
    for middleware in MIDDLEWARE
    if middleware != "django.middleware.security.SecurityMiddleware"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *_MIDDLEWARE_SIN_SEGURIDAD,
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
