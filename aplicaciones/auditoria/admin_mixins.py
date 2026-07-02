"""
Mixins de administracion Django para modelos auditables.
"""

from typing import Any

from django.contrib import admin, messages
from django.db import models

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import crear_snapshot_modelo, registrar_auditoria

CAMPOS_AUDITORIA_READONLY = (
    "fecha_creacion",
    "fecha_modificacion",
    "fecha_eliminacion",
    "creado_por",
    "modificado_por",
    "eliminado_por",
    "esta_eliminado",
)


def _usuario_desde_solicitud(request: Any) -> Any:
    """Retorna el usuario autenticado de una solicitud admin."""
    if request.user.is_authenticated:
        return request.user
    return None


def _obtener_snapshot_previo(obj: models.Model, change: bool) -> dict[str, Any] | None:
    """Obtiene el snapshot previo de un objeto en edicion."""
    if not change or not obj.pk:
        return None
    try:
        instancia_anterior = obj.__class__.todos.get(pk=obj.pk)
        return crear_snapshot_modelo(instancia_anterior)
    except obj.__class__.DoesNotExist:
        return None


def _asignar_usuarios_auditoria_admin(
    request: Any,
    obj: models.Model,
    change: bool,
) -> None:
    """Asigna creado_por y modificado_por desde el usuario del admin."""
    usuario = _usuario_desde_solicitud(request)
    if usuario is None:
        return
    if not change:
        obj.creado_por = usuario
    obj.modificado_por = usuario


class ModeloAuditableAdminMixin:
    """Mixin de admin con auditoria y soft delete."""

    def get_readonly_fields(
        self,
        request: Any,
        obj: models.Model | None = None,
    ) -> tuple[str, ...]:
        """Agrega campos de auditoria como solo lectura."""
        readonly = super().get_readonly_fields(request, obj)
        return tuple(set(readonly) | set(CAMPOS_AUDITORIA_READONLY))

    def save_model(
        self,
        request: Any,
        obj: models.Model,
        form: Any,
        change: bool,
    ) -> None:
        """Asigna usuario de auditoria y registra la accion."""
        valor_anterior = _obtener_snapshot_previo(obj, change)
        _asignar_usuarios_auditoria_admin(request, obj, change)
        super().save_model(request, obj, form, change)

        accion = AccionAuditoria.EDITAR if change else AccionAuditoria.CREAR
        registrar_auditoria(
            entidad=obj.__class__.__name__,
            entidad_id=str(obj.pk),
            accion=accion,
            valor_anterior=valor_anterior,
            valor_nuevo=crear_snapshot_modelo(obj),
        )

    def delete_model(self, request: Any, obj: models.Model) -> None:
        """Elimina logicamente el registro desde el admin."""
        obj.eliminar_logicamente(usuario=_usuario_desde_solicitud(request))

    def delete_queryset(self, request: Any, queryset: models.QuerySet) -> None:
        """Elimina logicamente los registros seleccionados."""
        usuario = _usuario_desde_solicitud(request)
        for instancia in queryset.activos().iterator():
            instancia.eliminar_logicamente(usuario=usuario)

    @admin.action(description="Eliminar logicamente registros seleccionados")
    def eliminar_logicamente_seleccionados(
        self,
        request: Any,
        queryset: models.QuerySet,
    ) -> None:
        """Accion admin para eliminacion logica."""
        usuario = _usuario_desde_solicitud(request)
        cantidad = 0
        for instancia in queryset.activos().iterator():
            instancia.eliminar_logicamente(usuario=usuario)
            cantidad += 1
        messages.success(
            request,
            f"Se eliminaron logicamente {cantidad} registro(s).",
        )

    @admin.action(description="Restaurar registros seleccionados")
    def restaurar_seleccionados(
        self,
        request: Any,
        queryset: models.QuerySet,
    ) -> None:
        """Accion admin para restaurar registros eliminados."""
        usuario = _usuario_desde_solicitud(request)
        cantidad = 0
        for instancia in queryset.eliminados().iterator():
            instancia.restaurar(usuario=usuario)
            cantidad += 1
        messages.success(request, f"Se restauraron {cantidad} registro(s).")
