"""
Constantes de grupos, permisos y mensajes del modulo de usuarios.
"""


class GrupoSistema:
    """Nombres de grupos de roles del sistema."""

    ADMINISTRADOR_GENERAL = "administrador_general"
    GESTOR_FORMULARIOS = "gestor_formularios"
    EDITOR_FORMULARIOS = "editor_formularios"
    LECTOR_FORMULARIOS = "lector_formularios"
    ANALISTA_DATOS = "analista_datos"
    ENCUESTADO = "encuestado"

    TODOS = (
        ADMINISTRADOR_GENERAL,
        GESTOR_FORMULARIOS,
        EDITOR_FORMULARIOS,
        LECTOR_FORMULARIOS,
        ANALISTA_DATOS,
        ENCUESTADO,
    )

    TODOS_CON_PERMISOS = (
        ADMINISTRADOR_GENERAL,
        GESTOR_FORMULARIOS,
        EDITOR_FORMULARIOS,
        LECTOR_FORMULARIOS,
        ANALISTA_DATOS,
    )


class PermisoCodigo:
    """Codigos de permisos personalizados del sistema."""

    GESTIONAR_FORMULARIOS = "puede_gestionar_formularios"
    PUBLICAR_FORMULARIOS = "puede_publicar_formularios"
    VERSIONAR_FORMULARIOS = "puede_versionar_formularios"
    CONSULTAR_FORMULARIOS_ADMIN = "puede_consultar_formularios_admin"
    EXPORTAR_RESPUESTAS = "puede_exportar_respuestas"
    GESTIONAR_USUARIOS = "puede_gestionar_usuarios"

    TODOS = (
        GESTIONAR_FORMULARIOS,
        PUBLICAR_FORMULARIOS,
        VERSIONAR_FORMULARIOS,
        CONSULTAR_FORMULARIOS_ADMIN,
        EXPORTAR_RESPUESTAS,
        GESTIONAR_USUARIOS,
    )


APP_LABEL_USUARIOS = "usuarios"

VARIABLES_PLANTILLAS_CORREO = (
    "nombre",
    "correo",
    "username",
    "url_restaurar_password",
    "url_login",
    "nombre_aplicativo",
    "formulario",
    "uuid_sesion",
    "fecha",
    "resumen_respuestas",
    "asunto",
    "mensaje",
)


class TipoInicioSesion:
    """Tipos de autenticacion soportados para el perfil de usuario."""

    CORREO_ELECTRONICO = "correo_electronico"
    ETIQUETA_CORREO_ELECTRONICO = "Correo electrónico"


def permiso_completo(codigo: str) -> str:
    """Construye el identificador completo de un permiso Django."""
    return f"{APP_LABEL_USUARIOS}.{codigo}"


class MensajesAuth:
    """Mensajes de respuesta para autenticacion."""

    CREDENCIALES_INVALIDAS = "Las credenciales proporcionadas no son válidas."
    IDENTIFICADOR_REQUERIDO = (
        "Debe indicar su usuario, correo electrónico o número de celular."
    )
    CONTRASENA_REQUERIDA = "Debe indicar su contraseña."
    USUARIO_INACTIVO = "La cuenta de usuario se encuentra inactiva."
    SESION_CERRADA = "La sesión se cerró correctamente."
    LOGIN_CORRECTO = "Inicio de sesión correcto."
    CONTRASENA_ACTUAL_INCORRECTA = "La contraseña actual no es correcta."
    CONTRASENA_CAMBIADA = "La contraseña se actualizó correctamente."
    CONTRASENAS_NO_COINCIDEN = "Las contraseñas no coinciden."
    NO_AUTENTICADO = "Se requiere autenticación para acceder a este recurso."
    USUARIO_REGISTRADO = "Usuario registrado correctamente."
    USERNAME_DUPLICADO = "El nombre de usuario ya está registrado."
    EMAIL_DUPLICADO = "El correo electrónico ya está registrado."
    EMAIL_INVALIDO = "El correo electrónico no es válido."
    PERFIL_ACTUALIZADO = "Perfil actualizado correctamente."
    SOLICITUD_RESTAURAR_CONTRASENA = (
        "Si el correo está registrado, recibirás instrucciones para restaurar la contraseña."
    )
    CONTRASENA_RESTAURADA = "La contraseña fue restaurada correctamente."
    TOKEN_RESTAURAR_INVALIDO = "El enlace de restauración no es válido o ha expirado."


class MensajesContacto:
    """Mensajes de respuesta para el formulario de contacto."""

    ENVIADO = "Tu mensaje fue enviado correctamente."
    SIN_EMAIL_SOPORTE = "No hay correo de soporte configurado."


class MensajesCopiaRespuestas:
    """Mensajes de respuesta para envio de copia de respuestas."""

    ENVIADA = "La copia de respuestas fue enviada al correo indicado."
    CORREO_INVALIDO = "El correo electrónico indicado no es válido."


class MensajesUsuariosAdmin:
    """Mensajes de respuesta para gestion administrativa de usuarios."""

    SIN_PERMISO = "No tiene permisos para gestionar usuarios del sistema."
    USUARIO_NO_ENCONTRADO = "El usuario solicitado no existe."
    GRUPOS_INVALIDOS = "Uno o más grupos indicados no existen en el sistema."
