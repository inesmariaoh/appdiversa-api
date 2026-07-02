"""
Vistas administrativas de gestion de usuarios y roles.
"""

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers, status
from aplicaciones.comun.autenticacion_sesion import AutenticacionSesionApi
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.usuarios.api.v1.admin_serializers import (
    AsignarGruposEntradaSerializer,
    GrupoSerializer,
    PermisoSerializer,
    UsuarioAdminActualizacionSerializer,
    UsuarioAdminCreacionSerializer,
    UsuarioAdminSerializer,
)
from aplicaciones.usuarios.excepciones import GruposInvalidosError, UsuarioNoEncontradoError
from aplicaciones.usuarios.permisos import PermisoGestionarUsuarios
from aplicaciones.usuarios.selectores import listar_grupos_sistema, listar_permisos_personalizados
from aplicaciones.usuarios.servicios.gestion_usuarios import (
    activar_usuario_admin,
    actualizar_usuario_admin,
    asignar_grupos_usuario_admin,
    crear_usuario_admin,
    desactivar_usuario_admin,
    listar_usuarios,
)

_AUTENTICACION_SESION = [AutenticacionSesionApi]
_DETALLE_ERROR = inline_serializer(
    name="DetalleErrorAdminUsuarios",
    fields={"detalle": serializers.CharField()},
)


class UsuariosAdminListCreateView(APIView):
    """Lista y crea usuarios del sistema."""

    permission_classes = [PermisoGestionarUsuarios]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Admin Usuarios"],
        summary="Listar usuarios",
        responses={status.HTTP_200_OK: UsuarioAdminSerializer(many=True)},
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna el listado de usuarios registrados."""
        usuarios = listar_usuarios()
        serializador = UsuarioAdminSerializer(usuarios, many=True)
        return Response(serializador.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Admin Usuarios"],
        summary="Crear usuario",
        request=UsuarioAdminCreacionSerializer,
        responses={
            status.HTTP_201_CREATED: UsuarioAdminSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Crea un nuevo usuario del sistema."""
        entrada = UsuarioAdminCreacionSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        contrasena = datos.pop("contrasena")
        usuario = crear_usuario_admin(datos, contrasena)
        serializador = UsuarioAdminSerializer(usuario)
        return Response(serializador.data, status=status.HTTP_201_CREATED)


class UsuarioAdminDetalleView(APIView):
    """Consulta y actualiza un usuario especifico."""

    permission_classes = [PermisoGestionarUsuarios]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Admin Usuarios"],
        summary="Detalle de usuario",
        responses={
            status.HTTP_200_OK: UsuarioAdminSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def get(self, solicitud: Request, usuario_id: int) -> Response:
        """Retorna el detalle de un usuario."""
        usuarios = listar_usuarios().filter(pk=usuario_id)
        if not usuarios.exists():
            return Response(
                {"detalle": UsuarioNoEncontradoError().mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializador = UsuarioAdminSerializer(usuarios.first())
        return Response(serializador.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Admin Usuarios"],
        summary="Actualizar usuario",
        request=UsuarioAdminActualizacionSerializer,
        responses={
            status.HTTP_200_OK: UsuarioAdminSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def patch(self, solicitud: Request, usuario_id: int) -> Response:
        """Actualiza campos permitidos de un usuario."""
        entrada = UsuarioAdminActualizacionSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        try:
            usuario = actualizar_usuario_admin(usuario_id, entrada.validated_data)
        except UsuarioNoEncontradoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializador = UsuarioAdminSerializer(usuario)
        return Response(serializador.data, status=status.HTTP_200_OK)


class UsuarioAdminActivarView(APIView):
    """Activa un usuario inactivo."""

    permission_classes = [PermisoGestionarUsuarios]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Admin Usuarios"],
        summary="Activar usuario",
        responses={
            status.HTTP_200_OK: UsuarioAdminSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request, usuario_id: int) -> Response:
        """Activa la cuenta del usuario indicado."""
        try:
            usuario = activar_usuario_admin(usuario_id)
        except UsuarioNoEncontradoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializador = UsuarioAdminSerializer(usuario)
        return Response(serializador.data, status=status.HTTP_200_OK)


class UsuarioAdminDesactivarView(APIView):
    """Desactiva un usuario activo."""

    permission_classes = [PermisoGestionarUsuarios]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Admin Usuarios"],
        summary="Desactivar usuario",
        responses={
            status.HTTP_200_OK: UsuarioAdminSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request, usuario_id: int) -> Response:
        """Desactiva la cuenta del usuario indicado."""
        try:
            usuario = desactivar_usuario_admin(usuario_id)
        except UsuarioNoEncontradoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializador = UsuarioAdminSerializer(usuario)
        return Response(serializador.data, status=status.HTTP_200_OK)


class UsuarioAdminAsignarGruposView(APIView):
    """Asigna grupos de roles a un usuario."""

    permission_classes = [PermisoGestionarUsuarios]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Admin Usuarios"],
        summary="Asignar grupos",
        request=AsignarGruposEntradaSerializer,
        responses={
            status.HTTP_200_OK: UsuarioAdminSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request, usuario_id: int) -> Response:
        """Reemplaza los grupos asignados al usuario."""
        entrada = AsignarGruposEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        try:
            usuario = asignar_grupos_usuario_admin(
                usuario_id,
                entrada.validated_data["grupos"],
            )
        except UsuarioNoEncontradoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        except GruposInvalidosError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializador = UsuarioAdminSerializer(usuario)
        return Response(serializador.data, status=status.HTTP_200_OK)


class GruposAdminListView(APIView):
    """Lista grupos de roles del sistema."""

    permission_classes = [PermisoGestionarUsuarios]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Admin Usuarios"],
        summary="Listar grupos",
        responses={status.HTTP_200_OK: GrupoSerializer(many=True)},
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna los grupos de roles parametrizados."""
        grupos = listar_grupos_sistema()
        datos = [{"id": grupo.pk, "name": grupo.name} for grupo in grupos]
        serializador = GrupoSerializer(datos, many=True)
        return Response(serializador.data, status=status.HTTP_200_OK)


class PermisosAdminListView(APIView):
    """Lista permisos personalizados del sistema."""

    permission_classes = [PermisoGestionarUsuarios]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Admin Usuarios"],
        summary="Listar permisos",
        responses={status.HTTP_200_OK: PermisoSerializer(many=True)},
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna permisos personalizados disponibles."""
        permisos = listar_permisos_personalizados()
        datos = [
            {
                "id": permiso.pk,
                "codename": permiso.codename,
                "name": permiso.name,
                "app_label": permiso.content_type.app_label,
            }
            for permiso in permisos
        ]
        serializador = PermisoSerializer(datos, many=True)
        return Response(serializador.data, status=status.HTTP_200_OK)
