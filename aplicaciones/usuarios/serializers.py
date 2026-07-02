"""
Serializers del modulo de usuarios y autenticacion.
"""

from rest_framework import serializers

from aplicaciones.usuarios.constantes import MensajesAuth
from aplicaciones.usuarios.validadores_contrasena import validar_contrasena_usuario


class LoginEntradaSerializer(serializers.Serializer):
    """Entrada para inicio de sesion con usuario o correo."""

    usuario = serializers.CharField(max_length=254, required=False, allow_blank=True)
    username = serializers.CharField(max_length=254, required=False, allow_blank=True)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs: dict) -> dict:
        """Normaliza identificador desde usuario o username del cliente."""
        identificador = (attrs.get("usuario") or attrs.get("username") or "").strip()
        if not identificador:
            raise serializers.ValidationError(
                {"detalle": MensajesAuth.IDENTIFICADOR_REQUERIDO},
            )
        attrs["usuario"] = identificador
        attrs.pop("username", None)
        return attrs


class RegistroEntradaSerializer(serializers.Serializer):
    """Entrada para registro de usuario."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    password_confirmacion = serializers.CharField(max_length=128, write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs: dict) -> dict:
        """Valida coincidencia de contrasenas en registro."""
        if attrs["password"] != attrs["password_confirmacion"]:
            raise serializers.ValidationError(
                {"password_confirmacion": MensajesAuth.CONTRASENAS_NO_COINCIDEN},
            )
        validar_contrasena_usuario(attrs["password"])
        return attrs


class RegistroCorreoEntradaSerializer(serializers.Serializer):
    """Entrada para autorregistro de usuarios normales con correo."""

    correo = serializers.EmailField()
    contrasena = serializers.CharField(max_length=128, write_only=True)


class CambiarPasswordEntradaSerializer(serializers.Serializer):
    """Entrada para cambio de contrasena del usuario autenticado."""

    password_actual = serializers.CharField(max_length=128, write_only=True)
    password_nueva = serializers.CharField(max_length=128, write_only=True)
    password_confirmacion = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs: dict) -> dict:
        """Valida coincidencia y fortaleza de la nueva contrasena."""
        if attrs["password_nueva"] != attrs["password_confirmacion"]:
            raise serializers.ValidationError(
                {"password_confirmacion": MensajesAuth.CONTRASENAS_NO_COINCIDEN},
            )
        validar_contrasena_usuario(attrs["password_nueva"])
        return attrs


class SolicitarRestaurarPasswordEntradaSerializer(serializers.Serializer):
    """Entrada para solicitud de restauracion de contrasena."""

    email = serializers.EmailField()


class RestaurarPasswordEntradaSerializer(serializers.Serializer):
    """Entrada para confirmar restauracion de contrasena."""

    uid = serializers.CharField()
    token = serializers.CharField()
    password_nueva = serializers.CharField(max_length=128, write_only=True)
    password_confirmacion = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs: dict) -> dict:
        """Valida coincidencia y fortaleza de la nueva contrasena."""
        if attrs["password_nueva"] != attrs["password_confirmacion"]:
            raise serializers.ValidationError(
                {"password_confirmacion": MensajesAuth.CONTRASENAS_NO_COINCIDEN},
            )
        validar_contrasena_usuario(attrs["password_nueva"])
        return attrs


class PerfilActualizacionSerializer(serializers.Serializer):
    """Entrada para actualizacion parcial del perfil."""

    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)


class PerfilEditableSerializer(serializers.Serializer):
    """Perfil editable del usuario autenticado."""

    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    fecha_ultimo_inicio_sesion = serializers.DateTimeField(allow_null=True)
    tipo_inicio_sesion = serializers.CharField()
    tipo_inicio_sesion_etiqueta = serializers.CharField()


class UsuarioAutenticadoSerializer(serializers.Serializer):
    """Perfil del usuario autenticado."""

    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    grupos = serializers.ListField(child=serializers.CharField())
    permisos = serializers.ListField(child=serializers.CharField())


class LoginSalidaSerializer(serializers.Serializer):
    """Respuesta de inicio de sesion exitoso."""

    usuario = UsuarioAutenticadoSerializer()
    detalle = serializers.CharField()


class DetalleSalidaSerializer(serializers.Serializer):
    """Respuesta con mensaje funcional en campo detalle."""

    detalle = serializers.CharField()


class ContactoEntradaSerializer(serializers.Serializer):
    """Entrada del formulario de contacto publico."""

    nombre = serializers.CharField(max_length=255)
    correo = serializers.EmailField()
    asunto = serializers.CharField(max_length=300)
    mensaje = serializers.CharField()


class EnviarCopiaRespuestasEntradaSerializer(serializers.Serializer):
    """Entrada para envio de copia de respuestas por correo."""

    correo = serializers.EmailField()


class MisRespuestaSesionSerializer(serializers.Serializer):
    """Item del historial de respuestas del usuario autenticado."""

    uuid_sesion = serializers.UUIDField()
    uuid_formulario = serializers.UUIDField()
    codigo_formulario = serializers.CharField()
    nombre_formulario = serializers.CharField()
    estado = serializers.CharField()
    fecha_inicio = serializers.DateTimeField()
    fecha_ultima_actividad = serializers.DateTimeField()
    fecha_finalizacion = serializers.DateTimeField()
    total_respuestas = serializers.IntegerField()
    es_offline = serializers.BooleanField()


class MisRespuestasSalidaSerializer(serializers.Serializer):
    """Listado de sesiones vinculadas al usuario autenticado."""

    resultados = MisRespuestaSesionSerializer(many=True)
