"""
Servicio de importacion del catalogo DIVIPOLA (departamentos y municipios).

Carga datos desde la API Socrata de Datos Abiertos Colombia o desde archivo local.
"""

from __future__ import annotations

import csv
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from django.db import transaction

from aplicaciones.catalogos.constantes import DivipolaConstantes, TiposCatalogo
from aplicaciones.catalogos.models import Catalogo, ItemCatalogo

logger = logging.getLogger(__name__)

TIMEOUT_DESCARGA_SEGUNDOS = 120
CLAVES_CODIGO_DEPARTAMENTO = (
    "codigo_departamento",
    "cod_dpto",
    "codigo_dpto",
)
CLAVES_NOMBRE_DEPARTAMENTO = (
    "nombre_departamento",
    "nom_departamento",
    "dpto",
    "nombre_dpto",
)
CLAVES_CODIGO_MUNICIPIO = (
    "codigo_municipio",
    "cod_mpio",
    "codigo_mpio",
)
CLAVES_NOMBRE_MUNICIPIO = (
    "nombre_municipio",
    "nom_mpio",
    "nombre_mpio",
    "mpio",
)


@dataclass(frozen=True)
class FilaDivipola:
    """Representa una fila normalizada del dataset DIVIPOLA."""

    codigo_departamento: str
    nombre_departamento: str
    codigo_municipio: str
    nombre_municipio: str


@dataclass
class ResumenImportacionDivipola:
    """Resumen de la ejecucion de importacion DIVIPOLA."""

    departamentos_creados: int = 0
    departamentos_actualizados: int = 0
    municipios_creados: int = 0
    municipios_actualizados: int = 0
    errores: list[str] = field(default_factory=list)


def _obtener_valor_fila(fila: dict[str, Any], claves: tuple[str, ...]) -> str:
    """Obtiene el primer valor no vacio de la fila segun las claves candidatas."""
    for clave in claves:
        valor = fila.get(clave)
        if valor is not None and str(valor).strip():
            return str(valor).strip()
    return ""


def normalizar_fila_divipola(fila: dict[str, Any]) -> FilaDivipola | None:
    """Normaliza una fila del dataset DIVIPOLA o retorna None si es invalida."""
    codigo_departamento = _obtener_valor_fila(fila, CLAVES_CODIGO_DEPARTAMENTO)
    nombre_departamento = _obtener_valor_fila(fila, CLAVES_NOMBRE_DEPARTAMENTO)
    codigo_municipio = _obtener_valor_fila(fila, CLAVES_CODIGO_MUNICIPIO)
    nombre_municipio = _obtener_valor_fila(fila, CLAVES_NOMBRE_MUNICIPIO)

    if not all(
        (
            codigo_departamento,
            nombre_departamento,
            codigo_municipio,
            nombre_municipio,
        ),
    ):
        return None

    return FilaDivipola(
        codigo_departamento=codigo_departamento,
        nombre_departamento=nombre_departamento,
        codigo_municipio=codigo_municipio,
        nombre_municipio=nombre_municipio,
    )


def _construir_metadatos_departamento() -> dict[str, str]:
    """Retorna metadatos estandar para un item de departamento DIVIPOLA."""
    return {
        "fuente": DivipolaConstantes.FUENTE,
        "recurso": DivipolaConstantes.RECURSO_SOCRATA,
    }


def _construir_metadatos_municipio(fila: FilaDivipola) -> dict[str, str]:
    """Retorna metadatos estandar para un item de municipio DIVIPOLA."""
    return {
        "fuente": DivipolaConstantes.FUENTE,
        "recurso": DivipolaConstantes.RECURSO_SOCRATA,
        "codigo_departamento": fila.codigo_departamento,
        "nombre_departamento": fila.nombre_departamento,
    }


def _descargar_json_api(
    url: str,
    apertura_url: Callable[..., Any] = urllib.request.urlopen,
) -> list[dict[str, Any]]:
    """Descarga registros DIVIPOLA desde la API Socrata."""
    solicitud = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "AppDiversa-API/1.0"},
    )
    with apertura_url(solicitud, timeout=TIMEOUT_DESCARGA_SEGUNDOS) as respuesta:
        datos = json.load(respuesta)

    if not isinstance(datos, list):
        raise ValueError("La respuesta de la API DIVIPOLA no es una lista JSON.")

    return datos


def obtener_url_api_divipola(limite: int = DivipolaConstantes.LIMITE_API) -> str:
    """Construye la URL de consulta Socrata para el recurso DIVIPOLA."""
    parametros = urllib.parse.urlencode({"$limit": limite})
    return f"{DivipolaConstantes.URL_API}?{parametros}"


def cargar_datos_desde_api(
    apertura_url: Callable[..., Any] | None = None,
) -> list[dict[str, Any]]:
    """Carga filas DIVIPOLA desde el endpoint oficial de Datos Abiertos Colombia."""
    url = obtener_url_api_divipola()
    apertura = apertura_url or urllib.request.urlopen
    try:
        return _descargar_json_api(url, apertura_url=apertura)
    except urllib.error.URLError as error:
        logger.exception("Fallo la descarga DIVIPOLA desde la API.")
        raise ConnectionError(
            "No fue posible consultar la API DIVIPOLA. "
            "Use la opcion --archivo para importar desde un archivo local.",
        ) from error


def _leer_json_local(ruta: Path) -> list[dict[str, Any]]:
    """Lee un archivo JSON local con filas DIVIPOLA."""
    contenido = ruta.read_text(encoding="utf-8")
    datos = json.loads(contenido)
    if not isinstance(datos, list):
        raise ValueError("El archivo JSON debe contener una lista de registros.")
    return datos


def _leer_csv_local(ruta: Path) -> list[dict[str, Any]]:
    """Lee un archivo CSV local con filas DIVIPOLA."""
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        return [dict(fila) for fila in lector]


def cargar_datos_desde_archivo(ruta_archivo: str | Path) -> list[dict[str, Any]]:
    """Carga filas DIVIPOLA desde un archivo JSON o CSV local."""
    ruta = Path(ruta_archivo)
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontro el archivo: {ruta}")

    extension = ruta.suffix.lower()
    if extension == ".json":
        return _leer_json_local(ruta)
    if extension == ".csv":
        return _leer_csv_local(ruta)

    raise ValueError(
        "Formato de archivo no soportado. Use un archivo .json o .csv.",
    )


def _asegurar_catalogo(
    codigo: str,
    nombre: str,
) -> Catalogo:
    """Crea o actualiza un catalogo jerarquico de sistema para DIVIPOLA."""
    catalogo = Catalogo.todos.filter(codigo=codigo).first()
    valores = {
        "nombre": nombre,
        "tipo_catalogo": TiposCatalogo.JERARQUICO,
        "esta_activo": True,
        "es_sistema": True,
        "esta_eliminado": False,
    }

    if catalogo is None:
        catalogo = Catalogo.objects.create(codigo=codigo, **valores)
        return catalogo

    campos_actualizables = (
        "nombre",
        "tipo_catalogo",
        "esta_activo",
        "es_sistema",
        "esta_eliminado",
    )
    if any(getattr(catalogo, campo) != valores[campo] for campo in campos_actualizables):
        for campo in campos_actualizables:
            setattr(catalogo, campo, valores[campo])
        catalogo.save(update_fields=list(campos_actualizables) + ["fecha_modificacion"])

    return catalogo


def _guardar_o_actualizar_item(
    catalogo: Catalogo,
    codigo: str,
    nombre: str,
    valor: str,
    codigo_externo: str,
    metadatos: dict[str, str],
    item_padre: ItemCatalogo | None,
    resumen: ResumenImportacionDivipola,
    es_departamento: bool,
) -> ItemCatalogo:
    """Crea o actualiza un item de catalogo y actualiza el resumen."""
    item = ItemCatalogo.todos.filter(catalogo=catalogo, codigo=codigo).first()
    valores = {
        "nombre": nombre,
        "valor": valor,
        "codigo_externo": codigo_externo,
        "metadatos": metadatos,
        "item_padre": item_padre,
        "esta_activo": True,
        "esta_eliminado": False,
    }

    if item is None:
        item = ItemCatalogo.objects.create(catalogo=catalogo, codigo=codigo, **valores)
        if es_departamento:
            resumen.departamentos_creados += 1
        else:
            resumen.municipios_creados += 1
        return item

    campos_actualizables = (
        "nombre",
        "valor",
        "codigo_externo",
        "metadatos",
        "item_padre",
        "esta_activo",
        "esta_eliminado",
    )
    hubo_cambios = any(getattr(item, campo) != valores[campo] for campo in campos_actualizables)
    if hubo_cambios:
        for campo in campos_actualizables:
            setattr(item, campo, valores[campo])
        item.save(update_fields=list(campos_actualizables) + ["fecha_modificacion"])
        if es_departamento:
            resumen.departamentos_actualizados += 1
        else:
            resumen.municipios_actualizados += 1

    return item


def _procesar_departamentos_unicos(
    filas: list[FilaDivipola],
    catalogo_departamentos: Catalogo,
    resumen: ResumenImportacionDivipola,
) -> dict[str, ItemCatalogo]:
    """Procesa departamentos unicos y retorna mapa codigo -> item."""
    departamentos: dict[str, FilaDivipola] = {}
    for fila in filas:
        departamentos.setdefault(fila.codigo_departamento, fila)

    mapa_items: dict[str, ItemCatalogo] = {}
    for codigo, fila in departamentos.items():
        item = _guardar_o_actualizar_item(
            catalogo=catalogo_departamentos,
            codigo=codigo,
            nombre=fila.nombre_departamento,
            valor=codigo,
            codigo_externo=codigo,
            metadatos=_construir_metadatos_departamento(),
            item_padre=None,
            resumen=resumen,
            es_departamento=True,
        )
        mapa_items[codigo] = item

    return mapa_items


def _procesar_municipios(
    filas: list[FilaDivipola],
    catalogo_municipios: Catalogo,
    mapa_departamentos: dict[str, ItemCatalogo],
    resumen: ResumenImportacionDivipola,
) -> None:
    """Procesa municipios y los relaciona con su departamento padre."""
    for fila in filas:
        departamento = mapa_departamentos.get(fila.codigo_departamento)
        if departamento is None:
            resumen.errores.append(
                f"Municipio {fila.codigo_municipio}: departamento "
                f"{fila.codigo_departamento} no encontrado.",
            )
            continue

        _guardar_o_actualizar_item(
            catalogo=catalogo_municipios,
            codigo=fila.codigo_municipio,
            nombre=fila.nombre_municipio,
            valor=fila.codigo_municipio,
            codigo_externo=fila.codigo_municipio,
            metadatos=_construir_metadatos_municipio(fila),
            item_padre=departamento,
            resumen=resumen,
            es_departamento=False,
        )


def importar_divipola(
    filas_raw: list[dict[str, Any]],
    dry_run: bool = False,
) -> ResumenImportacionDivipola:
    """Importa departamentos y municipios DIVIPOLA en catalogos parametrizables."""
    resumen = ResumenImportacionDivipola()
    filas_validas: list[FilaDivipola] = []

    for indice, fila_raw in enumerate(filas_raw, start=1):
        fila = normalizar_fila_divipola(fila_raw)
        if fila is None:
            resumen.errores.append(f"Fila {indice}: datos incompletos o invalidos.")
            continue
        filas_validas.append(fila)

    with transaction.atomic():
        catalogo_departamentos = _asegurar_catalogo(
            DivipolaConstantes.CODIGO_CATALOGO_DEPARTAMENTOS,
            DivipolaConstantes.NOMBRE_CATALOGO_DEPARTAMENTOS,
        )
        catalogo_municipios = _asegurar_catalogo(
            DivipolaConstantes.CODIGO_CATALOGO_MUNICIPIOS,
            DivipolaConstantes.NOMBRE_CATALOGO_MUNICIPIOS,
        )
        mapa_departamentos = _procesar_departamentos_unicos(
            filas_validas,
            catalogo_departamentos,
            resumen,
        )
        _procesar_municipios(
            filas_validas,
            catalogo_municipios,
            mapa_departamentos,
            resumen,
        )

        if dry_run:
            transaction.set_rollback(True)

    return resumen
