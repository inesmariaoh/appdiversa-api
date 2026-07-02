"""
Vistas de fachada bajo /api/v1/admin/formularios/{id}/ para el panel administrativo.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from aplicaciones.comun.autenticacion_sesion import AutenticacionSesionApi
from aplicaciones.formularios.api.v1.admin_serializers import (
    FormularioAdminSerializer,
    OpcionRespuestaAdminSerializer,
    PreguntaAdminSerializer,
    ReordenarCodigosEntradaSerializer,
    ReglaFormularioEntradaSerializer,
    SeccionFormularioAdminSerializer,
)
from aplicaciones.formularios.api.v1.util_admin import ejecutar_servicio_admin
from aplicaciones.formularios.constantes_admin import MensajesFormularioAdmin
from aplicaciones.formularios.excepciones_admin import (
    FormularioAdminNoEncontradoError,
    OpcionAdminNoEncontradaError,
    PreguntaAdminNoEncontradaError,
    ReglaAdminNoEncontradaError,
    SeccionAdminNoEncontradaError,
    VersionAdminNoEncontradaError,
)
from aplicaciones.formularios.servicios_admin_formulario import (
    actualizar_opcion_formulario_admin,
    actualizar_pregunta_formulario_admin,
    actualizar_regla_formulario_admin,
    actualizar_seccion_formulario_admin,
    cerrar_formulario_admin,
    crear_opcion_formulario_admin,
    crear_pregunta_formulario_admin,
    crear_regla_formulario_admin,
    crear_seccion_formulario_admin,
    duplicar_pregunta_formulario_admin,
    eliminar_opcion_formulario_admin,
    eliminar_pregunta_formulario_admin,
    eliminar_regla_formulario_admin,
    eliminar_seccion_formulario_admin,
    listar_reglas_formulario_admin_serializadas,
    publicar_formulario_admin,
    reordenar_opciones_formulario_admin,
    reordenar_preguntas_formulario_admin,
    reordenar_secciones_formulario_admin,
    serializar_regla_frontend,
)
from aplicaciones.usuarios.permisos import (
    PermisoConsultarFormulariosAdmin,
    PermisoEditarFormulariosAdmin,
    PermisoPublicarFormulariosAdmin,
)

_AUTENTICACION = [AutenticacionSesionApi]
_ERRORES_FORMULARIO = (FormularioAdminNoEncontradoError, VersionAdminNoEncontradaError)
_ERRORES_SECCION = (SeccionAdminNoEncontradaError,)
_ERRORES_PREGUNTA = (PreguntaAdminNoEncontradaError,)
_ERRORES_OPCION = (OpcionAdminNoEncontradaError,)
_ERRORES_REGLA = (ReglaAdminNoEncontradaError,)


class FormularioSeccionesAdminView(APIView):
    """Crea secciones usando la ruta centrada en formulario."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Crear seccion por formulario")
    def post(self, solicitud: Request, formulario_id: int) -> Response:
        entrada = SeccionFormularioAdminSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: crear_seccion_formulario_admin(
                formulario_id,
                entrada.validated_data,
            ),
            _ERRORES_FORMULARIO,
        )
        if error:
            return error
        return Response(
            SeccionFormularioAdminSerializer(resultado).data,
            status=status.HTTP_201_CREATED,
        )


class FormularioSeccionDetalleAdminView(APIView):
    """Actualiza o elimina secciones por codigo."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Actualizar seccion por codigo")
    def patch(
        self,
        solicitud: Request,
        formulario_id: int,
        codigo_seccion: str,
    ) -> Response:
        entrada = SeccionFormularioAdminSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: actualizar_seccion_formulario_admin(
                formulario_id,
                codigo_seccion,
                entrada.validated_data,
            ),
            _ERRORES_SECCION,
        )
        if error:
            return error
        return Response(SeccionFormularioAdminSerializer(resultado).data)

    @extend_schema(tags=["Admin Formularios"], summary="Eliminar seccion por codigo")
    def delete(
        self,
        solicitud: Request,
        formulario_id: int,
        codigo_seccion: str,
    ) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: eliminar_seccion_formulario_admin(formulario_id, codigo_seccion),
            _ERRORES_SECCION,
        )
        if error:
            return error
        return Response(SeccionFormularioAdminSerializer(resultado).data)


class FormularioSeccionesReordenarAdminView(APIView):
    """Reordena secciones por codigos."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Reordenar secciones")
    def post(self, solicitud: Request, formulario_id: int) -> Response:
        entrada = ReordenarCodigosEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        _, error = ejecutar_servicio_admin(
            lambda: reordenar_secciones_formulario_admin(
                formulario_id,
                entrada.validated_data["codigos"],
            ),
            _ERRORES_SECCION,
        )
        if error:
            return error
        return Response(status=status.HTTP_200_OK)


class FormularioPreguntasAdminView(APIView):
    """Crea preguntas usando codigo de seccion."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Crear pregunta por formulario")
    def post(self, solicitud: Request, formulario_id: int) -> Response:
        entrada = PreguntaAdminSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        payload = dict(entrada.validated_data)
        payload["seccion_codigo"] = solicitud.data.get("seccion_codigo")
        resultado, error = ejecutar_servicio_admin(
            lambda: crear_pregunta_formulario_admin(formulario_id, payload),
            _ERRORES_PREGUNTA + _ERRORES_SECCION,
        )
        if error:
            return error
        return Response(
            PreguntaAdminSerializer(resultado).data,
            status=status.HTTP_201_CREATED,
        )


class FormularioPreguntaDetalleAdminView(APIView):
    """Actualiza, elimina o duplica preguntas por codigo."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Actualizar pregunta por codigo")
    def patch(
        self,
        solicitud: Request,
        formulario_id: int,
        codigo_pregunta: str,
    ) -> Response:
        payload = dict(solicitud.data)
        resultado, error = ejecutar_servicio_admin(
            lambda: actualizar_pregunta_formulario_admin(
                formulario_id,
                codigo_pregunta,
                payload,
            ),
            _ERRORES_PREGUNTA + _ERRORES_SECCION,
        )
        if error:
            return error
        return Response(PreguntaAdminSerializer(resultado).data)

    @extend_schema(tags=["Admin Formularios"], summary="Eliminar pregunta por codigo")
    def delete(
        self,
        solicitud: Request,
        formulario_id: int,
        codigo_pregunta: str,
    ) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: eliminar_pregunta_formulario_admin(formulario_id, codigo_pregunta),
            _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response(PreguntaAdminSerializer(resultado).data)


class FormularioPreguntaDuplicarAdminView(APIView):
    """Duplica una pregunta por codigo."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Duplicar pregunta por codigo")
    def post(
        self,
        solicitud: Request,
        formulario_id: int,
        codigo_pregunta: str,
    ) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: duplicar_pregunta_formulario_admin(formulario_id, codigo_pregunta),
            _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response(
            PreguntaAdminSerializer(resultado).data,
            status=status.HTTP_201_CREATED,
        )


class FormularioPreguntasReordenarAdminView(APIView):
    """Reordena preguntas por codigos."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Reordenar preguntas")
    def post(self, solicitud: Request, formulario_id: int) -> Response:
        entrada = ReordenarCodigosEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        _, error = ejecutar_servicio_admin(
            lambda: reordenar_preguntas_formulario_admin(
                formulario_id,
                entrada.validated_data["codigos"],
            ),
            _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response(status=status.HTTP_200_OK)


class FormularioPreguntaOpcionesAdminView(APIView):
    """Crea opciones en una pregunta identificada por codigo."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Crear opcion por codigo de pregunta")
    def post(
        self,
        solicitud: Request,
        formulario_id: int,
        codigo_pregunta: str,
    ) -> Response:
        entrada = OpcionRespuestaAdminSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: crear_opcion_formulario_admin(
                formulario_id,
                codigo_pregunta,
                entrada.validated_data,
            ),
            _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response(
            OpcionRespuestaAdminSerializer(resultado).data,
            status=status.HTTP_201_CREATED,
        )


class FormularioOpcionDetalleAdminView(APIView):
    """Actualiza o elimina opciones por codigo."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Actualizar opcion por codigo")
    def patch(
        self,
        solicitud: Request,
        formulario_id: int,
        codigo_opcion: str,
    ) -> Response:
        entrada = OpcionRespuestaAdminSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: actualizar_opcion_formulario_admin(
                formulario_id,
                codigo_opcion,
                entrada.validated_data,
            ),
            _ERRORES_OPCION,
        )
        if error:
            return error
        return Response(OpcionRespuestaAdminSerializer(resultado).data)

    @extend_schema(tags=["Admin Formularios"], summary="Eliminar opcion por codigo")
    def delete(
        self,
        solicitud: Request,
        formulario_id: int,
        codigo_opcion: str,
    ) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: eliminar_opcion_formulario_admin(formulario_id, codigo_opcion),
            _ERRORES_OPCION,
        )
        if error:
            return error
        return Response(OpcionRespuestaAdminSerializer(resultado).data)


class FormularioOpcionesReordenarAdminView(APIView):
    """Reordena opciones de una pregunta."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Reordenar opciones")
    def post(
        self,
        solicitud: Request,
        formulario_id: int,
        codigo_pregunta: str,
    ) -> Response:
        entrada = ReordenarCodigosEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        _, error = ejecutar_servicio_admin(
            lambda: reordenar_opciones_formulario_admin(
                formulario_id,
                codigo_pregunta,
                entrada.validated_data["codigos"],
            ),
            _ERRORES_OPCION + _ERRORES_PREGUNTA,
        )
        if error:
            return error
        return Response(status=status.HTTP_200_OK)


class FormularioReglasAdminView(APIView):
    """Lista y crea reglas del formulario usando codigos."""

    authentication_classes = _AUTENTICACION

    def get_permissions(self):
        if self.request.method == "GET":
            return [PermisoConsultarFormulariosAdmin()]
        return [PermisoEditarFormulariosAdmin()]

    @extend_schema(tags=["Admin Formularios"], summary="Listar reglas del formulario")
    def get(self, solicitud: Request, formulario_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: listar_reglas_formulario_admin_serializadas(formulario_id),
            _ERRORES_FORMULARIO,
        )
        if error:
            return error
        return Response(resultado)

    @extend_schema(tags=["Admin Formularios"], summary="Crear regla del formulario")
    def post(self, solicitud: Request, formulario_id: int) -> Response:
        entrada = ReglaFormularioEntradaSerializer(data=solicitud.data)
        entrada.is_valid(raise_exception=True)
        if not entrada.validated_data.get("pregunta_origen"):
            return Response(
                {"detalle": MensajesFormularioAdmin.PREGUNTA_NO_ENCONTRADA},
                status=status.HTTP_400_BAD_REQUEST,
            )
        resultado, error = ejecutar_servicio_admin(
            lambda: crear_regla_formulario_admin(
                formulario_id,
                entrada.validated_data,
            ),
            _ERRORES_REGLA + _ERRORES_PREGUNTA + _ERRORES_SECCION,
        )
        if error:
            return error
        return Response(
            serializar_regla_frontend(resultado),
            status=status.HTTP_201_CREATED,
        )


class FormularioReglaDetalleAdminView(APIView):
    """Actualiza o elimina reglas del formulario."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoEditarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Actualizar regla del formulario")
    def patch(
        self,
        solicitud: Request,
        formulario_id: int,
        regla_id: int,
    ) -> Response:
        entrada = ReglaFormularioEntradaSerializer(data=solicitud.data, partial=True)
        entrada.is_valid(raise_exception=True)
        resultado, error = ejecutar_servicio_admin(
            lambda: actualizar_regla_formulario_admin(
                formulario_id,
                regla_id,
                entrada.validated_data,
            ),
            _ERRORES_REGLA + _ERRORES_PREGUNTA + _ERRORES_SECCION,
        )
        if error:
            return error
        return Response(serializar_regla_frontend(resultado))

    @extend_schema(tags=["Admin Formularios"], summary="Eliminar regla del formulario")
    def delete(
        self,
        solicitud: Request,
        formulario_id: int,
        regla_id: int,
    ) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: eliminar_regla_formulario_admin(formulario_id, regla_id),
            _ERRORES_REGLA,
        )
        if error:
            return error
        return Response(serializar_regla_frontend(resultado))


class FormularioPublicarAdminView(APIView):
    """Publica la version borrador del formulario."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoPublicarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Publicar formulario")
    def post(self, solicitud: Request, formulario_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: publicar_formulario_admin(formulario_id),
            _ERRORES_FORMULARIO,
        )
        if error:
            return error
        return Response(FormularioAdminSerializer(resultado).data)


class FormularioCerrarAdminView(APIView):
    """Cierra la version publicada del formulario."""

    authentication_classes = _AUTENTICACION
    permission_classes = [PermisoPublicarFormulariosAdmin]

    @extend_schema(tags=["Admin Formularios"], summary="Cerrar formulario")
    def post(self, solicitud: Request, formulario_id: int) -> Response:
        resultado, error = ejecutar_servicio_admin(
            lambda: cerrar_formulario_admin(formulario_id),
            _ERRORES_FORMULARIO,
        )
        if error:
            return error
        return Response(FormularioAdminSerializer(resultado).data)
