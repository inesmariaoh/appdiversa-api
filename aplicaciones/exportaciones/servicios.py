"""
Servicios del motor transversal de exportaciones.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from aplicaciones.analitica.servicios import listar_respuestas_analiticas
from aplicaciones.archivos.constantes import OrigenArchivo, TipoArchivo
from aplicaciones.archivos.servicios import guardar_archivo
from aplicaciones.auditoria.constantes import AccionAuditoria
from aplicaciones.auditoria.servicios import crear_snapshot_modelo, registrar_auditoria
from aplicaciones.catalogos.models import Catalogo, ItemCatalogo
from aplicaciones.exportaciones.constantes import (
    EXTENSION_POR_FORMATO,
    EstadoExportacion,
    FormatoExportacion,
    MIME_POR_FORMATO,
    TipoExportacion,
)
from aplicaciones.exportaciones.excepciones import (
    ExportacionNoEncontradaError,
    FormatoExportacionNoSoportadoError,
)
from aplicaciones.exportaciones.generadores import obtener_generador_exportacion
from aplicaciones.exportaciones.models import Exportacion
from aplicaciones.exportaciones.selectores import obtener_exportacion_por_uuid
from aplicaciones.respuestas.models import Respuesta


def _parsear_fecha_filtro(valor: str | None) -> datetime | None:
    """Convierte un filtro de fecha ISO a datetime."""
    if not valor:
        return None
    valor_normalizado = valor.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(valor_normalizado)
    except ValueError:
        return None


def _obtener_registros_respuestas(parametros: dict[str, Any]) -> list[dict[str, Any]]:
    """Obtiene registros planos de respuestas segun filtros."""
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
        )
        .order_by("sesion__fecha_inicio", "pregunta__orden")
    )

    uuid_sesion = parametros.get("uuid_sesion")
    if uuid_sesion:
        consulta = consulta.filter(sesion__uuid_sesion=uuid_sesion)

    codigo_formulario = parametros.get("formulario_codigo") or parametros.get("formulario")
    if codigo_formulario:
        consulta = consulta.filter(sesion__formulario__codigo=codigo_formulario)

    numero_version = parametros.get("version") or parametros.get("numero_version")
    if numero_version is not None:
        consulta = consulta.filter(
            sesion__version_formulario__numero_version=int(numero_version),
        )

    estado_sesion = parametros.get("estado_sesion")
    if estado_sesion:
        consulta = consulta.filter(sesion__estado=estado_sesion)

    idioma = parametros.get("idioma") or parametros.get("idioma_sesion")
    if idioma:
        consulta = consulta.filter(sesion__idioma=idioma)

    fecha_inicio = _parsear_fecha_filtro(parametros.get("fecha_inicio"))
    fecha_fin = _parsear_fecha_filtro(parametros.get("fecha_fin"))
    if fecha_inicio:
        consulta = consulta.filter(sesion__fecha_inicio__gte=fecha_inicio)
    if fecha_fin:
        consulta = consulta.filter(sesion__fecha_inicio__lte=fecha_fin)

    registros: list[dict[str, Any]] = []
    for respuesta in consulta.iterator():
        registros.append(
            {
                "uuid_sesion": str(respuesta.sesion.uuid_sesion),
                "formulario_codigo": respuesta.sesion.formulario.codigo,
                "version": respuesta.sesion.version_formulario.numero_version,
                "estado_sesion": respuesta.sesion.estado,
                "pregunta_codigo": respuesta.pregunta.codigo,
                "pregunta_texto": respuesta.pregunta.texto,
                "tipo_pregunta": respuesta.pregunta.tipo_pregunta,
                "valor_texto": respuesta.valor_texto,
                "valor_numero": (
                    float(respuesta.valor_numero)
                    if respuesta.valor_numero is not None
                    else None
                ),
                "valor_json": respuesta.valor_json,
                "idioma_sesion": respuesta.sesion.idioma,
            },
        )
    return registros


def _obtener_registros_catalogos(parametros: dict[str, Any]) -> list[dict[str, Any]]:
    """Obtiene registros planos de catalogos e items."""
    codigo_catalogo = parametros.get("catalogo_codigo")
    consulta_catalogos = Catalogo.objects.filter(
        esta_activo=True,
        esta_eliminado=False,
    )
    if codigo_catalogo:
        consulta_catalogos = consulta_catalogos.filter(codigo=codigo_catalogo)

    registros: list[dict[str, Any]] = []
    for catalogo in consulta_catalogos.iterator():
        items = ItemCatalogo.objects.filter(
            catalogo=catalogo,
            esta_activo=True,
            esta_eliminado=False,
        ).select_related("item_padre")
        for item in items.iterator():
            registros.append(
                {
                    "catalogo_codigo": catalogo.codigo,
                    "catalogo_nombre": catalogo.nombre,
                    "item_codigo": item.codigo,
                    "item_nombre": item.nombre,
                    "item_descripcion": item.descripcion,
                    "item_valor": item.valor,
                    "codigo_padre": (
                        item.item_padre.codigo if item.item_padre_id else None
                    ),
                    "metadatos": item.metadatos,
                },
            )
    return registros


def _obtener_registros_analitica(parametros: dict[str, Any]) -> list[dict[str, Any]]:
    """Obtiene registros de analitica segun filtros."""
    return listar_respuestas_analiticas(
        formulario_codigo=parametros.get("formulario_codigo"),
        fecha_inicio=parametros.get("fecha_inicio"),
        fecha_fin=parametros.get("fecha_fin"),
        estado_sesion=parametros.get("estado_sesion"),
    )


def _crear_registro_exportacion(
    tipo: str,
    formato: str,
    parametros: dict[str, Any],
    usuario: str = "",
) -> Exportacion:
    """Crea un registro de exportacion en estado pendiente."""
    return Exportacion.objects.create(
        tipo=tipo,
        formato=formato,
        estado=EstadoExportacion.PENDIENTE,
        usuario=usuario,
        parametros=parametros,
    )


def _ejecutar_exportacion(
    exportacion: Exportacion,
    registros: list[dict[str, Any]],
) -> Exportacion:
    """Ejecuta la generacion de archivo y actualiza el registro de exportacion."""
    exportacion.estado = EstadoExportacion.PROCESANDO
    exportacion.fecha_inicio = timezone.now()
    exportacion.save(update_fields=["estado", "fecha_inicio", "fecha_modificacion"])

    try:
        generador = obtener_generador_exportacion(exportacion.formato)
        contenido = generador.generar(registros, exportacion.parametros or {})
        extension = EXTENSION_POR_FORMATO[exportacion.formato]
        mime_type = MIME_POR_FORMATO[exportacion.formato]
        nombre_archivo = f"exportacion_{exportacion.tipo}_{exportacion.uuid}.{extension}"

        archivo = guardar_archivo(
            contenido=contenido,
            nombre_original=nombre_archivo,
            mime_type=mime_type,
            tipo_archivo=TipoArchivo.DOCUMENTO,
            origen=OrigenArchivo.OTRO,
            metadatos={
                "tipo_exportacion": exportacion.tipo,
                "formato": exportacion.formato,
            },
        )

        exportacion.estado = EstadoExportacion.FINALIZADA
        exportacion.fecha_fin = timezone.now()
        exportacion.archivo = archivo
        exportacion.registros_exportados = len(registros)
        exportacion.error = ""
        exportacion.save(
            update_fields=[
                "estado",
                "fecha_fin",
                "archivo",
                "registros_exportados",
                "error",
                "fecha_modificacion",
            ],
        )
        registrar_auditoria(
            entidad=Exportacion.__name__,
            entidad_id=str(exportacion.pk),
            accion=AccionAuditoria.EXPORTAR,
            valor_nuevo=crear_snapshot_modelo(exportacion),
        )
    except FormatoExportacionNoSoportadoError as error:
        exportacion.estado = EstadoExportacion.FALLIDA
        exportacion.fecha_fin = timezone.now()
        exportacion.error = error.mensaje
        exportacion.save(
            update_fields=["estado", "fecha_fin", "error", "fecha_modificacion"],
        )
    except Exception as error:  # noqa: BLE001 - captura controlada para marcar exportacion fallida
        exportacion.estado = EstadoExportacion.FALLIDA
        exportacion.fecha_fin = timezone.now()
        exportacion.error = "No fue posible completar la exportación solicitada."
        exportacion.save(
            update_fields=["estado", "fecha_fin", "error", "fecha_modificacion"],
        )

    return exportacion


def exportar_respuestas(
    formato: str,
    parametros: dict[str, Any] | None = None,
    usuario: str = "",
) -> Exportacion:
    """Exporta respuestas de formularios segun filtros."""
    parametros_exportacion = parametros or {}
    with transaction.atomic():
        exportacion = _crear_registro_exportacion(
            TipoExportacion.RESPUESTAS,
            formato,
            parametros_exportacion,
            usuario,
        )
    registros = _obtener_registros_respuestas(parametros_exportacion)
    return _ejecutar_exportacion(exportacion, registros)


def exportar_catalogos(
    formato: str,
    parametros: dict[str, Any] | None = None,
    usuario: str = "",
) -> Exportacion:
    """Exporta catalogos parametrizables e items."""
    parametros_exportacion = parametros or {}
    with transaction.atomic():
        exportacion = _crear_registro_exportacion(
            TipoExportacion.CATALOGOS,
            formato,
            parametros_exportacion,
            usuario,
        )
    registros = _obtener_registros_catalogos(parametros_exportacion)
    return _ejecutar_exportacion(exportacion, registros)


def exportar_analitica(
    formato: str,
    parametros: dict[str, Any] | None = None,
    usuario: str = "",
) -> Exportacion:
    """Exporta datos analiticos normalizados."""
    parametros_exportacion = parametros or {}
    with transaction.atomic():
        exportacion = _crear_registro_exportacion(
            TipoExportacion.ANALITICA,
            formato,
            parametros_exportacion,
            usuario,
        )
    registros = _obtener_registros_analitica(parametros_exportacion)
    return _ejecutar_exportacion(exportacion, registros)


def obtener_exportacion(uuid_exportacion: UUID) -> Exportacion:
    """Retorna una exportacion por UUID o lanza error funcional."""
    exportacion = obtener_exportacion_por_uuid(uuid_exportacion)
    if exportacion is None:
        raise ExportacionNoEncontradaError()
    return exportacion


def generar_contenido_respuestas(
    formato: str,
    parametros: dict[str, Any] | None = None,
) -> tuple[bytes, str, str]:
    """Genera el contenido de respuestas para descarga directa sin persistir."""
    parametros_exportacion = parametros or {}
    registros = _obtener_registros_respuestas(parametros_exportacion)
    generador = obtener_generador_exportacion(formato)
    contenido = generador.generar(registros, parametros_exportacion)
    return contenido, MIME_POR_FORMATO[formato], EXTENSION_POR_FORMATO[formato]
