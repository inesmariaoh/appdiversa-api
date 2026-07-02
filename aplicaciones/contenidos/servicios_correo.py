"""
Resolucion de correos de soporte y notificaciones desde configuracion de interfaz.
"""

from django.conf import settings

from aplicaciones.contenidos.selectores import obtener_configuracion_interfaz_activa


def obtener_email_soporte_configurado() -> str:
    """Retorna el correo de soporte activo o cadena vacia si no esta configurado."""
    configuracion = obtener_configuracion_interfaz_activa()
    if configuracion is None:
        return ""
    return (configuracion.email_soporte or "").strip()


def obtener_email_remitente_notificaciones() -> str:
    """Retorna el remitente de correos del sistema desde interfaz o entorno."""
    configuracion = obtener_configuracion_interfaz_activa()
    if configuracion is not None:
        remitente = (configuracion.email_remitente_notificaciones or "").strip()
        if remitente:
            return remitente
    return settings.EMAIL_DEFAULT_FROM
