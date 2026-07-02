"""
Comando para crear usuarios de demostracion con roles predefinidos.
"""

from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand

from aplicaciones.usuarios.constantes import GrupoSistema

User = get_user_model()

CONTRASENA_DEMO_PREDETERMINADA = "AppDiversaDemo123!"


@dataclass(frozen=True)
class UsuarioDemo:
    """Definicion de un usuario de demostracion."""

    username: str
    grupo: str
    email: str


USUARIOS_DEMO: tuple[UsuarioDemo, ...] = (
    UsuarioDemo(
        username="admin_appdiversa",
        grupo=GrupoSistema.ADMINISTRADOR_GENERAL,
        email="admin@appdiversa.local",
    ),
    UsuarioDemo(
        username="gestor_formularios",
        grupo=GrupoSistema.GESTOR_FORMULARIOS,
        email="gestor@appdiversa.local",
    ),
    UsuarioDemo(
        username="editor_formularios",
        grupo=GrupoSistema.EDITOR_FORMULARIOS,
        email="editor@appdiversa.local",
    ),
    UsuarioDemo(
        username="lector_formularios",
        grupo=GrupoSistema.LECTOR_FORMULARIOS,
        email="lector@appdiversa.local",
    ),
)


def _crear_o_actualizar_usuario_demo(
    definicion: UsuarioDemo,
    contrasena: str,
    resetear_contrasena: bool,
) -> tuple[User, bool]:
    """Crea o actualiza un usuario demo con su grupo asignado."""
    grupo = Group.objects.get(name=definicion.grupo)
    usuario, creado = User.objects.get_or_create(
        username=definicion.username,
        defaults={
            "email": definicion.email,
            "is_active": True,
            "is_staff": definicion.grupo == GrupoSistema.ADMINISTRADOR_GENERAL,
        },
    )
    if not creado:
        usuario.email = definicion.email
        usuario.is_active = True
        usuario.is_staff = definicion.grupo == GrupoSistema.ADMINISTRADOR_GENERAL
        usuario.save(update_fields=["email", "is_active", "is_staff"])

    if creado or resetear_contrasena:
        usuario.set_password(contrasena)
        usuario.save(update_fields=["password"])

    usuario.groups.set([grupo])
    return usuario, creado


class Command(BaseCommand):
    """Crea usuarios de demostracion para panel admin y pruebas E2E."""

    help = (
        "Crea usuarios demo (admin_appdiversa, gestor_formularios, "
        "editor_formularios, lector_formularios) con roles del sistema."
    )

    def add_arguments(self, parser) -> None:
        """Registra argumentos del comando."""
        parser.add_argument(
            "--password",
            default=CONTRASENA_DEMO_PREDETERMINADA,
            help="Contrasena inicial para los usuarios demo.",
        )
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Restablece la contrasena aunque el usuario ya exista.",
        )
        parser.add_argument(
            "--sin-roles",
            action="store_true",
            help="Omite la ejecucion previa de crear_grupos_iniciales.",
        )

    def handle(self, *args, **options) -> None:
        """Ejecuta la creacion o actualizacion de usuarios demo."""
        if not options["sin_roles"]:
            call_command("crear_grupos_iniciales")

        contrasena = str(options["password"])
        resetear = bool(options["reset_password"])

        for definicion in USUARIOS_DEMO:
            usuario, creado = _crear_o_actualizar_usuario_demo(
                definicion,
                contrasena,
                resetear,
            )
            accion = "creado" if creado else "actualizado"
            self.stdout.write(
                self.style.SUCCESS(
                    f"Usuario {usuario.username} ({definicion.grupo}) {accion}.",
                ),
            )

        self.stdout.write(
            self.style.WARNING(
                "Contrasena demo: use --password para personalizarla. "
                "Ejecute con --reset-password para restablecer usuarios existentes.",
            ),
        )
