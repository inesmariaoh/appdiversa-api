"""
Constantes del motor transversal de notificaciones.
"""

from django.db import models


class TipoNotificacion(models.TextChoices):
    """Canales o tipos de notificacion soportados."""

    CORREO = "correo", "Correo"
    SMS = "sms", "SMS"
    PUSH = "push", "Push"
    INTERNA = "interna", "Interna"
    WEBHOOK = "webhook", "Webhook"


class EstadoNotificacion(models.TextChoices):
    """Estados del ciclo de vida de una notificacion."""

    PENDIENTE = "pendiente", "Pendiente"
    PROCESANDO = "procesando", "Procesando"
    ENVIADA = "enviada", "Enviada"
    FALLIDA = "fallida", "Fallida"
    CANCELADA = "cancelada", "Cancelada"


class MensajesNotificacionApi:
    """Mensajes funcionales de la API de notificaciones."""

    NOTIFICACION_NO_ENCONTRADA = "La notificación solicitada no existe."
    PLANTILLA_NO_ENCONTRADA = "La plantilla solicitada no existe o no está activa."
    PLANTILLA_CODIGO_DUPLICADO = "Ya existe una plantilla con ese código."
    VARIABLES_INVALIDAS = "Las variables proporcionadas no son válidas para la plantilla."


class CodigoPlantillaCorreo:
    """Codigos de plantillas de correo parametrizables."""

    RESTAURAR_PASSWORD = "restaurar_password"
    USUARIO_CREADO = "usuario_creado"
    CONFIRMACION_REGISTRO = "confirmacion_registro"
    FORMULARIO_FINALIZADO = "formulario_finalizado"
    COPIA_RESPUESTAS = "copia_respuestas_formulario"
    CONTACTO_RECIBIDO = "contacto_recibido"


class RespuestaProveedorCorreo:
    """Valores estandar de respuesta del proveedor de correo."""

    PROVEEDOR_SMTP = "smtp"
    PROVEEDOR_DUMMY = "dummy"
    ESTADO_ENVIADO = "enviado"
    ESTADO_REGISTRADO = "registrado"
