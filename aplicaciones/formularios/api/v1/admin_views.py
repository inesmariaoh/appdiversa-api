"""
Vistas de la API administrativa de formularios.
"""

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers, status
from aplicaciones.comun.autenticacion_sesion import AutenticacionSesionApi
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.formularios.api.v1.admin_serializers import (
    FormularioAdminSerializer,
    FormularioVersionAdminSerializer,
    OpcionRespuestaAdminSerializer,
    PreguntaAdminSerializer,
    ReglaPreguntaAdminSerializer,
    ReordenarPreguntasEntradaSerializer,
    SeccionFormularioAdminSerializer,
    TextoFormularioAdminSerializer,
    VersionCreacionEntradaSerializer,
)
from aplicaciones.formularios.api.v1.serializers import FormularioEstructuraSerializer
from aplicaciones.formularios.api.v1.util_admin import ejecutar_servicio_admin
from aplicaciones.formularios.excepciones_admin import (
    FormularioAdminNoEncontradoError,
    OpcionAdminNoEncontradaError,
    PreguntaAdminNoEncontradaError,
    ReglaAdminNoEncontradaError,
    SeccionAdminNoEncontradaError,
    TextoAdminNoEncontradoError,
    VersionAdminNoEncontradaError,
)
from aplicaciones.formularios.servicios_admin import (
    actualizar_formulario_admin,
    actualizar_opcion_admin,
    actualizar_pregunta_admin,
    actualizar_regla_admin,
    actualizar_seccion_admin,
    actualizar_texto_admin,
    cerrar_version_admin,
    crear_formulario_admin,
    crear_opcion_admin,
    crear_pregunta_admin,
    crear_regla_admin,
    crear_seccion_admin,
    crear_texto_admin,
    crear_version_admin,
    duplicar_pregunta_admin,
    eliminar_formulario_admin,
    eliminar_opcion_admin,
    eliminar_pregunta_admin,
    eliminar_regla_admin,
    eliminar_seccion_admin,
    eliminar_texto_admin,
    listar_formularios,
    listar_opciones_admin,
    listar_preguntas_admin,
    listar_reglas_admin,
    listar_secciones_admin,
    listar_textos_admin,
    listar_versiones_admin,
    publicar_version_admin,
    reordenar_preguntas_admin,
)
from aplicaciones.formularios.selectores_admin import obtener_estructura_formulario_admin
from aplicaciones.internacionalizacion.api.serializers import FiltroIdiomaSerializer
from aplicaciones.internacionalizacion.servicios import normalizar_codigo_idioma
from aplicaciones.usuarios.permisos import (
    PermisoConsultarFormulariosAdmin,
    PermisoEditarFormulariosAdmin,
    PermisoPublicarFormulariosAdmin,
)

_AUTENTICACION = [AutenticacionSesionApi]
_ERRORES_FORMULARIO = (FormularioAdminNoEncontradoError,)
_ERRORES_VERSION = (FormularioAdminNoEncontradoError, VersionAdminNoEncontradaError)
_ERRORES_SECCION = (SeccionAdminNoEncontradaError,)
_ERRORES_PREGUNTA = (PreguntaAdminNoEncontradaError,)
_ERRORES_OPCION = (OpcionAdminNoEncontradaError,)
_ERRORES_TEXTO = (TextoAdminNoEncontradoError,)
_ERRORES_REGLA = (ReglaAdminNoEncontradaError,)
_DETALLE_ERROR = inline_serializer(
    name="DetalleErrorAdminFormularios",
    fields={"detalle": serializers.CharField()},
)


class FormulariosAdminListCreateView(APIView):
    """Lista y crea formularios parametrizables."""

    authentication_classes = _AUTENTICACION

    def get_permissions(self):
        if self.request.method == "POST":
            return [PermisoEditarFormulariosAdmin()]
        return [PermisoConsultarFormulariosAdmin()]

    @extend_schema(tags=["Admin Formularios"], summary="Listar formularios")
    def get(self, solicitud: Request) -> Response:
        datos = FormularioAdminSerializer(listar_formularios(), many=True)
        return Response(datos.data, status=status.HTTP_200_OK)

    @extend_schema(tags=["Admin Formularios"], summary="Crear formulario")
    def post(self, solicitud: Request) -> Response:
        entrada = FormularioAdminSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: crear_formulario_admin(entrada.validated_data),
            _ERRORES_FORMULARIO,
        )
        if error:
            return error
        return Response(
            FormularioAdminSerializer(resultado).data,
            status=status.HTTP_201_CREATED,
        )


class FormularioAdminDetalleView(APIView):
    """Consulta, actualiza o elimina un formulario."""

    authentication_classes = _AUTENTICACION

    def get_permissions(self):
        if self.request.method == "GET":
            return [PermisoConsultarFormulariosAdmin()]
        return [PermisoEditarFormulariosAdmin()]

    @extend_schema(tags=["Admin Formularios"], summary="Detalle de formulario")
    def get(self, solicitud: Request, formulario_id: int) -> Response:
        from aplicaciones.formularios.selectores_admin import obtener_formulario_admin_por_id

        formulario = obtener_formulario_admin_por_id(formulario_id)
        if formulario is None:
            return Response(
                {"detalle": FormularioAdminNoEncontradoError().mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(FormularioAdminSerializer(formulario).data)

    @extend_schema(tags=["Admin Formularios"], summary="Actualizar formulario")
    def patch(self, solicitud: Request, formulario_id: int) -> Response:
        entrada = FormularioAdminSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: actualizar_formulario_admin(formulario_id, entrada.validated_data),
            _ERRORES_FORMULARIO,
        )
        if error:
            return error
        return Response(FormularioAdminSerializer(resultado).data)

    @extend_schema(tags=["Admin Formularios"], summary="Eliminar formulario")
    def delete(self, solicitud: Request, formulario_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: eliminar_formulario_admin(formulario_id),
            _ERRORES_FORMULARIO,
        )
        if error:
            return error
        return Response(FormularioAdminSerializer(resultado).data)


class FormularioAdminEstructuraView(APIView):
    """Expone la estructura completa de un formulario para el editor administrativo."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoConsultarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Estructura del formulario")
    def get(self, solicitud: Request, formulario_id: int) -> Response:
        filtros = FiltroIdiomaSerializer(data=solicitud.query_params)
        filtros.is_valid(raise_exception=True)
        codigo_idioma = normalizar_codigo_idioma(
            filtros.validated_data.get("idioma"),
        )

        estructura = obtener_estructura_formulario_admin(formulario_id)
        if estructura is None:
            return Response(
                {"detalle": FormularioAdminNoEncontradoError().mensaje},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializador = FormularioEstructuraSerializer(
            estructura,
            context={
                "idioma": codigo_idioma,
                "request": solicitud,
            },
        )
        return Response(serializador.data)


class FormularioVersionesAdminView(APIView):
    """Lista y crea versiones de un formulario."""

    authentication_classes = _AUTENTICACION

    def get_permissions(self):
        if self.request.method == "GET":
            return [PermisoConsultarFormulariosAdmin()]
        return [PermisoPublicarFormulariosAdmin()]

    @extend_schema(tags=["Admin Formularios"], summary="Listar versiones")
    def get(self, solicitud: Request, formulario_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: listar_versiones_admin(formulario_id),
            _ERRORES_FORMULARIO,
        )
        if error:
            return error
        datos = FormularioVersionAdminSerializer(resultado, many=True)
        return Response(datos.data)

    @extend_schema(tags=["Admin Formularios"], summary="Crear versión")
    def post(self, solicitud: Request, formulario_id: int) -> Response:
        entrada = VersionCreacionEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: crear_version_admin(formulario_id, entrada.validated_data),
            _ERRORES_FORMULARIO,
        )
        if error:
            return error
        return Response(
            FormularioVersionAdminSerializer(resultado).data,
            status=status.HTTP_201_CREATED,
        )


class FormularioVersionPublicarView(APIView):
    """Publica una version de formulario."""

    permission_classes = [PermisoPublicarFormulariosAdmin]
    authentication_classes = _AUTENTICACION

    @extend_schema(tags=["Admin Formularios"], summary="Publicar versión")
    def post(self, solicitud: Request, formulario_id: int, version_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: publicar_version_admin(formulario_id, version_id),
            _ERRORES_VERSION,
        )
        if error:
            return error
        return Response(FormularioVersionAdminSerializer(resultado).data)


class FormularioVersionCerrarView(APIView):
    """Cierra una version de formulario."""

    permission_classes = [PermisoPublicarFormulariosAdmin]
    authentication_classes = _AUTENTICACION

    @extend_schema(tags=["Admin Formularios"], summary="Cerrar versión")
    def post(self, solicitud: Request, formulario_id: int, version_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: cerrar_version_admin(formulario_id, version_id),
            _ERRORES_VERSION,
        )
        if error:
            return error
        return Response(FormularioVersionAdminSerializer(resultado).data)


class VersionSeccionesAdminView(APIView):
    """Lista y crea secciones de una version."""

    authentication_classes = _AUTENTICACION

    def get_permissions(self):
        if self.request.method == "GET":
            return [PermisoConsultarFormulariosAdmin()]
        return [PermisoEditarFormulariosAdmin()]

    @extend_schema(tags=["Admin Formularios"], summary="Listar secciones")
    def get(self, solicitud: Request, version_id: int) -> Response:
        _, error = ejecutar_servicio_admin(
            lambda: listar_secciones_admin(version_id),
            (VersionAdminNoEncontradaError,),
        )
        if error:
            return error
        return Response(
            SeccionFormularioAdminSerializer(
                listar_secciones_admin(version_id),
                many=True,
            ).data,
        )

    @extend_schema(tags=["Admin Formularios"], summary="Crear sección")
    def post(self, solicitud: Request, version_id: int) -> Response:
        entrada = SeccionFormularioAdminSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: crear_seccion_admin(version_id, entrada.validated_data),
            (VersionAdminNoEncontradaError,),
        )
        if error:
            return error
        return Response(
            SeccionFormularioAdminSerializer(resultado).data,
            status=status.HTTP_201_CREATED,
        )


class SeccionAdminDetalleView(APIView):
    """Actualiza o elimina una seccion."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Actualizar sección")
    def patch(self, solicitud: Request, seccion_id: int) -> Response:
        entrada = SeccionFormularioAdminSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: actualizar_seccion_admin(seccion_id, entrada.validated_data),
            _ERRORES_SECCION,
        )
        if error:
            return error
        return Response(SeccionFormularioAdminSerializer(resultado).data)

    @extend_schema(tags=["Admin Formularios"], summary="Eliminar sección")
    def delete(self, solicitud: Request, seccion_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: eliminar_seccion_admin(seccion_id),
            _ERRORES_SECCION,
        )
        if error:
            return error
        return Response(SeccionFormularioAdminSerializer(resultado).data)


class SeccionPreguntasAdminView(APIView):
    """Lista y crea preguntas de una seccion."""

    authentication_classes = _AUTENTICACION

    def get_permissions(self):
        if self.request.method == "GET":
            return [PermisoConsultarFormulariosAdmin()]
        return [PermisoEditarFormulariosAdmin()]

    @extend_schema(tags=["Admin Preguntas"], summary="Listar preguntas")
    def get(self, solicitud: Request, seccion_id: int) -> Response:
        _, error = ejecutar_servicio_admin(
            lambda: listar_preguntas_admin(seccion_id),
            _ERRORES_SECCION,
        )
        if error:
            return error
        return Response(
            PreguntaAdminSerializer(listar_preguntas_admin(seccion_id), many=True).data,
        )

    @extend_schema(tags=["Admin Preguntas"], summary="Crear pregunta")
    def post(self, solicitud: Request, seccion_id: int) -> Response:
        entrada = PreguntaAdminSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: crear_pregunta_admin(seccion_id, entrada.validated_data),
            _ERRORES_SECCION,
        )
        if error:
            return error
        return Response(
            PreguntaAdminSerializer(resultado).data,
            status=status.HTTP_201_CREATED,
        )


class PreguntaAdminDetalleView(APIView):
    """Actualiza o elimina una pregunta."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Preguntas"], summary="Actualizar pregunta")
    def patch(self, solicitud: Request, pregunta_id: int) -> Response:
        entrada = PreguntaAdminSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: actualizar_pregunta_admin(pregunta_id, entrada.validated_data),
            _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response(PreguntaAdminSerializer(resultado).data)

    @extend_schema(tags=["Admin Preguntas"], summary="Eliminar pregunta")
    def delete(self, solicitud: Request, pregunta_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: eliminar_pregunta_admin(pregunta_id),
            _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response(PreguntaAdminSerializer(resultado).data)


class PreguntaDuplicarView(APIView):
    """Duplica una pregunta existente."""

    permission_classes = [PermisoEditarFormulariosAdmin]
    authentication_classes = _AUTENTICACION

    @extend_schema(tags=["Admin Preguntas"], summary="Duplicar pregunta")
    def post(self, solicitud: Request, pregunta_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: duplicar_pregunta_admin(pregunta_id),
            _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response(
            PreguntaAdminSerializer(resultado).data,
            status=status.HTTP_201_CREATED,
        )


class PreguntasReordenarView(APIView):
    """Reordena preguntas de una o varias secciones."""

    permission_classes = [PermisoEditarFormulariosAdmin]
    authentication_classes = _AUTENTICACION

    @extend_schema(tags=["Admin Preguntas"], summary="Reordenar preguntas")
    def post(self, solicitud: Request) -> Response:
        entrada = ReordenarPreguntasEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        _, error = ejecutar_servicio_admin(
            lambda: reordenar_preguntas_admin(entrada.validated_data["preguntas"]),
            _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response({"mensaje": "Preguntas reordenadas correctamente."})


class PreguntaOpcionesAdminView(APIView):
    """Lista y crea opciones de una pregunta."""

    authentication_classes = _AUTENTICACION

    def get_permissions(self):
        if self.request.method == "GET":
            return [PermisoConsultarFormulariosAdmin()]
        return [PermisoEditarFormulariosAdmin()]

    @extend_schema(tags=["Admin Preguntas"], summary="Listar opciones")
    def get(self, solicitud: Request, pregunta_id: int) -> Response:
        _, error = ejecutar_servicio_admin(
            lambda: listar_opciones_admin(pregunta_id),
            _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response(
            OpcionRespuestaAdminSerializer(
                listar_opciones_admin(pregunta_id),
                many=True,
            ).data,
        )

    @extend_schema(tags=["Admin Preguntas"], summary="Crear opción")
    def post(self, solicitud: Request, pregunta_id: int) -> Response:
        entrada = OpcionRespuestaAdminSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: crear_opcion_admin(pregunta_id, entrada.validated_data),
            _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response(
            OpcionRespuestaAdminSerializer(resultado).data,
            status=status.HTTP_201_CREATED,
        )


class OpcionAdminDetalleView(APIView):
    """Actualiza o elimina una opcion."""

    permission_classes = [PermisoEditarFormulariosAdmin]
    authentication_classes = _AUTENTICACION

    @extend_schema(tags=["Admin Preguntas"], summary="Actualizar opción")
    def patch(self, solicitud: Request, opcion_id: int) -> Response:
        entrada = OpcionRespuestaAdminSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: actualizar_opcion_admin(opcion_id, entrada.validated_data),
            _ERRORES_OPCION,
        )
        if error:
            return error
        return Response(OpcionRespuestaAdminSerializer(resultado).data)

    @extend_schema(tags=["Admin Preguntas"], summary="Eliminar opción")
    def delete(self, solicitud: Request, opcion_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: eliminar_opcion_admin(opcion_id),
            _ERRORES_OPCION,
        )
        if error:
            return error
        return Response(OpcionRespuestaAdminSerializer(resultado).data)


class FormularioTextosAdminView(APIView):
    """Lista y crea textos de un formulario."""

    authentication_classes = _AUTENTICACION

    def get_permissions(self):
        if self.request.method == "GET":
            return [PermisoConsultarFormulariosAdmin()]
        return [PermisoEditarFormulariosAdmin()]

    @extend_schema(tags=["Admin Formularios"], summary="Listar textos")
    def get(self, solicitud: Request, formulario_id: int) -> Response:
        _, error = ejecutar_servicio_admin(
            lambda: listar_textos_admin(formulario_id),
            _ERRORES_FORMULARIO,
        )
        if error:
            return error
        return Response(
            TextoFormularioAdminSerializer(
                listar_textos_admin(formulario_id),
                many=True,
            ).data,
        )

    @extend_schema(tags=["Admin Formularios"], summary="Crear texto")
    def post(self, solicitud: Request, formulario_id: int) -> Response:
        entrada = TextoFormularioAdminSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: crear_texto_admin(formulario_id, entrada.validated_data),
            _ERRORES_FORMULARIO,
        )
        if error:
            return error
        return Response(
            TextoFormularioAdminSerializer(resultado).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(tags=["Admin Formularios"], summary="Actualizar textos en bloque")
    def patch(self, solicitud: Request, formulario_id: int) -> Response:
        from aplicaciones.formularios.api.v1.admin_serializers import (
            TextosBulkEntradaSerializer,
        )
        from aplicaciones.formularios.servicios_admin_formulario import (
            actualizar_textos_formulario_admin,
        )

        entrada = TextosBulkEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: actualizar_textos_formulario_admin(
                formulario_id,
                entrada.validated_data["textos"],
            ),
            _ERRORES_FORMULARIO,
        )
        if error:
            return error
        return Response(TextoFormularioAdminSerializer(resultado, many=True).data)


class TextoAdminDetalleView(APIView):
    """Actualiza o elimina un texto."""

    permission_classes = [PermisoEditarFormulariosAdmin]
    authentication_classes = _AUTENTICACION

    @extend_schema(tags=["Admin Formularios"], summary="Actualizar texto")
    def patch(self, solicitud: Request, texto_id: int) -> Response:
        entrada = TextoFormularioAdminSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: actualizar_texto_admin(texto_id, entrada.validated_data),
            _ERRORES_TEXTO,
        )
        if error:
            return error
        return Response(TextoFormularioAdminSerializer(resultado).data)

    @extend_schema(tags=["Admin Formularios"], summary="Eliminar texto")
    def delete(self, solicitud: Request, texto_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: eliminar_texto_admin(texto_id),
            _ERRORES_TEXTO,
        )
        if error:
            return error
        return Response(TextoFormularioAdminSerializer(resultado).data)


class PreguntaReglasAdminView(APIView):
    """Lista y crea reglas de una pregunta."""

    authentication_classes = _AUTENTICACION

    def get_permissions(self):
        if self.request.method == "GET":
            return [PermisoConsultarFormulariosAdmin()]
        return [PermisoEditarFormulariosAdmin()]

    @extend_schema(tags=["Admin Reglas"], summary="Listar reglas")
    def get(self, solicitud: Request, pregunta_id: int) -> Response:
        _, error = ejecutar_servicio_admin(
            lambda: listar_reglas_admin(pregunta_id),
            _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response(
            ReglaPreguntaAdminSerializer(
                listar_reglas_admin(pregunta_id),
                many=True,
            ).data,
        )

    @extend_schema(tags=["Admin Reglas"], summary="Crear regla")
    def post(self, solicitud: Request, pregunta_id: int) -> Response:
        entrada = ReglaPreguntaAdminSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: crear_regla_admin(pregunta_id, entrada.validated_data),
            _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response(
            ReglaPreguntaAdminSerializer(resultado).data,
            status=status.HTTP_201_CREATED,
        )


class ReglaAdminDetalleView(APIView):
    """Actualiza o elimina una regla."""

    permission_classes = [PermisoEditarFormulariosAdmin]
    authentication_classes = _AUTENTICACION

    @extend_schema(tags=["Admin Reglas"], summary="Actualizar regla")
    def patch(self, solicitud: Request, regla_id: int) -> Response:
        entrada = ReglaPreguntaAdminSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: actualizar_regla_admin(regla_id, entrada.validated_data),
            _ERRORES_REGLA,
        )
        if error:
            return error
        return Response(ReglaPreguntaAdminSerializer(resultado).data)

    @extend_schema(tags=["Admin Reglas"], summary="Eliminar regla")
    def delete(self, solicitud: Request, regla_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: eliminar_regla_admin(regla_id),
            _ERRORES_REGLA,
        )
        if error:
            return error
        return Response(ReglaPreguntaAdminSerializer(resultado).data)
