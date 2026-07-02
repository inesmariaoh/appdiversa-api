"""
Modelos de contenidos y parametrizacion de interfaz.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models

from aplicaciones.archivos.constantes import REFERENCIA_MODELO_ARCHIVO_REPOSITORIO
from aplicaciones.auditoria.models import AuditoriaModeloAbstracto
from aplicaciones.contenidos.constantes import RUTA_CARGA_FAVICON_INTERFAZ

RUTA_CARGA_LOGOS_INTERFAZ = "interfaz/logos/"


class ConfiguracionInterfaz(AuditoriaModeloAbstracto):
    """Parametrizacion visual de la interfaz del aplicativo."""

    nombre_aplicativo = models.CharField(max_length=255)
    nombre_corto = models.CharField(max_length=100, blank=True)
    descripcion_aplicativo = models.TextField(blank=True)
    texto_pie_pagina = models.CharField(max_length=255, blank=True)
    texto_titulo_seccion_encuestas = models.CharField(max_length=255, blank=True)
    texto_descripcion_seccion_encuestas = models.TextField(blank=True)
    email_soporte = models.EmailField(
        blank=True,
        verbose_name="Correo de soporte",
        help_text=(
            "Destino del formulario de contacto y referencia visible en términos."
        ),
    )
    email_remitente_notificaciones = models.EmailField(
        blank=True,
        verbose_name="Correo remitente de notificaciones",
        help_text=(
            "Remitente de correos del sistema. Si está vacío, se usa EMAIL_DEFAULT_FROM."
        ),
    )
    texto_terminos_condiciones = models.TextField(blank=True)
    texto_autorizacion_datos = models.TextField(blank=True)
    texto_verificacion_exitosa_titulo = models.CharField(max_length=255, blank=True)
    texto_verificacion_exitosa_cuerpo = models.TextField(blank=True)
    texto_confirmacion_envio_titulo = models.CharField(max_length=255, blank=True)
    texto_confirmacion_envio_subtitulo = models.TextField(blank=True)
    meta_titulo_seo = models.CharField(max_length=255, blank=True)
    meta_descripcion_seo = models.TextField(blank=True)
    accion_lengua_senas_habilitada = models.BooleanField(default=False)
    url_lengua_senas = models.URLField(blank=True)
    texto_lengua_senas = models.CharField(max_length=255, blank=True)
    logo_principal = models.ImageField(
        upload_to=RUTA_CARGA_LOGOS_INTERFAZ,
        null=True,
        blank=True,
    )
    logo_secundario = models.ImageField(
        upload_to=RUTA_CARGA_LOGOS_INTERFAZ,
        null=True,
        blank=True,
    )
    logo_institucional = models.ImageField(
        upload_to=RUTA_CARGA_LOGOS_INTERFAZ,
        null=True,
        blank=True,
    )
    favicon = models.ImageField(
        upload_to=RUTA_CARGA_FAVICON_INTERFAZ,
        null=True,
        blank=True,
    )
    logo_principal_repositorio = models.ForeignKey(
        REFERENCIA_MODELO_ARCHIVO_REPOSITORIO,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="configuraciones_logo_principal",
    )
    logo_secundario_repositorio = models.ForeignKey(
        REFERENCIA_MODELO_ARCHIVO_REPOSITORIO,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="configuraciones_logo_secundario",
    )
    logo_institucional_repositorio = models.ForeignKey(
        REFERENCIA_MODELO_ARCHIVO_REPOSITORIO,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="configuraciones_logo_institucional",
    )
    favicon_repositorio = models.ForeignKey(
        REFERENCIA_MODELO_ARCHIVO_REPOSITORIO,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="configuraciones_favicon",
    )
    color_primario = models.CharField(max_length=20, blank=True)
    color_secundario = models.CharField(max_length=20, blank=True)
    color_acento = models.CharField(max_length=20, blank=True)
    esta_activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["-fecha_modificacion"]
        indexes = [
            models.Index(fields=["esta_activa"]),
        ]
        verbose_name = "Configuración de interfaz"
        verbose_name_plural = "Configuraciones de interfaz"

    def __str__(self) -> str:
        return self.nombre_aplicativo


class ConfiguracionFlujoFormulario(AuditoriaModeloAbstracto):
    """Textos parametrizables de modales y terminos del flujo de formularios."""

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    configuracion_interfaz = models.ForeignKey(
        ConfiguracionInterfaz,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="configuraciones_flujo",
    )
    modal_salir_titulo = models.CharField(max_length=255, blank=True)
    modal_salir_p1 = models.TextField(blank=True)
    modal_salir_p2 = models.TextField(blank=True)
    modal_salir_btn_volver = models.CharField(max_length=255, blank=True)
    modal_salir_btn_salir = models.CharField(max_length=255, blank=True)
    modal_salir_link_sesion = models.CharField(max_length=255, blank=True)
    modal_sesion_titulo = models.CharField(max_length=255, blank=True)
    modal_sesion_parrafo = models.TextField(blank=True)
    modal_sesion_btn_login = models.CharField(max_length=255, blank=True)
    modal_sesion_btn_registro = models.CharField(max_length=255, blank=True)
    modal_sesion_link_cancelar = models.CharField(max_length=255, blank=True)
    modal_guardado_titulo = models.CharField(max_length=255, blank=True)
    modal_guardado_parrafo = models.TextField(blank=True)
    modal_guardado_btn_seguir = models.CharField(max_length=255, blank=True)
    modal_guardado_btn_otras = models.CharField(max_length=255, blank=True)
    terminos_titulo = models.CharField(max_length=500, blank=True)
    terminos_contenido = models.TextField(blank=True)
    terminos_p1 = models.TextField(blank=True)
    terminos_p2 = models.TextField(blank=True)
    terminos_p3 = models.TextField(blank=True)
    terminos_url_ley = models.URLField(blank=True)
    terminos_url_politica_datos = models.URLField(blank=True)
    terminos_email_soporte = models.EmailField(blank=True)
    terminos_boton_aceptar = models.CharField(max_length=255, blank=True)
    terminos_boton_cerrar = models.CharField(max_length=255, blank=True)
    terminos_enlace = models.CharField(max_length=255, blank=True)
    terminos_enlace_ley = models.CharField(max_length=255, blank=True)
    terminos_enlace_politica_datos = models.CharField(max_length=255, blank=True)
    img_enc_enviada_exito = models.ForeignKey(
        REFERENCIA_MODELO_ARCHIVO_REPOSITORIO,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="configuraciones_flujo_envio_exito",
    )
    img_enc_enviada_exito_alt = models.CharField(max_length=500, blank=True)
    esta_activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["-fecha_modificacion"]
        indexes = [
            models.Index(fields=["esta_activa"]),
            models.Index(fields=["uuid"]),
        ]
        verbose_name = "Configuración de flujo de formulario"
        verbose_name_plural = "Configuraciones de flujo de formulario"

    def __str__(self) -> str:
        estado = "activa" if self.esta_activa else "inactiva"
        return f"Flujo formulario ({estado})"

    def clean(self) -> None:
        """Valida que solo exista una configuracion activa no eliminada."""
        super().clean()
        if not self.esta_activa:
            return
        otras_activas = ConfiguracionFlujoFormulario.objects.filter(
            esta_activa=True,
            esta_eliminado=False,
        ).exclude(pk=self.pk)
        if otras_activas.exists():
            raise ValidationError(
                {"esta_activa": "Ya existe otra configuración de flujo activa."},
            )


class LogoInterfaz(AuditoriaModeloAbstracto):
    """Logo o imagen parametrizable asociada a una configuracion de interfaz."""

    configuracion_interfaz = models.ForeignKey(
        ConfiguracionInterfaz,
        on_delete=models.CASCADE,
        related_name="logos",
    )
    codigo = models.CharField(max_length=100)
    nombre = models.CharField(max_length=255)
    texto_alternativo = models.CharField(max_length=500, blank=True)
    imagen = models.ImageField(
        upload_to=RUTA_CARGA_LOGOS_INTERFAZ,
        null=True,
        blank=True,
    )
    archivo_repositorio = models.ForeignKey(
        REFERENCIA_MODELO_ARCHIVO_REPOSITORIO,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="logos_interfaz",
    )
    orden = models.PositiveIntegerField(default=1)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["configuracion_interfaz", "orden", "codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["configuracion_interfaz", "codigo"],
                condition=models.Q(esta_eliminado=False),
                name="uq_logo_interfaz_config_codigo_activo",
            ),
        ]
        indexes = [
            models.Index(fields=["configuracion_interfaz"]),
            models.Index(fields=["codigo"]),
            models.Index(fields=["esta_activo"]),
            models.Index(fields=["orden"]),
        ]
        verbose_name = "Logo de interfaz"
        verbose_name_plural = "Logos de interfaz"

    def __str__(self) -> str:
        return f"{self.codigo} - {self.nombre}"
