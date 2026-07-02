"""
Serializers de gestion administrativa de usuarios.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UsuarioAdminSerializer(serializers.ModelSerializer):
    """Serializer de lectura de usuarios para administracion."""

    grupos = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "is_active",
            "grupos",
            "date_joined",
            "last_login",
        )
        read_only_fields = fields

    def get_grupos(self, instancia: User) -> list[str]:
        """Retorna los nombres de grupos asignados al usuario."""
        return list(instancia.groups.values_list("name", flat=True))


class UsuarioAdminCreacionSerializer(serializers.Serializer):
    """Entrada para creacion de usuarios desde administracion."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")
    contrasena = serializers.CharField(max_length=128, write_only=True)
    is_staff = serializers.BooleanField(required=False, default=False)


class UsuarioAdminActualizacionSerializer(serializers.Serializer):
    """Entrada para actualizacion parcial de usuarios."""

    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    is_staff = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)


class AsignarGruposEntradaSerializer(serializers.Serializer):
    """Entrada para asignacion de grupos a un usuario."""

    grupos = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=True,
    )


class GrupoSerializer(serializers.Serializer):
    """Representacion de un grupo de roles."""

    id = serializers.IntegerField()
    name = serializers.CharField()


class PermisoSerializer(serializers.Serializer):
    """Representacion de un permiso del sistema."""

    id = serializers.IntegerField()
    codename = serializers.CharField()
    name = serializers.CharField()
    app_label = serializers.CharField()
