"""
Vistas de autenticacion, perfil y contacto de usuarios.
"""

from uuid import UUID

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import serializers, status
from aplicaciones.comun.autenticacion_sesion import AutenticacionSesionApi
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from aplicaciones.comun.throttling import ScopeThrottle

from aplicaciones.usuarios.constantes import (
    MensajesAuth,
    MensajesContacto,
    MensajesCopiaRespuestas,
)
from aplicaciones.usuarios.excepciones import (
    ContrasenaActualIncorrectaError,
    ContrasenaInvalidaError,
    ContrasenasNoCoincidenError,
    CredencialesInvalidasError,
    EmailDuplicadoError,
    TokenRestaurarInvalidoError,
    UsernameDuplicadoError,
    UsuarioInactivoError,
)
from aplicaciones.usuarios.permisos import (
    PermisoUsuarioAutenticado,
    PermisoUsuarioAutenticado401,
)
from aplicaciones.usuarios.serializers import (
    CambiarPasswordEntradaSerializer,
    ContactoEntradaSerializer,
    DetalleSalidaSerializer,
    LoginEntradaSerializer,
    LoginSalidaSerializer,
    MisRespuestasSalidaSerializer,
    PerfilActualizacionSerializer,
    PerfilEditableSerializer,
    RegistroCorreoEntradaSerializer,
    RegistroEntradaSerializer,
    RestaurarPasswordEntradaSerializer,
    SolicitarRestaurarPasswordEntradaSerializer,
    UsuarioAutenticadoSerializer,
)
from aplicaciones.usuarios.servicios.autenticacion import (
    autenticar_usuario,
    cambiar_contrasena_usuario,
    cerrar_sesion_usuario,
    construir_datos_perfil_editable,
    construir_datos_usuario_autenticado,
    construir_respuesta_perfil_autenticado,
)
from aplicaciones.usuarios.servicios.contacto import (
    ContactoSinEmailSoporteError,
    enviar_contacto,
)
from aplicaciones.usuarios.servicios.exportar_respuestas_usuario import (
    SesionNoPerteneceUsuarioError,
    exportar_respuestas_sesion_usuario,
)
from aplicaciones.usuarios.servicios.perfil import actualizar_perfil_usuario
from aplicaciones.usuarios.servicios.mis_respuestas import construir_historial_respuestas_usuario
from aplicaciones.exportaciones.constantes import (
    FORMATOS_DESCARGA_DIRECTA,
    FormatoExportacion,
    MensajesExportacionApi,
)
from aplicaciones.usuarios.servicios.registro import (
    registrar_usuario,
    registrar_usuario_por_correo,
)
from aplicaciones.usuarios.servicios.restaurar_password import (
    restaurar_password,
    solicitar_restaurar_password,
)

_AUTENTICACION_SESION = [AutenticacionSesionApi]
_DETALLE_ERROR = inline_serializer(
    name="DetalleErrorUsuarios",
    fields={"detalle": serializers.CharField()},
)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfCookieView(APIView):
    """Establece la cookie CSRF requerida por solicitudes autenticadas desde SPA."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        summary="Obtener cookie CSRF",
        responses={status.HTTP_200_OK: DetalleSalidaSerializer},
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna confirmacion funcional tras emitir la cookie CSRF."""
        return Response({"detalle": "Cookie CSRF disponible."})


class LoginView(APIView):
    """Inicia sesion con credenciales Django."""

    permission_classes = [AllowAny]
    authentication_classes = _AUTENTICACION_SESION
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = ScopeThrottle.LOGIN

    @extend_schema(
        tags=["Auth"],
        summary="Iniciar sesión",
        request=LoginEntradaSerializer,
        responses={
            status.HTTP_200_OK: LoginSalidaSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Autentica usuario por nombre de usuario o correo electronico."""
        entrada = LoginEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        try:
            usuario = autenticar_usuario(
                solicitud,
                datos["usuario"],
                datos["password"],
            )
        except (CredencialesInvalidasError, UsuarioInactivoError) as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                **construir_respuesta_perfil_autenticado(usuario),
                "detalle": MensajesAuth.LOGIN_CORRECTO,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """Cierra la sesion autenticada del usuario."""

    permission_classes = [PermisoUsuarioAutenticado]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Auth"],
        summary="Cerrar sesión",
        responses={status.HTTP_200_OK: DetalleSalidaSerializer},
    )
    def post(self, solicitud: Request) -> Response:
        """Finaliza la sesion del usuario autenticado."""
        cerrar_sesion_usuario(solicitud)
        return Response(
            {"detalle": MensajesAuth.SESION_CERRADA},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """Retorna el usuario autenticado."""

    permission_classes = [PermisoUsuarioAutenticado401]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Auth"],
        summary="Usuario autenticado",
        responses={
            status.HTTP_200_OK: UsuarioAutenticadoSerializer,
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna datos del usuario autenticado con grupos y permisos."""
        return Response(
            construir_respuesta_perfil_autenticado(solicitud.user),
            status=status.HTTP_200_OK,
        )


class PerfilView(APIView):
    """Consulta y actualiza el perfil del usuario autenticado."""

    permission_classes = [PermisoUsuarioAutenticado401]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Perfil"],
        summary="Obtener perfil",
        responses={
            status.HTTP_200_OK: PerfilEditableSerializer,
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna datos editables del perfil autenticado."""
        return Response(construir_datos_perfil_editable(solicitud.user))

    @extend_schema(
        tags=["Perfil"],
        summary="Actualizar perfil",
        request=PerfilActualizacionSerializer,
        responses={
            status.HTTP_200_OK: PerfilEditableSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def patch(self, solicitud: Request) -> Response:
        """Actualiza nombre, apellido y correo del usuario autenticado."""
        entrada = PerfilActualizacionSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        try:
            usuario = actualizar_perfil_usuario(solicitud.user, entrada.validated_data)
        except EmailDuplicadoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(construir_datos_perfil_editable(usuario))


class CambiarPasswordView(APIView):
    """Cambia la contrasena del usuario autenticado."""

    permission_classes = [PermisoUsuarioAutenticado]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Auth"],
        summary="Cambiar contraseña",
        request=CambiarPasswordEntradaSerializer,
        responses={
            status.HTTP_200_OK: DetalleSalidaSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Actualiza la contrasena del usuario autenticado."""
        entrada = CambiarPasswordEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        try:
            cambiar_contrasena_usuario(
                solicitud.user,
                datos["password_actual"],
                datos["password_nueva"],
                datos["password_confirmacion"],
            )
        except ContrasenaActualIncorrectaError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (ContrasenasNoCoincidenError, ContrasenaInvalidaError) as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detalle": MensajesAuth.CONTRASENA_CAMBIADA})


class RegistroView(APIView):
    """Registra un nuevo usuario en el sistema."""

    permission_classes = [AllowAny]
    authentication_classes = _AUTENTICACION_SESION
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = ScopeThrottle.REGISTRO

    @extend_schema(
        tags=["Auth"],
        summary="Registrar usuario",
        request=RegistroEntradaSerializer,
        responses={
            status.HTTP_201_CREATED: DetalleSalidaSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Crea un usuario activo y envia correo de bienvenida si aplica."""
        entrada = RegistroEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        try:
            registrar_usuario(entrada.validated_data)
        except (
            UsernameDuplicadoError,
            EmailDuplicadoError,
            ContrasenasNoCoincidenError,
            ContrasenaInvalidaError,
        ) as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detalle": MensajesAuth.USUARIO_REGISTRADO},
            status=status.HTTP_201_CREATED,
        )


class RegistroCorreoView(APIView):
    """Autorregistro de usuarios normales con correo y contrasena."""

    permission_classes = [AllowAny]
    authentication_classes = _AUTENTICACION_SESION
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = ScopeThrottle.REGISTRO

    @extend_schema(
        tags=["Auth"],
        summary="Registrar usuario con correo",
        request=RegistroCorreoEntradaSerializer,
        responses={
            status.HTTP_201_CREATED: DetalleSalidaSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Crea un usuario activo con rol encuestado a partir del correo."""
        entrada = RegistroCorreoEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        try:
            registrar_usuario_por_correo(datos["correo"], datos["contrasena"])
        except (
            UsernameDuplicadoError,
            EmailDuplicadoError,
            ContrasenasNoCoincidenError,
            ContrasenaInvalidaError,
        ) as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detalle": MensajesAuth.USUARIO_REGISTRADO},
            status=status.HTTP_201_CREATED,
        )


class SolicitarRestaurarPasswordView(APIView):
    """Solicita enlace de restauracion de contrasena por correo."""

    permission_classes = [AllowAny]
    authentication_classes = _AUTENTICACION_SESION
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = ScopeThrottle.RESTAURAR_PASSWORD

    @extend_schema(
        tags=["Auth"],
        summary="Solicitar restaurar contraseña",
        request=SolicitarRestaurarPasswordEntradaSerializer,
        responses={status.HTTP_200_OK: DetalleSalidaSerializer},
    )
    def post(self, solicitud: Request) -> Response:
        """Procesa solicitud sin revelar si el correo existe."""
        entrada = SolicitarRestaurarPasswordEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        solicitar_restaurar_password(entrada.validated_data["email"])
        return Response({"detalle": MensajesAuth.SOLICITUD_RESTAURAR_CONTRASENA})


class RestaurarPasswordView(APIView):
    """Restaura contrasena con uid y token del enlace."""

    permission_classes = [AllowAny]
    authentication_classes = _AUTENTICACION_SESION
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = ScopeThrottle.RESTAURAR_PASSWORD

    @extend_schema(
        tags=["Auth"],
        summary="Restaurar contraseña",
        request=RestaurarPasswordEntradaSerializer,
        responses={
            status.HTTP_200_OK: DetalleSalidaSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Valida token y establece nueva contrasena."""
        entrada = RestaurarPasswordEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        try:
            restaurar_password(
                datos["uid"],
                datos["token"],
                datos["password_nueva"],
                datos["password_confirmacion"],
            )
        except (
            TokenRestaurarInvalidoError,
            ContrasenasNoCoincidenError,
            ContrasenaInvalidaError,
        ) as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detalle": MensajesAuth.CONTRASENA_RESTAURADA})


class ContactoView(APIView):
    """Recibe mensajes del formulario de contacto publico."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = ScopeThrottle.CONTACTO

    @extend_schema(
        tags=["Contacto"],
        summary="Enviar mensaje de contacto",
        request=ContactoEntradaSerializer,
        responses={
            status.HTTP_200_OK: DetalleSalidaSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Envia mensaje al correo de soporte configurado en interfaz."""
        entrada = ContactoEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        try:
            enviar_contacto(entrada.validated_data)
        except ContactoSinEmailSoporteError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detalle": MensajesContacto.ENVIADO})


class MisRespuestasView(APIView):
    """Lista sesiones anonimas vinculadas al usuario autenticado."""

    permission_classes = [PermisoUsuarioAutenticado401]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Perfil"],
        summary="Historial de respuestas del usuario",
        responses={
            status.HTTP_200_OK: MisRespuestasSalidaSerializer,
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def get(self, solicitud: Request) -> Response:
        """Retorna sesiones de formularios asociadas al usuario autenticado."""
        historial = construir_historial_respuestas_usuario(solicitud.user)
        return Response({"resultados": historial}, status=status.HTTP_200_OK)


class MisRespuestasExportarView(APIView):
    """Descarga las respuestas de una sesion propia del usuario autenticado."""

    permission_classes = [PermisoUsuarioAutenticado401]
    authentication_classes = _AUTENTICACION_SESION

    @extend_schema(
        tags=["Perfil"],
        summary="Exportar respuestas de una sesion del usuario",
        responses={
            (status.HTTP_200_OK, "application/pdf"): bytes,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=_DETALLE_ERROR),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response=_DETALLE_ERROR),
        },
    )
    def get(self, solicitud: Request, uuid_sesion: UUID) -> HttpResponse:
        """Genera y descarga el archivo de respuestas de la sesion indicada."""
        formato = solicitud.query_params.get("formato", FormatoExportacion.XLSX)
        if formato not in FORMATOS_DESCARGA_DIRECTA:
            return Response(
                {"detalle": MensajesExportacionApi.FORMATO_NO_SOPORTADO},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            contenido, mime, extension = exportar_respuestas_sesion_usuario(
                solicitud.user,
                uuid_sesion,
                formato,
            )
        except SesionNoPerteneceUsuarioError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        respuesta = HttpResponse(contenido, content_type=mime)
        nombre_archivo = f"mis_respuestas_{uuid_sesion}.{extension}"
        respuesta["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'
        return respuesta
