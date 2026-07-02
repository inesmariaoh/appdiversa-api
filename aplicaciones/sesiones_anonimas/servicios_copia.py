"""
Reexportacion del servicio de copia de respuestas hacia notificaciones.
"""

from aplicaciones.notificaciones.servicios_correo import enviar_copia_respuestas_formulario

enviar_copia_respuestas_sesion = enviar_copia_respuestas_formulario

__all__ = ("enviar_copia_respuestas_sesion", "enviar_copia_respuestas_formulario")
