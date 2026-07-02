# 07 — Catálogos

Los catálogos son listas parametrizables (países, departamentos, municipios, sexo, estrato, etc.) consumidas por preguntas tipo `select`, `autocomplete`, `radio`, `checkbox`.

## Endpoints

| Método | URL | Uso |
|--------|-----|-----|
| GET | `/catalogos/` | Listar catálogos activos |
| GET | `/catalogos/{codigo}/items/` | Items con filtros |
| GET | `/catalogos/{codigo}/items/{codigo_item}/hijos/` | Hijos jerárquicos |

Todos **públicos** (sin autenticación).

## Parámetros de consulta (items)

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `codigo_padre` | string | — | Filtra hijos de un padre |
| `solo_activos` | boolean | `true` | Solo ítems activos |
| `busqueda` | string | — | Búsqueda por nombre/código |
| `limite` | int | — | Máximo de resultados (min 1) |
| `idioma` | string | — | Traducciones |
| `incluir_accesibilidad` | boolean | `false` | Contenido accesible |

## Catálogo asociado en pregunta

Cuando `usa_catalogo=true` en la estructura del formulario:

```json
{
  "usa_catalogo": true,
  "catalogo_asociado": {
    "codigo": "municipios",
    "nombre": "Municipios",
    "endpoint_items": "/api/v1/catalogos/municipios/items/"
  },
  "pregunta_padre_catalogo": {
    "codigo": "P_DEPARTAMENTO",
    "texto": "Departamento"
  },
  "permite_busqueda_catalogo": true,
  "limite_items_catalogo": 50
}
```

El frontend debe:

1. Resolver dependencias: cargar padre antes que hijo.
2. Usar `codigo_padre` al consultar hijos o items filtrados.
3. Para autocomplete: `busqueda` + `limite`.

## Jerarquías (dependencias)

Ejemplo país → departamento → municipio:

```http
GET /api/v1/catalogos/departamentos/items/?codigo_padre=CO
GET /api/v1/catalogos/municipios/items/05/hijos/?solo_activos=true
```

Flujo UI:

1. Usuario selecciona país → guardar código padre.
2. Cargar departamentos con `codigo_padre` del país.
3. Usuario selecciona departamento → cargar municipios hijos.

## Autocomplete

Para preguntas `autocomplete` con `permite_busqueda_catalogo=true`:

```http
GET /api/v1/catalogos/ocupaciones/items/?busqueda=medico&limite=20&idioma=es
```

Mostrar `nombre` / `valor` al usuario; enviar `valor` o `codigo` según validación del tipo de pregunta (el backend valida contra catálogo al guardar respuesta).

## Validación en guardado

Al `POST /respuestas/`, el backend valida que el valor pertenezca al catálogo asociado a la pregunta. Error 400:

```json
{"detalle": "El valor enviado no pertenece al catálogo asociado a la pregunta."}
```

## Internacionalización

Combinar `idioma=es` en catálogos con `GET /internacionalizacion/traducciones/?entidad=ItemCatalogo&entidad_uuid=...` para textos alternativos.

## Ejemplo ítem

```json
{
  "codigo": "05001",
  "codigo_catalogo": "municipios",
  "nombre": "Medellín",
  "descripcion": "",
  "valor": "05001",
  "codigo_padre": "05",
  "codigo_externo": "DANE-05001",
  "metadatos": {"region": "metro"},
  "orden": 1,
  "esta_activo": true
}
```

## Documentos relacionados

- [03_endpoints_publicos.md](./03_endpoints_publicos.md)
- [05_modelos_json.md](./05_modelos_json.md)
