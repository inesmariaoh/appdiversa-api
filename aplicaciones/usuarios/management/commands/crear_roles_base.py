"""
Comando para crear roles base y asignar permisos del sistema.
"""

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from aplicaciones.usuarios.constantes import GrupoSistema, PermisoCodigo


def _obtener_permiso(codename: str) -> Permission:
    """Obtiene un permiso personalizado por codename."""
    return Permission.objects.get(codename=codename)


def _asignar_permisos_grupo(grupo: Group, codenames: tuple[str, ...]) -> None:
    """Asigna permisos personalizados a un grupo."""
    if not codenames:
        grupo.permissions.clear()
        return
    permisos = [_obtener_permiso(codename) for codename in codenames]
    grupo.permissions.set(permisos)


MAPA_PERMISOS_GRUPOS: dict[str, tuple[str, ...]] = {
    GrupoSistema.ADMINISTRADOR_GENERAL: PermisoCodigo.TODOS,
    GrupoSistema.GESTOR_FORMULARIOS: (
        PermisoCodigo.GESTIONAR_FORMULARIOS,
        PermisoCodigo.PUBLICAR_FORMULARIOS,
        PermisoCodigo.VERSIONAR_FORMULARIOS,
        PermisoCodigo.CONSULTAR_FORMULARIOS_ADMIN,
    ),
    GrupoSistema.EDITOR_FORMULARIOS: (
        PermisoCodigo.GESTIONAR_FORMULARIOS,
        PermisoCodigo.CONSULTAR_FORMULARIOS_ADMIN,
    ),
    GrupoSistema.LECTOR_FORMULARIOS: (
        PermisoCodigo.CONSULTAR_FORMULARIOS_ADMIN,
    ),
    GrupoSistema.ANALISTA_DATOS: (
        PermisoCodigo.EXPORTAR_RESPUESTAS,
    ),
    GrupoSistema.ENCUESTADO: (),
}


class Command(BaseCommand):
    """Crea roles base del sistema con permisos parametrizados."""

    help = "Crea roles base y asigna permisos personalizados del sistema."

    def handle(self, *args, **options) -> None:
        """Ejecuta la creacion o actualizacion de roles base."""
        for nombre_grupo, permisos in MAPA_PERMISOS_GRUPOS.items():
            grupo, creado = Group.objects.get_or_create(name=nombre_grupo)
            _asignar_permisos_grupo(grupo, permisos)
            accion = "creado" if creado else "actualizado"
            self.stdout.write(
                self.style.SUCCESS(
                    f"Grupo {nombre_grupo} {accion} con {len(permisos)} permisos.",
                ),
            )
