"""
Vistas de la aplicacion comun.
"""

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response


@extend_schema(
    summary="Verificar salud del servicio",
    description="Confirma que el servicio API responde correctamente.",
    responses=inline_serializer(
        name="SaludRespuesta",
        fields={"estado": serializers.CharField()},
    ),
)
@api_view(["GET"])
def verificar_salud(request: Request) -> Response:
    """Confirma que el servicio API responde correctamente."""
    return Response({"estado": "ok"})
