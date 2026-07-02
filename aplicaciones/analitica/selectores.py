"""
Selectores de consulta para analitica.
"""

from datetime import datetime

from django.db.models import QuerySet

from aplicaciones.respuestas.models import Respuesta


def obtener_respuestas_para_analitica(
    formulario_codigo: str | None = None,
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
    estado_sesion: str | None = None,
) -> QuerySet[Respuesta]:
    """Retorna respuestas activas optimizadas para exportacion analitica."""
    consulta = (
        Respuesta.objects.filter(
            esta_eliminado=False,
            sesion__esta_eliminado=False,
        )
        .select_related(
            "sesion",
            "sesion__formulario",
            "sesion__version_formulario",
            "pregunta",
            "pregunta__seccion",
            "pregunta__catalogo_asociado",
        )
        .order_by(
            "sesion__fecha_inicio",
            "pregunta__seccion__orden",
            "pregunta__orden",
        )
    )

    if formulario_codigo:
        consulta = consulta.filter(sesion__formulario__codigo=formulario_codigo)

    if estado_sesion:
        consulta = consulta.filter(sesion__estado=estado_sesion)

    if fecha_inicio is not None:
        consulta = consulta.filter(sesion__fecha_inicio__gte=fecha_inicio)

    if fecha_fin is not None:
        consulta = consulta.filter(sesion__fecha_inicio__lte=fecha_fin)

    return consulta
