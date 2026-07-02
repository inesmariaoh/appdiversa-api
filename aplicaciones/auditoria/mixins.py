"""
Mixins y managers para soft delete y auditoria de modelos.
"""

from typing import TYPE_CHECKING, Any

from django.db import models
from django.utils import timezone

from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.contexto import obtener_contexto_auditoria

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet con operaciones de soft delete."""

    def activos(self) -> "SoftDeleteQuerySet":
        """Filtra registros no eliminados logicamente."""
        return self.filter(esta_eliminado=False)

    def eliminados(self) -> "SoftDeleteQuerySet":
        """Filtra registros eliminados logicamente."""
        return self.filter(esta_eliminado=True)

    def eliminar_logicamente(self) -> int:
        """Marca todos los registros del queryset como eliminados."""
        cantidad = 0
        for instancia in self.activos().iterator():
            instancia.eliminar_logicamente()
            cantidad += 1
        return cantidad

    def restaurar(self) -> int:
        """Restaura todos los registros eliminados del queryset."""
        cantidad = 0
        for instancia in self.eliminados().iterator():
            instancia.restaurar()
            cantidad += 1
        return cantidad


class SoftDeleteManager(models.Manager):
    """Manager que expone solo registros activos por defecto."""

    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).activos()


class AuditoriaMixin:
    """Mixin con operaciones de eliminacion logica y restauracion."""

    def _resolver_usuario_auditoria(
        self,
        usuario: "AbstractBaseUser | None",
    ) -> "AbstractBaseUser | None":
        """Resuelve el usuario para auditoria desde parametro o contexto."""
        if usuario is not None:
            return usuario
        contexto = obtener_contexto_auditoria()
        if contexto is not None and contexto.usuario is not None:
            return contexto.usuario
        return None

    def _registrar_operacion_auditoria(
        self,
        accion: str,
        valor_anterior: dict[str, Any],
        valor_nuevo: dict[str, Any] | None = None,
        descripcion: str = "",
    ) -> None:
        """Registra una operacion de auditoria sobre la instancia actual."""
        from aplicaciones.auditoria.servicios import registrar_auditoria

        registrar_auditoria(
            entidad=self.__class__.__name__,
            entidad_id=str(self.pk),
            accion=accion,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            descripcion=descripcion,
        )

    def eliminar_logicamente(
        self,
        usuario: "AbstractBaseUser | None" = None,
    ) -> None:
        """Marca el registro como eliminado y registra la accion."""
        from aplicaciones.auditoria.servicios import crear_snapshot_modelo

        usuario_auditoria = self._resolver_usuario_auditoria(usuario)
        valor_anterior = crear_snapshot_modelo(self)
        self.esta_eliminado = True
        self.fecha_eliminacion = timezone.now()
        self.eliminado_por = usuario_auditoria
        self.save(
            update_fields=[
                "esta_eliminado",
                "fecha_eliminacion",
                "eliminado_por",
                "fecha_modificacion",
            ],
        )
        self._registrar_operacion_auditoria(
            AccionAuditoria.ELIMINAR,
            valor_anterior,
            descripcion="Eliminacion logica del registro.",
        )

    def restaurar(self, usuario: "AbstractBaseUser | None" = None) -> None:
        """Restaura un registro eliminado logicamente."""
        from aplicaciones.auditoria.servicios import crear_snapshot_modelo

        usuario_auditoria = self._resolver_usuario_auditoria(usuario)
        valor_anterior = crear_snapshot_modelo(self)
        self.esta_eliminado = False
        self.fecha_eliminacion = None
        self.eliminado_por = None
        if usuario_auditoria is not None:
            self.modificado_por = usuario_auditoria
        self.save(
            update_fields=[
                "esta_eliminado",
                "fecha_eliminacion",
                "eliminado_por",
                "modificado_por",
                "fecha_modificacion",
            ],
        )
        self._registrar_operacion_auditoria(
            AccionAuditoria.RESTAURAR,
            valor_anterior,
            valor_nuevo=crear_snapshot_modelo(self),
            descripcion="Restauracion logica del registro.",
        )
