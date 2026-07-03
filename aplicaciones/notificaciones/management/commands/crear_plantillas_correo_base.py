"""
Comando para crear plantillas base de correo electronico.
"""

from django.core.management.base import BaseCommand

from aplicaciones.notificaciones.constantes import TipoNotificacion
from aplicaciones.notificaciones.models import PlantillaNotificacion
from aplicaciones.usuarios.constantes import VARIABLES_PLANTILLAS_CORREO

PLANTILLAS_BASE: dict[str, dict] = {
    "restaurar_password": {
        "nombre": "Restaurar contraseña",
        "asunto": "Restaurar contraseña - {{nombre_aplicativo}}",
        "contenido_html": (
            "<p>Hola {{nombre}},</p>"
            "<p>Recibimos una solicitud para restaurar tu contraseña.</p>"
            "<p><a href=\"{{url_restaurar_password}}\">Restaurar contraseña</a></p>"
            "<p>Si no solicitaste este cambio, ignora este mensaje.</p>"
        ),
        "contenido_texto": (
            "Hola {{nombre}}, usa el enlace para restaurar tu contraseña: "
            "{{url_restaurar_password}}"
        ),
    },
    "usuario_creado": {
        "nombre": "Usuario creado",
        "asunto": "Cuenta creada en {{nombre_aplicativo}}",
        "contenido_html": (
            "<p>Hola {{nombre}},</p>"
            "<p>Se creó tu cuenta con usuario {{username}}.</p>"
            "<p><a href=\"{{url_login}}\">Iniciar sesión</a></p>"
        ),
        "contenido_texto": "Hola {{nombre}}, tu cuenta {{username}} fue creada.",
    },
    "confirmacion_registro": {
        "nombre": "Confirmación de registro",
        "asunto": "Bienvenido a {{nombre_aplicativo}}",
        "contenido_html": (
            "<p>Hola {{nombre}},</p>"
            "<p>Tu registro fue exitoso con el usuario {{username}}.</p>"
            "<p><a href=\"{{url_login}}\">Iniciar sesión</a></p>"
        ),
        "contenido_texto": (
            "Hola {{nombre}}, bienvenido. Usuario: {{username}}. "
            "Inicia sesión en {{url_login}}"
        ),
    },
    "verificacion_correo": {
        "nombre": "Verificación de correo",
        "asunto": "Verifica tu correo - {{nombre_aplicativo}}",
        "contenido_html": (
            "<p>Hola {{nombre}},</p>"
            "<p>Para completar tu registro, verifica tu correo electrónico.</p>"
            "<p><a href=\"{{url_verificar_correo}}\">Verificar correo</a></p>"
            "<p>Si no creaste esta cuenta, ignora este mensaje.</p>"
        ),
        "contenido_texto": (
            "Hola {{nombre}}, verifica tu correo con el siguiente enlace: "
            "{{url_verificar_correo}}"
        ),
    },
    "formulario_finalizado": {
        "nombre": "Formulario finalizado",
        "asunto": "Formulario {{formulario}} finalizado",
        "contenido_html": (
            "<p>El formulario {{formulario}} fue finalizado.</p>"
            "<p>Sesión: {{uuid_sesion}}</p><p>Fecha: {{fecha}}</p>"
        ),
        "contenido_texto": "Formulario {{formulario}} finalizado el {{fecha}}.",
    },
    "copia_respuestas_formulario": {
        "nombre": "Copia de respuestas",
        "asunto": "Copia de respuestas - {{formulario}}",
        "contenido_html": (
            "<p>Copia de respuestas del formulario {{formulario}}.</p>"
            "<p>Sesión: {{uuid_sesion}}</p><p>Fecha: {{fecha}}</p>"
            "<pre>{{resumen_respuestas}}</pre>"
        ),
        "contenido_texto": (
            "Copia de respuestas de {{formulario}} ({{uuid_sesion}}):\n"
            "{{resumen_respuestas}}"
        ),
    },
    "contacto_recibido": {
        "nombre": "Contacto recibido",
        "asunto": "Contacto: {{asunto}}",
        "contenido_html": (
            "<p>Mensaje de {{nombre}} ({{correo}})</p>"
            "<p><strong>Asunto:</strong> {{asunto}}</p>"
            "<p>{{mensaje}}</p>"
        ),
        "contenido_texto": "De {{nombre}} ({{correo}}): {{asunto}} - {{mensaje}}",
    },
}


class Command(BaseCommand):
    """Crea o actualiza plantillas base de correo del sistema."""

    help = "Crea o actualiza plantillas base de correo electrónico."

    def handle(self, *args, **options) -> None:
        """Ejecuta la creacion o actualizacion de plantillas base."""
        for codigo, datos in PLANTILLAS_BASE.items():
            _, creada = PlantillaNotificacion.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "nombre": datos["nombre"],
                    "tipo": TipoNotificacion.CORREO,
                    "asunto": datos["asunto"],
                    "contenido_html": datos["contenido_html"],
                    "contenido_texto": datos["contenido_texto"],
                    "variables_disponibles": list(VARIABLES_PLANTILLAS_CORREO),
                    "esta_activa": True,
                },
            )
            accion = "creada" if creada else "actualizada"
            self.stdout.write(
                self.style.SUCCESS(f"Plantilla {codigo} {accion}."),
            )
