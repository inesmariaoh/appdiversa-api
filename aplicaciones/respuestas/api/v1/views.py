"""
Vistas de la API de respuestas.
"""

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.comun.spectacular_parametros import PARAMETROS_SESION_ANONIMA
from aplicaciones.respuestas.api.v1.serializers import (
    GuardarRespuestaEntradaSerializer,
    GuardarRespuestaSalidaSerializer,
)
from aplicaciones.respuestas.excepciones import (
    OrigenRespuestaInvalidoError,
    PreguntaNoExisteError,
    SesionRespuestaNoExisteError,
    ValorInvalidoError,
    ValorNoPerteneceCatalogoError,
)
from aplicaciones.formularios.reglas.servicio import evaluar_reglas_sesion
from aplicaciones.respuestas.servicios import guardar_o_actualizar_respuesta
from aplicaciones.sesiones_anonimas.permisos import PermisoSesionAnonimaValida

_DETALLE_ERROR_SERIALIZER = inline_serializer(
    name="DetalleErrorRespuesta",
    fields={"detalle": serializers.CharField()},
)


class GuardarRespuestaView(APIView):
    """Guarda o actualiza una respuesta anonima."""

    permission_classes = [PermisoSesionAnonimaValida]

    @extend_schema(
        tags=["Respuestas"],
        summary="Guardar o actualizar respuesta",
        description=(
            "Crea o actualiza una respuesta para una pregunta dentro de una "
            "sesion anonima. El backend determina el campo de almacenamiento "
            "segun el tipo de pregunta."
        ),
        parameters=PARAMETROS_SESION_ANONIMA,
        request=GuardarRespuestaEntradaSerializer,
        responses={
            status.HTTP_201_CREATED: GuardarRespuestaSalidaSerializer,
            status.HTTP_200_OK: GuardarRespuestaSalidaSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response=_DETALLE_ERROR_SERIALIZER,
            ),
        },
    )
    def post(self, solicitud: Request) -> Response:
        """Guarda o actualiza una respuesta."""
        entrada = GuardarRespuestaEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data

        try:
            resultado = guardar_o_actualizar_respuesta(
                uuid_sesion=datos["uuid_sesion"],
                codigo_pregunta=datos["codigo_pregunta"],
                valor=datos["valor"],
                observacion=datos.get("observacion", ""),
                origen_respuesta=datos.get("origen_respuesta", "web"),
                fecha_respuesta_cliente=datos.get("fecha_respuesta_cliente"),
            )
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
        except (
            ValorInvalidoError,
            ValorNoPerteneceCatalogoError,
            OrigenRespuestaInvalidoError,
        ) as error:
            return Response(
                {"detalle": error.mensaje},
                status=status.HTTP_400_BAD_REQUEST,
            )

        salida = {
            "uuid_sesion": datos["uuid_sesion"],
            "codigo_pregunta": datos["codigo_pregunta"],
            "version_respuesta": resultado.respuesta.version_respuesta,
            "origen_respuesta": resultado.respuesta.origen_respuesta,
            "requiere_sincronizacion": resultado.respuesta.requiere_sincronizacion,
            "esta_eliminado": resultado.respuesta.esta_eliminado,
            "reglas": evaluar_reglas_sesion(datos["uuid_sesion"]),
        }
        serializador = GuardarRespuestaSalidaSerializer(salida)
        codigo_estado = (
            status.HTTP_201_CREATED if resultado.fue_creada else status.HTTP_200_OK
        )
        return Response(serializador.data, status=codigo_estado)
