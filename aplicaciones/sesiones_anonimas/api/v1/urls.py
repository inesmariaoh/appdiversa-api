"""
Rutas de la API de sesiones anonimas v1.
"""

from django.urls import path

from aplicaciones.sesiones_anonimas.api.v1.views import (
    CrearSesionAnonimaView,
    EnviarCopiaRespuestasView,
    EvaluarReglasPreguntaView,
    EvaluarReglasSesionView,
    FinalizarFormularioView,
    RespuestasSesionView,
    ResumenFormularioSesionView,
    ValidarFinalizacionView,
    VincularUsuarioSesionView,
)

urlpatterns = [
    path("", CrearSesionAnonimaView.as_view(), name="crear-sesion-anonima"),
    path(
        "<uuid:uuid_sesion>/respuestas/",
        RespuestasSesionView.as_view(),
        name="respuestas-sesion",
    ),
    path(
        "<uuid:uuid_sesion>/validar-finalizacion/",
        ValidarFinalizacionView.as_view(),
        name="validar-finalizacion-sesion",
    ),
    path(
        "<uuid:uuid_sesion>/finalizar/",
        FinalizarFormularioView.as_view(),
        name="finalizar-sesion",
    ),
    path(
        "<uuid:uuid_sesion>/resumen/",
        ResumenFormularioSesionView.as_view(),
        name="resumen-sesion",
    ),
    path(
        "<uuid:uuid_sesion>/evaluar-reglas/",
        EvaluarReglasSesionView.as_view(),
        name="evaluar-reglas-sesion",
    ),
    path(
        "<uuid:uuid_sesion>/preguntas/<str:codigo_pregunta>/evaluar-reglas/",
        EvaluarReglasPreguntaView.as_view(),
        name="evaluar-reglas-pregunta",
    ),
    path(
        "<uuid:uuid_sesion>/enviar-copia/",
        EnviarCopiaRespuestasView.as_view(),
        name="enviar-copia-respuestas",
    ),
    path(
        "<uuid:uuid_sesion>/vincular-usuario/",
        VincularUsuarioSesionView.as_view(),
        name="vincular-usuario-sesion",
    ),
]
