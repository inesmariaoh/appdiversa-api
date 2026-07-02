"""
Utilidades de prueba para sincronizacion offline.
"""

import uuid

from aplicaciones.formularios.models import (
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)
from aplicaciones.respuestas.models import Respuesta
from aplicaciones.sesiones_anonimas.models import EstadoSesionAnonima, SesionAnonima
from aplicaciones.sesiones_anonimas.seguridad import generar_token_cliente_seguro
from aplicaciones.sincronizacion.validadores import calcular_checksum_operacion


def crear_contexto_sincronizacion(
    codigo_pregunta: str = "P_SYNC",
) -> tuple[SesionAnonima, str, str, Pregunta]:
    """Crea sesion, token y pregunta para pruebas de sincronizacion."""
    formulario = Formulario.objects.create(
        codigo=f"form_sync_{uuid.uuid4().hex[:8]}",
        nombre="Formulario sync",
        tipo_formulario=TipoFormulario.ENCUESTA,
        estado=EstadoFormulario.PUBLICADO,
    )
    version = FormularioVersion.objects.create(
        formulario=formulario,
        numero_version=1,
        estado=EstadoFormulario.PUBLICADO,
        es_publicada=True,
    )
    uuid_sesion = uuid.uuid4()
    token = generar_token_cliente_seguro()
    sesion = SesionAnonima.objects.create(
        uuid_sesion=uuid_sesion,
        formulario=formulario,
        version_formulario=version,
        token_cliente=token,
        estado=EstadoSesionAnonima.INICIADA,
    )
    seccion = SeccionFormulario.objects.create(
        formulario_version=version,
        codigo="sec_sync",
        titulo="Seccion sync",
        orden=1,
    )
    pregunta = Pregunta.objects.create(
        seccion=seccion,
        codigo=codigo_pregunta,
        texto="Pregunta sync",
        tipo_pregunta=TipoPregunta.NUMERO,
        orden=1,
    )
    return sesion, str(uuid_sesion), token, pregunta


def construir_operacion(
    uuid_local: uuid.UUID,
    codigo_pregunta: str,
    valor: object,
    version_cliente: int,
    fecha_cliente: str = "2026-06-28T10:00:00+00:00",
    incluir_checksum: bool = True,
) -> dict[str, object]:
    """Construye una operacion de sincronizacion para pruebas."""
    checksum = ""
    if incluir_checksum:
        checksum = calcular_checksum_operacion(
            codigo_pregunta,
            valor,
            version_cliente,
        )
    return {
        "uuid_local": str(uuid_local),
        "codigo_pregunta": codigo_pregunta,
        "valor": valor,
        "version_cliente": version_cliente,
        "fecha_cliente": fecha_cliente,
        "checksum": checksum,
    }


def construir_payload_batch(
    uuid_sesion: str,
    token: str,
    operaciones: list[dict[str, object]],
    dispositivo: str = "web-indexeddb",
) -> dict[str, object]:
    """Construye el payload completo del endpoint de sincronizacion."""
    return {
        "uuid_sesion": uuid_sesion,
        "token_cliente": token,
        "dispositivo": dispositivo,
        "version_app": "1.0.0",
        "operaciones": operaciones,
    }


def crear_pregunta_adicional(
    sesion: SesionAnonima,
    codigo: str,
    orden: int = 2,
) -> Pregunta:
    """Crea una pregunta adicional en la version de la sesion."""
    seccion = sesion.version_formulario.secciones.first()
    if seccion is None:
        raise ValueError("La sesion no tiene secciones.")
    return Pregunta.objects.create(
        seccion=seccion,
        codigo=codigo,
        texto=f"Pregunta {codigo}",
        tipo_pregunta=TipoPregunta.NUMERO,
        orden=orden,
    )


def crear_respuesta_con_uuid_local(
    sesion: SesionAnonima,
    pregunta: Pregunta,
    uuid_local: uuid.UUID,
    version_cliente: int,
    valor_numero: int,
) -> Respuesta:
    """Crea una respuesta con campos de sincronizacion para pruebas."""
    return Respuesta.objects.create(
        sesion=sesion,
        pregunta=pregunta,
        valor_numero=valor_numero,
        uuid_local=uuid_local,
        version_cliente=version_cliente,
        fecha_modificacion_cliente="2026-06-28T09:00:00+00:00",
        dispositivo_origen="test-device",
    )
