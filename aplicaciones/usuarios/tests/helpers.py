"""
Utilidades compartidas para pruebas del modulo de usuarios.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

from aplicaciones.usuarios.constantes import GrupoSistema, PermisoCodigo

User = get_user_model()

URL_LOGIN = "/api/v1/auth/login/"
URL_LOGOUT = "/api/v1/auth/logout/"
URL_ME = "/api/v1/auth/me/"
URL_PERFIL = "/api/v1/auth/perfil/"
URL_MIS_RESPUESTAS = "/api/v1/auth/mis-respuestas/"
URL_REGISTRO = "/api/v1/auth/registro/"
URL_CAMBIAR_PASSWORD = "/api/v1/auth/cambiar-password/"
URL_SOLICITAR_RESTAURAR = "/api/v1/auth/solicitar-restaurar-password/"
URL_RESTAURAR_PASSWORD = "/api/v1/auth/restaurar-password/"
URL_USUARIOS = "/api/v1/admin/usuarios/"
URL_CONTACTO = "/api/v1/contacto/"
CONTRASENA_PRUEBA = "Contrasena123!"


def inicializar_entorno_usuarios() -> None:
    """Ejecuta comandos base de roles y plantillas de correo."""
    call_command("crear_roles_base")
    call_command("crear_plantillas_correo_base")


def crear_usuario_prueba(
    username: str,
    contrasena: str = CONTRASENA_PRUEBA,
    grupo: str | None = None,
    email: str | None = None,
) -> User:
    """Crea un usuario de prueba con grupo opcional."""
    usuario = User.objects.create_user(
        username=username,
        email=email or f"{username}@example.com",
        password=contrasena,
    )
    if grupo is not None:
        grupo_obj = Group.objects.get(name=grupo)
        usuario.groups.add(grupo_obj)
    return usuario


def autenticar_cliente(cliente, username: str, contrasena: str = CONTRASENA_PRUEBA):
    """Autentica un APIClient mediante login de sesion."""
    return cliente.post(
        URL_LOGIN,
        {"usuario": username, "password": contrasena},
        format="json",
    )


GRUPO_ADMIN = GrupoSistema.ADMINISTRADOR_GENERAL
GRUPO_GESTOR = GrupoSistema.GESTOR_FORMULARIOS
GRUPO_EDITOR = GrupoSistema.EDITOR_FORMULARIOS
GRUPO_LECTOR = GrupoSistema.LECTOR_FORMULARIOS
GRUPO_ENCUESTADO = GrupoSistema.ENCUESTADO
