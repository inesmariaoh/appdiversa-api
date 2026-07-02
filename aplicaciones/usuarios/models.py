"""
Modelos del modulo de usuarios y permisos personalizados.
"""

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
