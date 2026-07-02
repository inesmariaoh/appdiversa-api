# 12 — Swagger y OpenAPI

Documentación interactiva disponible en **modo DEBUG** (`DJANGO_DEBUG=True`).

## URLs de documentación

| URL | Descripción |
|-----|-------------|
| `/api/schema/` | Esquema OpenAPI 3 (JSON) |
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |

Base API: `http://localhost:8000` (desarrollo Docker).

## Export estático

El proyecto incluye exportación para el frontend:

```bash
python manage.py spectacular --file docs/frontend/openapi_export.json
```

Archivo generado: [openapi_export.json](./openapi_export.json)

## Cómo probar endpoints

### Swagger UI

1. Abrir `http://localhost:8000/api/docs/`.
2. Expandir endpoint.
3. **Authorize** no aplica JWT; usar headers manualmente en “Try it out”:
   - `X-Sesion-Anonima`
   - `X-Token-Sesion`
   - `X-API-INTERNA`

### Flujo típico en Swagger

1. `POST /api/v1/sesiones/` → copiar `token_cliente`.
2. En endpoints protegidos, agregar parámetros de header documentados.
3. `POST /api/v1/respuestas/` con body + headers.

## Headers documentados en OpenAPI

Parámetros reutilizables (`PARAMETROS_SESION_ANONIMA`, `PARAMETROS_API_INTERNA`):

| Parámetro | Header |
|-----------|--------|
| Sesión | `X-Sesion-Anonima` |
| Token sesión | `X-Token-Sesion` |
| API interna | `X-API-INTERNA` |

## Importar OpenAPI en herramientas

### Cliente TypeScript (openapi-generator, orval, etc.)

```bash
# Ejemplo con archivo local
openapi-generator-cli generate \
  -i docs/frontend/openapi_export.json \
  -g typescript-axios \
  -o src/api/generated
```

### Postman / Insomnia

Importar `openapi_export.json` como colección.

### Validación de contrato en CI

Comparar export con snapshot en PR del frontend.

## Limitaciones conocidas del esquema

`drf-spectacular` puede omitir vistas sin serializer explícito en:

- `ValidarFinalizacionView`
- `FinalizarFormularioView`
- `EvaluarReglasSesionView`
- `EvaluarReglasPreguntaView`

Los contratos completos están en:

- [05_modelos_json.md](./05_modelos_json.md)
- [04_endpoints_protegidos.md](./04_endpoints_protegidos.md)

## Configuración spectacular

```python
SPECTACULAR_SETTINGS = {
    "TITLE": "AppDiversa API",
    "DESCRIPTION": "API REST del motor de formularios parametrizables AppDiversa 2.0",
    "VERSION": "v1",
}
```

## Documentos relacionados

- [03_endpoints_publicos.md](./03_endpoints_publicos.md)
- [04_endpoints_protegidos.md](./04_endpoints_protegidos.md)
