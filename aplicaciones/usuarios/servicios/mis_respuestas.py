"""
Servicios de historial de respuestas del usuario autenticado.
"""

from django.contrib.auth.models import AbstractBaseUser
from django.db.models import Count, Q

from aplicaciones.sesiones_anonimas.selectores import listar_sesiones_vinculadas_usuario


def construir_historial_respuestas_usuario(
    usuario: AbstractBaseUser,
) -> list[dict[str, object]]:
    """Construye el listado de sesiones vinculadas al usuario autenticado."""
    sesiones = listar_sesiones_vinculadas_usuario(usuario).annotate(
        total_respuestas=Count(
            "respuestas",
            filter=Q(respuestas__esta_eliminado=False),
        ),
    )
    return [
        {
            "uuid_sesion": str(sesion.uuid_sesion),
            "uuid_formulario": str(sesion.formulario.uuid),
            "codigo_formulario": sesion.formulario.codigo,
            "nombre_formulario": sesion.formulario.nombre,
            "estado": sesion.estado,
            "fecha_inicio": sesion.fecha_inicio,
            "fecha_ultima_actividad": sesion.fecha_ultima_actividad,
            "fecha_finalizacion": sesion.fecha_ultima_actividad,
            "total_respuestas": sesion.total_respuestas,
            "es_offline": sesion.es_offline,
        }
        for sesion in sesiones
    ]
