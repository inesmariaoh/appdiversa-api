"""
Selectores de consulta para usuarios y permisos del sistema.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import Q, QuerySet

from aplicaciones.usuarios.constantes import GrupoSistema, PermisoCodigo

User = get_user_model()


def obtener_usuario_por_id(usuario_id: int) -> User | None:
    """Retorna un usuario activo o inactivo por identificador."""
    return User.objects.filter(pk=usuario_id).first()


def obtener_usuario_por_identificador(identificador: str) -> User | None:
    """Busca un usuario por nombre de usuario o correo electronico."""
    identificador_limpio = identificador.strip()
    if not identificador_limpio:
        return None
    return User.objects.filter(
        Q(username__iexact=identificador_limpio)
        | Q(email__iexact=identificador_limpio),
    ).first()


def listar_usuarios_admin() -> QuerySet:
    """Lista usuarios del sistema ordenados por nombre de usuario."""
    return User.objects.all().order_by("username")


def obtener_usuario_por_email(email: str) -> User | None:
    """Busca un usuario activo o inactivo por correo electronico."""
    email_limpio = email.strip()
    if not email_limpio:
        return None
    return User.objects.filter(email__iexact=email_limpio).first()


def existe_username(username: str, excluir_id: int | None = None) -> bool:
    """Indica si ya existe un usuario con el nombre de usuario indicado."""
    consulta = User.objects.filter(username__iexact=username.strip())
    if excluir_id is not None:
        consulta = consulta.exclude(pk=excluir_id)
    return consulta.exists()


def existe_email(email: str, excluir_id: int | None = None) -> bool:
    """Indica si ya existe un usuario con el correo indicado."""
    consulta = User.objects.filter(email__iexact=email.strip())
    if excluir_id is not None:
        consulta = consulta.exclude(pk=excluir_id)
    return consulta.exists()


def listar_grupos_sistema() -> QuerySet[Group]:
    """Lista grupos de roles parametrizados del sistema."""
    return Group.objects.filter(name__in=GrupoSistema.TODOS).order_by("name")


def listar_permisos_personalizados() -> QuerySet[Permission]:
    """Lista permisos personalizados definidos para AppDiversa."""
    return Permission.objects.filter(
        codename__in=PermisoCodigo.TODOS,
    ).select_related("content_type").order_by("codename")


def obtener_grupos_por_nombres(nombres: list[str]) -> QuerySet[Group]:
    """Retorna grupos cuyos nombres coinciden con la lista indicada."""
    return Group.objects.filter(name__in=nombres)


def usuario_tiene_permiso_gestion_usuarios(usuario: User) -> bool:
    """Indica si el usuario puede gestionar otros usuarios."""
    if not usuario.is_authenticated:
        return False
    if usuario.is_superuser:
        return True
    return usuario.has_perm(f"usuarios.{PermisoCodigo.GESTIONAR_USUARIOS}")


def usuario_tiene_permiso_consulta_formularios_admin(usuario: User) -> bool:
    """Indica si el usuario puede consultar formularios en administracion."""
    if not usuario.is_authenticated:
        return False
    if usuario.is_superuser:
        return True
    codigos_consulta = (
        PermisoCodigo.CONSULTAR_FORMULARIOS_ADMIN,
        PermisoCodigo.GESTIONAR_FORMULARIOS,
        PermisoCodigo.PUBLICAR_FORMULARIOS,
        PermisoCodigo.VERSIONAR_FORMULARIOS,
    )
    return any(
        usuario.has_perm(f"usuarios.{codigo}") for codigo in codigos_consulta
    )


def usuario_tiene_permiso_editar_formularios(usuario: User) -> bool:
    """Indica si el usuario puede editar formularios en borrador."""
    if not usuario.is_authenticated:
        return False
    if usuario.is_superuser:
        return True
    return usuario.has_perm(f"usuarios.{PermisoCodigo.GESTIONAR_FORMULARIOS}")


def usuario_tiene_permiso_publicar_formularios(usuario: User) -> bool:
    """Indica si el usuario puede publicar o versionar formularios."""
    if not usuario.is_authenticated:
        return False
    if usuario.is_superuser:
        return True
    return usuario.has_perm(
        f"usuarios.{PermisoCodigo.PUBLICAR_FORMULARIOS}",
    ) or usuario.has_perm(f"usuarios.{PermisoCodigo.VERSIONAR_FORMULARIOS}")


def usuario_tiene_permiso_exportar_respuestas(usuario: User) -> bool:
    """Indica si el usuario puede exportar respuestas para analisis."""
    if not usuario.is_authenticated:
        return False
    if usuario.is_superuser:
        return True
    return usuario.has_perm(f"usuarios.{PermisoCodigo.EXPORTAR_RESPUESTAS}")
