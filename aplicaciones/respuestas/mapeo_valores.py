"""
Mapeo de valores de entrada a campos del modelo Respuesta.
"""

from collections.abc import Callable
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from typing import Any

from aplicaciones.formularios.models import TipoPregunta
from aplicaciones.respuestas.excepciones import ValorInvalidoError
from aplicaciones.respuestas.models import Respuesta

TIPOS_VALOR_TEXTO = frozenset(
    {
        TipoPregunta.TEXTO_CORTO,
        TipoPregunta.TEXTO_LARGO,
        TipoPregunta.RADIO,
        TipoPregunta.SELECT,
        TipoPregunta.AUTOCOMPLETE,
        TipoPregunta.ARCHIVO,
        TipoPregunta.FIRMA,
        TipoPregunta.AUDIO,
        TipoPregunta.VIDEO,
    },
)

TIPOS_VALOR_JSON = frozenset(
    {
        TipoPregunta.CHECKBOX,
        TipoPregunta.SELECT_MULTIPLE,
        TipoPregunta.MATRIZ,
        TipoPregunta.LIKERT,
        TipoPregunta.UBICACION_GEOGRAFICA,
    },
)

CLAVES_GEOLOCALIZACION = frozenset({"latitud", "longitud", "precision_metros"})


def _limpiar_campos_valor(respuesta: Respuesta) -> None:
    """Limpia los campos de valor antes de asignar un nuevo contenido."""
    respuesta.valor_texto = ""
    respuesta.valor_numero = None
    respuesta.valor_booleano = None
    respuesta.valor_fecha = None
    respuesta.valor_hora = None
    respuesta.valor_fecha_hora = None
    respuesta.valor_json = None
    respuesta.archivo_nombre = ""
    respuesta.archivo_ruta = ""
    respuesta.latitud = None
    respuesta.longitud = None
    respuesta.precision_metros = None


def _asignar_valor_texto(respuesta: Respuesta, valor: Any) -> None:
    respuesta.valor_texto = str(valor)


def _asignar_valor_numero(respuesta: Respuesta, valor: Any) -> None:
    try:
        respuesta.valor_numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValorInvalidoError() from error


def _parsear_componentes_fecha(valor: Any) -> date | None:
    """Interpreta una fecha desde cadena ISO o componentes anio/mes/dia."""
    if isinstance(valor, date):
        return valor
    if isinstance(valor, dict):
        anio = valor.get("anio")
        mes = valor.get("mes")
        dia = valor.get("dia")
        if anio and mes and dia:
            return date(int(anio), int(mes), int(dia))
        return None
    if isinstance(valor, str):
        partes = valor.split("T")[0]
        partes_fecha = partes.split("-")
        if len(partes_fecha) == 3:
            return date(
                int(partes_fecha[0]),
                int(partes_fecha[1]),
                int(partes_fecha[2]),
            )
    return None


def _asignar_valor_fecha(respuesta: Respuesta, valor: Any) -> None:
    fecha = _parsear_componentes_fecha(valor)
    if fecha is None:
        raise ValorInvalidoError()
    respuesta.valor_fecha = fecha


def _asignar_valor_hora(respuesta: Respuesta, valor: Any) -> None:
    if isinstance(valor, time):
        respuesta.valor_hora = valor
        return
    if isinstance(valor, str):
        partes = valor.split(":")
        if len(partes) >= 2:
            respuesta.valor_hora = time(
                int(partes[0]),
                int(partes[1]),
                int(partes[2]) if len(partes) > 2 else 0,
            )
            return
    raise ValorInvalidoError()


def _asignar_valor_fecha_hora(respuesta: Respuesta, valor: Any) -> None:
    if isinstance(valor, datetime):
        respuesta.valor_fecha_hora = valor
        return
    if isinstance(valor, str):
        valor_normalizado = valor.replace("Z", "+00:00")
        try:
            respuesta.valor_fecha_hora = datetime.fromisoformat(valor_normalizado)
            return
        except ValueError as error:
            raise ValorInvalidoError() from error
    raise ValorInvalidoError()


def _asignar_valor_json(respuesta: Respuesta, valor: Any) -> None:
    if isinstance(valor, (dict, list)):
        respuesta.valor_json = valor
        return
    raise ValorInvalidoError()


def _asignar_geolocalizacion(respuesta: Respuesta, valor: Any) -> None:
    if not isinstance(valor, dict):
        raise ValorInvalidoError()

    latitud = valor.get("latitud")
    longitud = valor.get("longitud")
    precision = valor.get("precision_metros")

    if latitud is None or longitud is None:
        raise ValorInvalidoError()

    try:
        respuesta.latitud = Decimal(str(latitud))
        respuesta.longitud = Decimal(str(longitud))
        if precision is not None:
            respuesta.precision_metros = Decimal(str(precision))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValorInvalidoError() from error

    datos_adicionales = {
        clave: valor[clave]
        for clave in valor
        if clave not in CLAVES_GEOLOCALIZACION
    }
    if datos_adicionales:
        respuesta.valor_json = datos_adicionales


def _asignar_valor_booleano(respuesta: Respuesta, valor: Any) -> None:
    respuesta.valor_booleano = valor


ESTRATEGIAS_POR_TIPO: dict[str, Callable[[Respuesta, Any], None]] = {
    TipoPregunta.NUMERO: _asignar_valor_numero,
    TipoPregunta.FECHA: _asignar_valor_fecha,
    TipoPregunta.HORA: _asignar_valor_hora,
    TipoPregunta.FECHA_HORA: _asignar_valor_fecha_hora,
    TipoPregunta.GEOLOCALIZACION: _asignar_geolocalizacion,
}


def asignar_valor_a_respuesta(
    respuesta: Respuesta,
    tipo_pregunta: str,
    valor: Any,
) -> None:
    """Asigna el valor recibido al campo correspondiente segun el tipo de pregunta."""
    _limpiar_campos_valor(respuesta)

    if isinstance(valor, bool):
        _asignar_valor_booleano(respuesta, valor)
        return

    if tipo_pregunta in TIPOS_VALOR_TEXTO:
        _asignar_valor_texto(respuesta, valor)
        return

    if tipo_pregunta in TIPOS_VALOR_JSON:
        _asignar_valor_json(respuesta, valor)
        return

    estrategia = ESTRATEGIAS_POR_TIPO.get(tipo_pregunta)
    if estrategia is not None:
        estrategia(respuesta, valor)
        return

    raise ValorInvalidoError()
