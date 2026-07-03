"""
Configuracion base compartida por todos los entornos de AppDiversa API.
"""

import os
import sys
from pathlib import Path

import environ
from corsheaders.defaults import default_headers

from appdiversa_core.settings.opciones_base_datos import construir_opciones_mysql

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1", "0.0.0.0"]),
    CORS_ALLOWED_ORIGINS=(list, []),
    DB_PORT=(str, "3306"),
    DB_SSL_MODE=(str, ""),
    DB_SSL_CA=(str, ""),
    API_INTERNA_TOKEN=(str, ""),
    EMAIL_PORT=(int, 587),
    EMAIL_USE_TLS=(bool, True),
    EMAIL_TIMEOUT=(int, 20),
    NOTIFICACIONES_PROVEEDOR=(str, "dummy"),
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "aplicaciones.comun",
    "aplicaciones.formularios",
    "aplicaciones.respuestas",
    "aplicaciones.sesiones_anonimas",
    "aplicaciones.sincronizacion",
    "aplicaciones.auditoria",
    "aplicaciones.contenidos",
    "aplicaciones.analitica",
    "aplicaciones.catalogos",
    "aplicaciones.archivos",
    "aplicaciones.internacionalizacion",
    "aplicaciones.notificaciones",
    "aplicaciones.exportaciones",
    "aplicaciones.usuarios",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "aplicaciones.comun.middleware_csrf_api.EximirCsrfRutasApiMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "aplicaciones.auditoria.middleware.AuditoriaContextoMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "appdiversa_core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "appdiversa_core.wsgi.application"
ASGI_APPLICATION = "appdiversa_core.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
        "OPTIONS": construir_opciones_mysql(env),
        "TEST": {
            "CHARSET": "utf8mb4",
        },
    },
}

if "test" in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / ".test_db.sqlite3",
        },
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Almacenamiento de archivos: local (disco) o s3 (Amazon S3 o compatible).
STORAGE_BACKEND = env("STORAGE_BACKEND", default="local")
AWS_S3_BUCKET = env("AWS_S3_BUCKET", default="")
AWS_S3_REGION = env("AWS_S3_REGION", default="")
AWS_S3_ACCESS_KEY_ID = env("AWS_S3_ACCESS_KEY_ID", default="")
AWS_S3_SECRET_ACCESS_KEY = env("AWS_S3_SECRET_ACCESS_KEY", default="")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="")
AWS_S3_PUBLIC_BASE_URL = env("AWS_S3_PUBLIC_BASE_URL", default="")
AWS_S3_PREFIJO = env("AWS_S3_PREFIJO", default="")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (
    *default_headers,
    "x-sesion-anonima",
    "x-token-sesion",
)

# Token temporal para endpoints internos hasta integrar Keycloak.
API_INTERNA_TOKEN = env("API_INTERNA_TOKEN")

# Configuracion de correo electronico y notificaciones.
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_DEFAULT_FROM = env("EMAIL_DEFAULT_FROM", default="noreply@appdiversa.local")
DEFAULT_FROM_EMAIL = EMAIL_DEFAULT_FROM
EMAIL_TIMEOUT = env("EMAIL_TIMEOUT")
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")
NOTIFICACIONES_PROVEEDOR = env("NOTIFICACIONES_PROVEEDOR")

if (
    NOTIFICACIONES_PROVEEDOR == "smtp"
    and EMAIL_BACKEND.endswith("console.EmailBackend")
):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

_CSRF_TRUSTED_ORIGINS_ENV = env.list("CSRF_TRUSTED_ORIGINS", default=[])
if _CSRF_TRUSTED_ORIGINS_ENV:
    CSRF_TRUSTED_ORIGINS = _CSRF_TRUSTED_ORIGINS_ENV
else:
    CSRF_TRUSTED_ORIGINS = list(CORS_ALLOWED_ORIGINS)
    _origen_frontend = FRONTEND_URL.rstrip("/")
    if _origen_frontend and _origen_frontend not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_origen_frontend)

CSRF_FAILURE_VIEW = "aplicaciones.comun.vistas_csrf.respuesta_csrf_fallida"
CSRF_COOKIE_SAMESITE = env("CSRF_COOKIE_SAMESITE", default="Lax")

PAGINACION_TAMANO_PAGINA = env.int("PAGINACION_TAMANO_PAGINA", default=25)
PAGINACION_TAMANO_MAXIMO = env.int("PAGINACION_TAMANO_MAXIMO", default=200)

THROTTLE_RATE_LOGIN = env("THROTTLE_RATE_LOGIN", default="10/min")
THROTTLE_RATE_REGISTRO = env("THROTTLE_RATE_REGISTRO", default="5/min")
THROTTLE_RATE_CONTACTO = env("THROTTLE_RATE_CONTACTO", default="5/min")
THROTTLE_RATE_RESTAURAR_PASSWORD = env("THROTTLE_RATE_RESTAURAR_PASSWORD", default="5/min")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "aplicaciones.comun.paginacion.PaginacionEstandar",
    "PAGE_SIZE": PAGINACION_TAMANO_PAGINA,
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "login": THROTTLE_RATE_LOGIN,
        "registro": THROTTLE_RATE_REGISTRO,
        "contacto": THROTTLE_RATE_CONTACTO,
        "restaurar_password": THROTTLE_RATE_RESTAURAR_PASSWORD,
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "aplicaciones.comun.excepciones_api.manejador_excepciones_api",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "AppDiversa API",
    "DESCRIPTION": "API REST del motor de formularios parametrizables AppDiversa 2.0",
    "VERSION": "v1",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Cola de tareas asincronas (Celery + Redis).
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/1")
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
