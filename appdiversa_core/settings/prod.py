"""
Configuracion para entorno de produccion.
"""

from .base import (
    ALLOWED_HOSTS,
    ASGI_APPLICATION,
    AUTH_PASSWORD_VALIDATORS,
    BASE_DIR,
    CORS_ALLOWED_ORIGINS,
    DATABASES,
    DEBUG,
    DEFAULT_AUTO_FIELD,
    INSTALLED_APPS,
    LANGUAGE_CODE,
    MEDIA_ROOT,
    MEDIA_URL,
    MIDDLEWARE,
    REST_FRAMEWORK,
    ROOT_URLCONF,
    SECRET_KEY,
    STATIC_ROOT,
    STATIC_URL,
    TEMPLATES,
    TIME_ZONE,
    USE_I18N,
    USE_TZ,
    WSGI_APPLICATION,
)

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
        "backend": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "backend": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
