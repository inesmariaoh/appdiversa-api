# 10 — Finalización de formulario

Flujo para cerrar el diligenciamiento anónimo y obtener resumen.

## Secuencia recomendada

1. `POST /sesiones/{uuid}/validar-finalizacion/` — pre-chequeo sin cerrar.
2. Si `es_valido=true` → `POST /sesiones/{uuid}/finalizar/`.
3. `GET /sesiones/{uuid}/resumen/` — pantalla de confirmación.

Todos requieren credenciales de sesión (`X-Sesion-Anonima` + `X-Token-Sesion`).

## Validación

**POST** `/api/v1/sesiones/{uuid_sesion}/validar-finalizacion/`

**Respuesta 200**

```json
{
  "es_valido": false,
  "total_pendientes": 2,
  "preguntas_pendientes": [
    {
      "codigo": "P_EDAD",
      "texto": "¿Cuál es su edad?",
      "seccion_codigo": "sec_01",
      "seccion_titulo": "Datos generales",
      "orden": 1
    }
  ]
}
```

| Campo | Descripción |
|-------|-------------|
| `es_valido` | `true` si no hay obligatorias pendientes |
| `total_pendientes` | Cantidad de preguntas sin respuesta útil |
| `preguntas_pendientes` | Detalle para navegación en UI |

**Errores**

| Código | `detalle` típico |
|--------|------------------|
| 403 | Token inválido / sesión finalizada |
| 404 | Sesión no existe |

## Finalizar

**POST** `/api/v1/sesiones/{uuid_sesion}/finalizar/`

**Respuesta 200** (éxito)

```json
{
  "estado": "finalizada",
  "mensaje": "El formulario fue finalizado correctamente.",
  "resumen": {
    "uuid_sesion": "...",
    "estado": "finalizada",
    "formulario": { "uuid": "...", "codigo": "...", "nombre": "..." },
    "version": { "numero_version": 1 },
    "respuestas": []
  }
}
```

**Respuesta 400** (obligatorias pendientes)

Body = `ValidacionFinalizacion` (igual que validar).

**Respuesta 400** (ya finalizado)

```json
{"detalle": "El formulario ya fue finalizado."}
```

Tras finalizar, mutaciones (`POST respuestas`, sync) reciben 403:

```json
{"detalle": "La sesión ya fue finalizada."}
```

## Resumen

**GET** `/api/v1/sesiones/{uuid_sesion}/resumen/`

Permitido con sesión finalizada (`requiere_sesion_modificable=false`).

Estructura: ver [05_modelos_json.md](./05_modelos_json.md#resumen).

## Integración con reglas

Si `ResultadoReglas.finalizar_formulario=true`, el frontend puede:

1. Validar automáticamente.
2. Mostrar confirmación al usuario.
3. Finalizar si `es_valido`.

## Offline

Antes de finalizar offline:

1. Sincronizar batch pendiente (`POST /sincronizacion/`).
2. Validar en servidor (no confiar solo en validación local).
3. Finalizar solo con conexión.

## UI recomendada

- Botón “Enviar” deshabilitado hasta `es_valido=true` o con modal de pendientes.
- Lista clickeable de `preguntas_pendientes` → scroll a campo.
- Pantalla de éxito con datos de `resumen` y textos de `configuracion` (`texto_confirmacion_envio_*`).

## Documentos relacionados

- [02_flujo_completo_aplicacion.md](./02_flujo_completo_aplicacion.md)
- [08_motor_reglas.md](./08_motor_reglas.md)
