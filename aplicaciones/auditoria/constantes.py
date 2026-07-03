"""
Choices y constantes del modulo de auditoria.
"""

from django.db import models

HEADER_KEYCLOAK_USER_ID = "HTTP_X_KEYCLOAK_USER_ID"
HEADER_SESION_ANONIMA = "HTTP_X_SESION_ANONIMA"

SUBCADENAS_CAMPOS_SENSIBLES = (
    "password",
    "token",
    "secret",
    "key",
)


class AccionAuditoria(models.TextChoices):
    """Acciones registrables en el log de auditoria."""

    CREAR = "crear", "Crear"
    EDITAR = "editar", "Editar"
    ELIMINAR = "eliminar", "Eliminar"
    RESTAURAR = "restaurar", "Restaurar"
    PUBLICAR = "publicar", "Publicar"
    CERRAR = "cerrar", "Cerrar"
    ARCHIVAR = "archivar", "Archivar"
    CONSULTAR = "consultar", "Consultar"
    EXPORTAR = "exportar", "Exportar"
    INICIAR_SESION = "iniciar_sesion", "Iniciar sesión"
    FINALIZAR_SESION = "finalizar_sesion", "Finalizar sesión"
    REGISTRAR_USUARIO = "registrar_usuario", "Registrar usuario"
    EDITAR_PERFIL = "editar_perfil", "Editar perfil"
    ELIMINAR_CUENTA = "eliminar_cuenta", "Eliminar cuenta"
    VERIFICAR_CORREO = "verificar_correo", "Verificar correo"
    CAMBIAR_PASSWORD = "cambiar_password", "Cambiar contraseña"
    SOLICITAR_RESTAURAR_PASSWORD = "solicitar_restaurar_password", "Solicitar restaurar contraseña"
    PASSWORD_RESTAURADO = "password_restaurado", "Contraseña restaurada"
    CONTACTO_ENVIADO = "contacto_enviado", "Contacto enviado"
    COPIA_RESPUESTAS_ENVIADA = "copia_respuestas_enviada", "Copia respuestas enviada"
    CORREO_ENVIADO = "correo_enviado", "Correo enviado"
    CORREO_FALLIDO = "correo_fallido", "Correo fallido"
    VERSIONAR = "versionar", "Versionar"
    FINALIZAR_FORMULARIO = "finalizar_formulario", "Finalizar formulario"
    SINCRONIZAR = "sincronizar", "Sincronizar"
    ACCESO_DENEGADO = "acceso_denegado", "Acceso denegado"
    CONFLICTO = "conflicto", "Conflicto"
    RESOLUCION_CONFLICTO = "resolucion_conflicto", "Resolución de conflicto"


class MensajesAuditoriaApi:
    """Mensajes de respuesta de la API de auditoria."""

    SIN_PERMISO = "No tiene permisos para consultar los registros de auditoría."
    REGISTRO_NO_ENCONTRADO = "El registro de auditoría solicitado no existe."


class FiltrosAuditoria:
    """Nombres de los parametros de filtrado de la API de auditoria."""

    ENTIDAD = "entidad"
    ENTIDAD_ID = "entidad_id"
    ACCION = "accion"
    USUARIO = "usuario"
    FECHA_INICIO = "fecha_inicio"
    FECHA_FIN = "fecha_fin"
    BUSQUEDA = "busqueda"
