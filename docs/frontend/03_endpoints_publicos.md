# 03 — Endpoints públicos

Endpoints que **no requieren** `X-Sesion-Anonima`, `X-Token-Sesion` ni `X-API-INTERNA`.

Prefijo base: **`/api/v1/`**

Formato de error habitual: `{"detalle": "mensaje funcional"}`

---

## GET /salud/

| | |
|---|---|
| **Descripción** | Verificación de salud del servicio |
| **Headers** | Ninguno |
| **Query** | Ninguno |
| **Body** | Ninguno |

**Respuesta 200**

```json
{"estado": "ok"}
```

**Errores**: no documentados en código (fallo de infraestructura).

---

## GET /interfaz/configuracion/

| | |
|---|---|
| **Descripción** | Configuración pública de la interfaz (branding, textos, logos) |
| **Query** | `idioma` (opcional), `incluir_accesibilidad` (opcional, boolean, default `false`) |

**Respuesta 200**: ver [05_modelos_json.md](./05_modelos_json.md#configuracioninterfaz).

Si no hay configuración activa, el backend devuelve valores por defecto.

---

## GET /formularios/disponibles/

| | |
|---|---|
| **Descripción** | Lista formularios publicados disponibles para diligenciar |
| **Query** | `idioma` (opcional) |

**Respuesta 200**: array de `FormularioDisponible`.

**Ejemplo**

```json
[
  {
    "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "codigo": "encuesta_salud",
    "nombre": "Encuesta de salud",
    "descripcion": "Descripción breve",
    "tipo_formulario": "encuesta",
    "tiempo_estimado_minutos": 15,
    "fecha_inicio": "2026-01-01",
    "fecha_fin": "2026-12-31",
    "permite_anonimo": true,
    "permite_registro_final": false,
    "permite_multiples_respuestas": false,
    "permite_offline": true,
    "imagen_portada": "http://localhost:8000/media/..."
  }
]
```

---

## GET /formularios/{uuid_formulario}/estructura/

| | |
|---|---|
| **Descripción** | Estructura completa del formulario (versión publicada) |
| **Path** | `uuid_formulario` — UUID del formulario |
| **Query** | `idioma` (opcional) |

**Respuesta 200**: `FormularioEstructura` — ver [05_modelos_json.md](./05_modelos_json.md#formularioestructura).

**Respuesta 404**

```json
{"detalle": "El formulario solicitado no existe o no está disponible."}
```

---

## GET /catalogos/

| | |
|---|---|
| **Descripción** | Lista catálogos activos |
| **Query** | `idioma` (opcional) |

**Respuesta 200**: array de `Catalogo`.

---

## GET /catalogos/{codigo_catalogo}/items/

| | |
|---|---|
| **Descripción** | Items de un catálogo |
| **Query** | `codigo_padre`, `solo_activos` (default `true`), `busqueda`, `limite` (min 1), `idioma`, `incluir_accesibilidad` (default `false`) |

**Respuesta 200**: array de `ItemCatalogo`.

**Respuesta 404**: catálogo no encontrado.

---

## GET /catalogos/{codigo_catalogo}/items/{codigo_item}/hijos/

| | |
|---|---|
| **Descripción** | Hijos directos de un ítem (jerarquías país → departamento → municipio) |
| **Query** | `solo_activos` (default `true`), `idioma`, `incluir_accesibilidad` |

**Respuesta 200**: array de `ItemCatalogo`.

---

## GET /internacionalizacion/traducciones/

| | |
|---|---|
| **Descripción** | Traducciones y contenido accesible por entidad |
| **Query** | `idioma`, `entidad`, `entidad_uuid`, `campo` (todos opcionales) |

**Respuesta 200**: array de `TraduccionContenido`.

---

## POST /sesiones/

| | |
|---|---|
| **Descripción** | Crea o recupera sesión anónima; **emite `token_cliente`** |
| **Headers** | Ninguno requerido |
| **Permiso** | Público (`AllowAny`) |

**Body**

| Campo | Tipo | Requerido |
|-------|------|-----------|
| `uuid_sesion` | UUID | sí |
| `uuid_formulario` | UUID | sí |
| `token_cliente` | string | no (si vacío, el servidor genera uno) |
| `idioma` | string | no |
| `zona_horaria` | string | no |
| `es_offline` | boolean | no (default `false`) |

**Respuesta 201** (nueva) / **200** (existente)

```json
{
  "uuid_sesion": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "estado": "iniciada",
  "token_cliente": "xY9kL2mN..."
}
```

**Respuesta 404**

```json
{"detalle": "El formulario solicitado no existe o no está disponible."}
```

---

## Resumen de endpoints públicos

| Método | URL | Auth |
|--------|-----|------|
| GET | `/salud/` | No |
| GET | `/interfaz/configuracion/` | No |
| GET | `/formularios/disponibles/` | No |
| GET | `/formularios/{uuid}/estructura/` | No |
| GET | `/catalogos/` | No |
| GET | `/catalogos/{codigo}/items/` | No |
| GET | `/catalogos/{codigo}/items/{item}/hijos/` | No |
| GET | `/internacionalizacion/traducciones/` | No |
| POST | `/sesiones/` | No (devuelve token) |

## Documentos relacionados

- [04_endpoints_protegidos.md](./04_endpoints_protegidos.md)
- [05_modelos_json.md](./05_modelos_json.md)
