# 04 — Endpoints protegidos

Endpoints que requieren credenciales. El frontend MVP usa principalmente **sesión anónima**; **API interna** es para administración, BI y operaciones de backend.

## Headers de seguridad

| Header HTTP | Variable Django | Uso |
|-------------|-----------------|-----|
| `X-Sesion-Anonima` | `HTTP_X_SESION_ANONIMA` | UUID de la sesión |
| `X-Token-Sesion` | `HTTP_X_TOKEN_SESION` | Token emitido al crear sesión |
| `X-API-INTERNA` | `HTTP_X_API_INTERNA` | Token de API interna (`API_INTERNA_TOKEN`) |

### Cuándo usar cada mecanismo

| Mecanismo | Cuándo |
|-----------|--------|
| **Sesión anónima** | Guardar respuestas, finalizar, reglas, resumen, sync offline, subir archivos en contexto de formulario |
| **API interna** | Analítica, exportaciones, notificaciones, eliminar archivos, descargar archivos privados |
| **Ambos (upload)** | `POST /archivos/` acepta sesión válida **o** API interna |

Credenciales de sesión también pueden ir en el **body**: `uuid_sesion`, `token_cliente`. El permiso prioriza: path URL → header → body.

### Mensajes 403 (sesión)

- `"La sesión anónima no existe."`
- `"El token de sesión no es válido."`
- `"La sesión ya fue finalizada."` (en mutaciones)

### Mensajes 403 (API interna)

- `"El acceso interno de la API no está autorizado."`
- `"El acceso interno de la API no está disponible en este entorno."` (token no configurado)

---

## Sesión anónima (`PermisoSesionAnonimaValida`)

| Método | URL | Modificable con sesión finalizada |
|--------|-----|----------------------------------|
| POST | `/respuestas/` | No |
| GET | `/sesiones/{uuid}/respuestas/` | Sí (`requiere_sesion_modificable=false`) |
| POST | `/sesiones/{uuid}/validar-finalizacion/` | No |
| POST | `/sesiones/{uuid}/finalizar/` | No |
| GET | `/sesiones/{uuid}/resumen/` | Sí |
| POST | `/sesiones/{uuid}/evaluar-reglas/` | No |
| POST | `/sesiones/{uuid}/preguntas/{codigo}/evaluar-reglas/` | No |
| POST | `/sincronizacion/` | No |

**Ejemplo headers**

```http
X-Sesion-Anonima: f47ac10b-58cc-4372-a567-0e02b2c3d479
X-Token-Sesion: xY9kL2mN3pQ4rS5tU6vW7xY8zA9bC0dE1fG2hI3jK4
```

---

## POST /respuestas/

| Campo body | Tipo | Requerido |
|------------|------|-----------|
| `uuid_sesion` | UUID | sí |
| `codigo_pregunta` | string | sí |
| `valor` | JSON | sí |
| `observacion` | string | no |
| `origen_respuesta` | `web` \| `offline` \| `sincronizacion` | no |
| `fecha_respuesta_cliente` | datetime | no |
| `token_cliente` | string | no (si no va en header) |

**Respuesta 201/200**: `GuardarRespuestaSalida` (incluye `reglas` si aplica).

**Errores**: 400 validación, 403 permiso, 404 sesión/pregunta.

---

## GET /sesiones/{uuid}/respuestas/

**Respuesta 200**: `RespuestasSesion` (`uuid_sesion`, `estado`, `respuestas[]`).

---

## POST /sesiones/{uuid}/validar-finalizacion/

**Body**: vacío (credenciales en headers).

**Respuesta 200**: `ValidacionFinalizacion`.

---

## POST /sesiones/{uuid}/finalizar/

**Respuesta 200**: `FinalizacionFormulario` con `resumen`.

**Respuesta 400**: `ValidacionFinalizacion` si hay obligatorias pendientes.

---

## GET /sesiones/{uuid}/resumen/

**Respuesta 200**: `ResumenFormularioSesion`.

---

## POST /sesiones/{uuid}/evaluar-reglas/

**Respuesta 200**: `ResultadoReglas`.

---

## POST /sesiones/{uuid}/preguntas/{codigo_pregunta}/evaluar-reglas/

**Respuesta 200**: `ResultadoReglas` (evaluación contextual a una pregunta).

---

## POST /sincronizacion/

Ver [06_flujo_offline.md](./06_flujo_offline.md).

**Body obligatorio**: `uuid_sesion`, `token_cliente`, `dispositivo`, `version_app`, `operaciones[]`.

---

## API interna (`PermisoApiInternaTemporal`)

Header **`X-API-INTERNA`** = valor de `API_INTERNA_TOKEN` en el servidor.

| Método | URL |
|--------|-----|
| GET | `/analitica/respuestas/` |
| GET | `/notificaciones/` |
| GET | `/notificaciones/{uuid}/` |
| POST | `/notificaciones/probar/` |
| POST | `/exportaciones/respuestas/` |
| POST | `/exportaciones/catalogos/` |
| POST | `/exportaciones/analitica/` |
| GET | `/exportaciones/{uuid}/` |
| DELETE | `/archivos/{uuid}/` |

---

## Archivos (híbrido / condicional)

| Método | URL | Credencial |
|--------|-----|------------|
| POST | `/archivos/` | Sesión **o** API interna |
| GET | `/archivos/{uuid}/` | Público si `es_publico=true`; else API interna |
| GET | `/archivos/{uuid}/descargar/` | Igual que metadatos |
| DELETE | `/archivos/{uuid}/` | API interna |

Ver [09_archivos.md](./09_archivos.md).

---

## Documentos relacionados

- [11_seguridad.md](./11_seguridad.md)
- [08_motor_reglas.md](./08_motor_reglas.md)
- [10_finalizacion.md](./10_finalizacion.md)
