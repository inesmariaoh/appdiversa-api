"""
Mapeo de permisos Django a codigos consumidos por el panel administrativo.
"""

from django.contrib.auth.models import AbstractBaseUser

from aplicaciones.usuarios.constantes import (
    GrupoSistema,
    PermisoCodigo,
    permiso_completo,
)


class PermisoFrontend:
    """Codigos de permisos expuestos al frontend del panel administrativo."""

    FORMULARIOS_VER = "formularios.ver"
    FORMULARIOS_EDITAR = "formularios.editar"
    FORMULARIOS_PUBLICAR = "formularios.publicar"
    USUARIOS_VER = "usuarios.ver"
    USUARIOS_EDITAR = "usuarios.editar"

    TODOS_ADMINISTRADOR = (
        FORMULARIOS_VER,
        FORMULARIOS_EDITAR,
        FORMULARIOS_PUBLICAR,
        USUARIOS_VER,
        USUARIOS_EDITAR,
    )


_MAPEO_PERMISO_DJANGO_FRONTEND: dict[str, tuple[str, ...]] = {
    permiso_completo(PermisoCodigo.CONSULTAR_FORMULARIOS_ADMIN): (
        PermisoFrontend.FORMULARIOS_VER,
    ),
    permiso_completo(PermisoCodigo.GESTIONAR_FORMULARIOS): (
        PermisoFrontend.FORMULARIOS_VER,
        PermisoFrontend.FORMULARIOS_EDITAR,
    ),
    permiso_completo(PermisoCodigo.PUBLICAR_FORMULARIOS): (
        PermisoFrontend.FORMULARIOS_PUBLICAR,
    ),
    permiso_completo(PermisoCodigo.VERSIONAR_FORMULARIOS): (
        PermisoFrontend.FORMULARIOS_PUBLICAR,
    ),
    permiso_completo(PermisoCodigo.GESTIONAR_USUARIOS): (
        PermisoFrontend.USUARIOS_VER,
        PermisoFrontend.USUARIOS_EDITAR,
    ),
}


def construir_permisos_frontend(usuario: AbstractBaseUser) -> list[str]:
    """Deriva permisos del panel a partir de grupos y permisos Django."""
    if usuario.groups.filter(name=GrupoSistema.ADMINISTRADOR_GENERAL).exists():
        return sorted(PermisoFrontend.TODOS_ADMINISTRADOR)

    permisos_panel: set[str] = set()
    for permiso_django in usuario.get_all_permissions():
        permisos_panel.update(_MAPEO_PERMISO_DJANGO_FRONTEND.get(permiso_django, ()))
    return sorted(permisos_panel)
