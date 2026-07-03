"""
Modelos del modulo de usuarios y permisos personalizados.
"""

from django.conf import settings
from django.db import models

from aplicaciones.usuarios.constantes import PermisoCodigo


class PermisoSistema(models.Model):
    """
    Modelo contenedor para registrar permisos personalizados en Django.
    No almacena datos funcionales; solo define permisos del sistema.
    """

    class Meta:
        verbose_name = "Permiso del sistema"
        verbose_name_plural = "Permisos del sistema"
        permissions = [
            (
                PermisoCodigo.GESTIONAR_FORMULARIOS,
                "Puede gestionar formularios",
            ),
            (
                PermisoCodigo.PUBLICAR_FORMULARIOS,
                "Puede publicar formularios",
            ),
            (
                PermisoCodigo.VERSIONAR_FORMULARIOS,
                "Puede versionar formularios",
            ),
            (
                PermisoCodigo.CONSULTAR_FORMULARIOS_ADMIN,
                "Puede consultar formularios en administracion",
            ),
            (
                PermisoCodigo.EXPORTAR_RESPUESTAS,
                "Puede exportar respuestas",
            ),
            (
                PermisoCodigo.GESTIONAR_USUARIOS,
                "Puede gestionar usuarios",
            ),
        ]


class VerificacionCorreo(models.Model):
    """Estado de verificacion del correo electronico de un usuario."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verificacion_correo",
    )
    verificado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_verificacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Verificación de correo"
        verbose_name_plural = "Verificaciones de correo"

    def __str__(self) -> str:
        estado = "verificado" if self.verificado else "pendiente"
        return f"{self.usuario_id} ({estado})"
