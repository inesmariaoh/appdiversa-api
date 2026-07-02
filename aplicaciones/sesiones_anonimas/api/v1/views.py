"""
Vistas de la API de sesiones anonimas.
"""

from uuid import UUID

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.comun.spectacular_parametros import PARAMETROS_SESION_ANONIMA
from aplicaciones.formularios.api.v1.reglas_serializers import ResultadoReglasSerializer
from aplicaciones.formularios.reglas.servicio import (
    evaluar_reglas_para_respuesta,
    evaluar_reglas_sesion,
)
from aplicaciones.respuestas.api.v1.serializers import RespuestasSesionSerializer
from aplicaciones.respuestas.excepciones import (
    FormularioYaFinalizadoError,
    PreguntaNoExisteError,
    SesionRespuestaNoExisteError,
)
from aplicaciones.respuestas.servicios import (
    finalizar_formulario_sesion,
    listar_respuestas_sesion,
    obtener_respuestas_de_sesion,
    resumen_respuestas_sesion,
    validar_formulario_sesion,
)
from aplicaciones.sesiones_anonimas.api.v1.finalizacion_serializers import (
    FinalizacionEntradaSerializer,
    FinalizacionFormularioSerializer,
    ResumenFormularioSesionSerializer,
    ValidacionFinalizacionSerializer,
)
from aplicaciones.sesiones_anonimas.api.v1.serializers import (
    CrearSesionAnonimaEntradaSerializer,
    SesionAnonimaSerializer,
)

from aplicaciones.formularios.excepciones import FormularioAunNoDisponibleError
from aplicaciones.sesiones_anonimas.constantes import MensajesSesionApi
from aplicaciones.sesiones_anonimas.excepciones import (
    FormularioSesionNoDisponibleError,
    SesionYaVinculadaOtroUsuarioError,
    VersionSesionNoDisponibleError,
)
from aplicaciones.comun.autenticacion_sesion import AutenticacionSesionApi
from aplicaciones.sesiones_anonimas.permisos import (
    PermisoSesionAnonimaOUsuarioVinculado,
    PermisoSesionAnonimaValida,
)
from aplicaciones.sesiones_anonimas.seguridad import (
    extraer_credenciales_sesion,
)
from aplicaciones.sesiones_anonimas.servicios import crear_o_obtener_sesion_anonima
from aplicaciones.sesiones_anonimas.servicios_vinculacion import (
    vincular_sesion_anonima_a_usuario,
)
from aplicaciones.usuarios.permisos import PermisoUsuarioAutenticado

_DETALLE_ERROR_SERIALIZER = inline_serializer(
    name="DetalleErrorSesion",
    fields={"detalle": serializers.CharField()},
)


class CrearSesionAnonimaView(APIView):
    """Crea o reutiliza una sesion anonima."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Sesiones"],
        summary="Crear o reutilizar sesión anónima",
        description=(
            "Registra una sesión anónima asociada a un formulario publicado "
            "o reutiliza una sesión existente por uuid_sesion. "
            "Si no se envía token_cliente, el backend genera uno seguro."
        ),
        request=CrearSesionAnonimaEntradaSerializer,
        responses={
            status.HTTP_201_CREATED: SesionAnonimaSerializer,
            status.HTTP_200_OK: SesionAnonimaSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
                description=(
                    "Formulario publicado con fecha de inicio futura "
                    "(aún no disponible para diligenciar)."
                ),
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
                description="Formulario no publicado, vencido o inexistente.",
            ),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Crea o reutiliza una sesion anonima."""
        entrada = CrearSesionAnonimaEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        try:
            resultado = crear_o_obtener_sesion_anonima(
                uuid_sesion=datos["uuid_sesion"],
                uuid_formulario=datos["uuid_formulario"],
                solicitud=solicitud,
                token_cliente=datos.get("token_cliente", ""),
                idioma=datos.get("idioma", ""),
                zona_horaria=datos.get("zona_horaria", ""),
                es_offline=datos.get("es_offline", False),
            )
        except FormularioSesionNoDisponibleError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        except FormularioAunNoDisponibleError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except VersionSesionNoDisponibleError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializador = SesionAnonimaSerializer(resultado.sesion)
        codigo_estado = (
            status.HTTP_201_CREATED if resultado.fue_creada else status.HTTP_200_OK
        )
        return Response(serializador.data, status=codigo_estado)


class RespuestasSesionView(APIView):
    """Lista las respuestas guardadas de una sesion anonima."""

    permission_classes = [PermisoSesionAnonimaValida]
    requiere_sesion_modificable = False

    @extend_schema(
        tags=["Sesiones"],
        summary="Listar respuestas de sesión",
        description="Retorna todas las respuestas guardadas para una sesión anónima.",
        parameters=PARAMETROS_SESION_ANONIMA,
        responses={
            status.HTTP_200_OK: RespuestasSesionSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def get(self, solicitud: Request, uuid_sesion: UUID) -> Response:
        """Retorna las respuestas asociadas a la sesion."""
        try:
            sesion = listar_respuestas_sesion(uuid_sesion)
            respuestas = obtener_respuestas_de_sesion(sesion)
        except SesionRespuestaNoExisteError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        datos = {
            "uuid_sesion": sesion.uuid_sesion,
            "estado": sesion.estado,
            "respuestas": respuestas,
        }
        serializador = RespuestasSesionSerializer(datos)
        return Response(serializador.data, status=status.HTTP_200_OK)


class ValidarFinalizacionView(APIView):
    """Valida preguntas obligatorias antes de finalizar el formulario."""

    permission_classes = [PermisoSesionAnonimaValida]

    @extend_schema(
        tags=["Sesiones"],
        summary="Validar finalización de formulario",
        description=(
            "Verifica que todas las preguntas obligatorias de la sesión "
            "tengan una respuesta útil."
        ),
        parameters=PARAMETROS_SESION_ANONIMA,
        responses={
            status.HTTP_200_OK: ValidacionFinalizacionSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def post(self, solicitud: Request, uuid_sesion: UUID) -> Response:
        """Ejecuta la validacion final del formulario de la sesion."""
        try:
            resultado = validar_formulario_sesion(uuid_sesion)
        except SesionRespuestaNoExisteError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializador = ValidacionFinalizacionSerializer(resultado)
        return Response(serializador.data, status=status.HTTP_200_OK)


class FinalizarFormularioView(APIView):
    """Finaliza el diligenciamiento anonimo del formulario."""

    permission_classes = [PermisoSesionAnonimaValida]

    @extend_schema(
        tags=["Sesiones", "Respuestas"],
        summary="Finalizar formulario de sesión",
        description=(
            "Finaliza la sesión si todas las preguntas obligatorias "
            "tienen respuesta útil."
        ),
        parameters=PARAMETROS_SESION_ANONIMA,
        request=FinalizacionEntradaSerializer,
        responses={
            status.HTTP_200_OK: FinalizacionFormularioSerializer,
            status.HTTP_400_BAD_REQUEST: ValidacionFinalizacionSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def post(self, solicitud: Request, uuid_sesion: UUID) -> Response:
        """Finaliza el formulario asociado a la sesion anonima."""
        entrada = FinalizacionEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        correo = entrada.validated_data.get("correo", "")
        try:
            resultado = finalizar_formulario_sesion(
                uuid_sesion,
                correo_notificacion=correo or None,
            )
        except SesionRespuestaNoExisteError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        except FormularioYaFinalizadoError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not resultado.get("es_valido", True):
            serializador = ValidacionFinalizacionSerializer(resultado)
            return Response(serializador.data, status=status.HTTP_400_BAD_REQUEST)

        serializador = FinalizacionFormularioSerializer(resultado)
        return Response(serializador.data, status=status.HTTP_200_OK)


class ResumenFormularioSesionView(APIView):
    """Retorna el resumen de respuestas de una sesion anonima."""

    permission_classes = [PermisoSesionAnonimaOUsuarioVinculado]
    authentication_classes = [AutenticacionSesionApi]
    requiere_sesion_modificable = False

    @extend_schema(
        tags=["Sesiones", "Respuestas"],
        summary="Resumen de respuestas de sesión",
        description="Retorna el resumen de respuestas activas de la sesión.",
        parameters=PARAMETROS_SESION_ANONIMA,
        responses={
            status.HTTP_200_OK: ResumenFormularioSesionSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def get(self, solicitud: Request, uuid_sesion: UUID) -> Response:
        """Retorna el resumen del formulario diligenciado en la sesion."""
        try:
            resumen = resumen_respuestas_sesion(uuid_sesion)
        except SesionRespuestaNoExisteError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializador = ResumenFormularioSesionSerializer(resumen)
        return Response(serializador.data, status=status.HTTP_200_OK)


class EvaluarReglasSesionView(APIView):
    """Evalua todas las reglas activas de la sesion."""

    permission_classes = [PermisoSesionAnonimaValida]

    @extend_schema(
        tags=["Reglas", "Sesiones"],
        summary="Evaluar reglas de sesión",
        description=(
            "Evalúa las reglas condicionales activas del formulario "
            "según las respuestas registradas en la sesión."
        ),
        parameters=PARAMETROS_SESION_ANONIMA,
        responses={
            status.HTTP_200_OK: ResultadoReglasSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def post(self, solicitud: Request, uuid_sesion: UUID) -> Response:
        """Retorna el resultado completo de reglas para la sesion."""
        try:
            resultado = evaluar_reglas_sesion(uuid_sesion)
        except SesionRespuestaNoExisteError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializador = ResultadoReglasSerializer(resultado)
        return Response(serializador.data, status=status.HTTP_200_OK)


class EvaluarReglasPreguntaView(APIView):
    """Evalua reglas asociadas a una pregunta origen."""

    permission_classes = [PermisoSesionAnonimaValida]

    @extend_schema(
        tags=["Reglas", "Sesiones"],
        summary="Evaluar reglas por pregunta",
        description=(
            "Evalúa las reglas cuya pregunta origen coincide con el código "
            "indicado, según las respuestas de la sesión."
        ),
        parameters=PARAMETROS_SESION_ANONIMA,
        responses={
            status.HTTP_200_OK: ResultadoReglasSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def post(
        self,
        solicitud: Request,
        uuid_sesion: UUID,
        codigo_pregunta: str,
    ) -> Response:
        """Retorna el impacto de reglas relacionadas con la pregunta."""
        try:
            resultado = evaluar_reglas_para_respuesta(uuid_sesion, codigo_pregunta)
        except SesionRespuestaNoExisteError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PreguntaNoExisteError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializador = ResultadoReglasSerializer(resultado)
        return Response(serializador.data, status=status.HTTP_200_OK)


class EnviarCopiaRespuestasView(APIView):
    """Envia copia del resumen de respuestas por correo electronico."""

    permission_classes = [PermisoSesionAnonimaValida]
    requiere_sesion_modificable = False
    responder_404_sesion_inexistente = True

    @extend_schema(
        tags=["Sesiones", "Notificaciones"],
        summary="Enviar copia de respuestas por correo",
        parameters=PARAMETROS_SESION_ANONIMA,
        request=inline_serializer(
            name="EnviarCopiaRespuestasEntrada",
            fields={"correo": serializers.EmailField()},
        ),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
                description="Copia enviada correctamente.",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def post(self, solicitud: Request, uuid_sesion: UUID) -> Response:
        """Envia resumen de respuestas al correo indicado."""
        from aplicaciones.sesiones_anonimas.servicios_copia import (
            enviar_copia_respuestas_sesion,
        )
        from aplicaciones.usuarios.constantes import MensajesCopiaRespuestas
        from aplicaciones.usuarios.serializers import EnviarCopiaRespuestasEntradaSerializer

        entrada = EnviarCopiaRespuestasEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        try:
            enviar_copia_respuestas_sesion(
                uuid_sesion,
                entrada.validated_data["correo"],
            )
        except SesionRespuestaNoExisteError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"detalle": MensajesCopiaRespuestas.ENVIADA})


_AUTENTICACION_SESION = [AutenticacionSesionApi]


class VincularUsuarioSesionView(APIView):
    """Asocia una sesion anonima finalizada o en curso al usuario autenticado."""

    permission_classes = [PermisoUsuarioAutenticado, PermisoSesionAnonimaValida]
    authentication_classes = _AUTENTICACION_SESION
    requiere_sesion_modificable = False
    responder_404_sesion_inexistente = True

    @extend_schema(
        tags=["Sesiones", "Auth"],
        summary="Vincular sesión anónima al usuario autenticado",
        parameters=PARAMETROS_SESION_ANONIMA,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
                description="Sesión vinculada correctamente.",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def post(self, solicitud: Request, uuid_sesion: UUID) -> Response:
        """Vincula la sesion anonima validada al usuario autenticado."""
        credenciales = extraer_credenciales_sesion(solicitud, uuid_sesion)
        try:
            vincular_sesion_anonima_a_usuario(
                uuid_sesion,
                credenciales.token_cliente,
                solicitud.user,
            )
        except SesionYaVinculadaOtroUsuarioError as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detalle": MensajesSesionApi.SESION_VINCULADA})
