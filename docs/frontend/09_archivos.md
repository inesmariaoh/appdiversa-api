# 09 — Archivos (repositorio documental)

API bajo `/api/v1/archivos/`. Validaciones de MIME, extensión, tamaño y checksum en el servidor.

## Subida

```http
POST /api/v1/archivos/
Content-Type: multipart/form-data
X-Sesion-Anonima: {uuid_sesion}
X-Token-Sesion: {token_cliente}
```

| Campo | Tipo | Requerido | Valores |
|-------|------|-----------|---------|
| `archivo` | file | sí | Binario |
| `tipo_archivo` | string | sí | Ver tabla abajo |
| `origen` | string | sí | `formulario`, `pregunta`, `respuesta`, `internacionalizacion`, `configuracion`, `catalogo`, `notificacion`, `otro` |
| `descripcion` | string | no | |
| `es_publico` | boolean | no | default `false` |
| `metadatos` | JSON | no | |
| `usuario_keycloak` | string | no | Futuro |
| `uuid_sesion` | UUID | no | Contexto sesión |
| `token_cliente` | string | no | Alternativa a header |

Alternativa: header `X-API-INTERNA` en lugar de sesión (operaciones administrativas).

**Respuesta 201**: `ArchivoRepositorio` (metadatos + `url` de descarga).

**Errores 400** (mensajes funcionales):

- Extensión no permitida
- MIME no permitido
- Tamaño supera máximo
- Nombre no válido
- Checksum inválido

## Tipos de archivo (`tipo_archivo`)

| Valor | MIME permitidos (resumen) | Tamaño máximo |
|-------|---------------------------|---------------|
| `imagen` | jpeg, png, webp, gif, svg | 10 MB |
| `documento` | pdf, doc, docx, xlsx, csv, txt, json | 25 MB |
| `audio` | mpeg, wav, ogg, mp4 | 50 MB |
| `video` | mp4, webm, quicktime | 100 MB |
| `firma` | png, jpeg, svg | 5 MB |
| `multimedia` | imagen + audio + video selectos | 100 MB |
| `archivo_general` | pdf, txt, jpeg, png | 25 MB |

**Extensiones prohibidas**: `exe`, `dll`, `bat`, `cmd`, `ps1`, `sh`, `jar`, `msi`, `apk`, `ipa`, `scr`, `com`.

## Metadatos

```http
GET /api/v1/archivos/{uuid_archivo}/
```

| Credencial | Condición |
|------------|-----------|
| Sin header | Solo si `es_publico=true` |
| `X-API-INTERNA` | Archivos privados |

**Respuesta 200**: `ArchivoRepositorio`.

## Descarga

```http
GET /api/v1/archivos/{uuid_archivo}/descargar/
```

- **Público**: binario directo (`Content-Type` del archivo).
- **Privado**: requiere `X-API-INTERNA`.

El campo `url` en metadatos apunta a la ruta de descarga.

## Eliminación

```http
DELETE /api/v1/archivos/{uuid_archivo}/
X-API-INTERNA: {token}
```

Soft delete. **No disponible para el frontend MVP** (solo API interna).

## Estados (`estado`)

`activo`, `eliminado`, `cuarentena`, `procesando`.

## Uso en preguntas tipo archivo / firma / audio / video

1. Subir archivo con `origen=respuesta` y sesión válida.
2. Guardar referencia en respuesta (nombre/ruta según tipo de pregunta) vía `POST /respuestas/`.

## Archivos públicos vs privados

| `es_publico` | GET metadatos | GET descargar |
|--------------|---------------|---------------|
| `true` | Sin auth | Sin auth |
| `false` | `X-API-INTERNA` | `X-API-INTERNA` |

Logos e imágenes de interfaz suelen ser públicos (`es_publico=true`).

## Documentos relacionados

- [04_endpoints_protegidos.md](./04_endpoints_protegidos.md)
- [05_modelos_json.md](./05_modelos_json.md)
