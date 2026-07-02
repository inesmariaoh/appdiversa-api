"""
Parametros OpenAPI reutilizables para documentacion de seguridad.
"""

from drf_spectacular.utils import OpenApiParameter

PARAMETRO_HEADER_SESION_ANONIMA = OpenApiParameter(
    name="X-Sesion-Anonima",
    type=str,
    location=OpenApiParameter.HEADER,
    required=False,
    description="UUID de la sesión anónima asociada a la operación.",
)

PARAMETRO_HEADER_TOKEN_SESION = OpenApiParameter(
    name="X-Token-Sesion",
    type=str,
    location=OpenApiParameter.HEADER,
    required=False,
    description="Token de sesión anónima emitido al crear la sesión.",
)

PARAMETRO_HEADER_API_INTERNA = OpenApiParameter(
    name="X-API-INTERNA",
    type=str,
    location=OpenApiParameter.HEADER,
    required=False,
    description="Token de acceso interno autorizado para la API.",
)

PARAMETROS_SESION_ANONIMA = [
    PARAMETRO_HEADER_SESION_ANONIMA,
    PARAMETRO_HEADER_TOKEN_SESION,
]

PARAMETROS_API_INTERNA = [PARAMETRO_HEADER_API_INTERNA]
