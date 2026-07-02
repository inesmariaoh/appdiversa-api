"""
Constantes reutilizables para respuestas de ubicacion geografica compuesta.
"""

CLAVE_DEPARTAMENTO_CODIGO = "departamento_codigo"
CLAVE_DEPARTAMENTO_NOMBRE = "departamento_nombre"
CLAVE_MUNICIPIO_CODIGO = "municipio_codigo"
CLAVE_MUNICIPIO_NOMBRE = "municipio_nombre"

CLAVES_UBICACION_GEOGRAFICA = frozenset(
    {
        CLAVE_DEPARTAMENTO_CODIGO,
        CLAVE_DEPARTAMENTO_NOMBRE,
        CLAVE_MUNICIPIO_CODIGO,
        CLAVE_MUNICIPIO_NOMBRE,
    },
)
