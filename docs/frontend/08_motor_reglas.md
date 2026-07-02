# 08 — Motor de reglas

Las reglas se definen en Django Admin y se entregan en la estructura del formulario (`reglas_origen` en cada pregunta). El backend **evalúa** reglas; el frontend **aplica** el resultado en la UI.

## Endpoints de evaluación

| Método | URL | Cuándo llamar |
|--------|-----|---------------|
| POST | `/sesiones/{uuid}/evaluar-reglas/` | Tras cambios globales o al cargar sesión |
| POST | `/sesiones/{uuid}/preguntas/{codigo}/evaluar-reglas/` | Tras guardar una respuesta específica |

Requieren credenciales de sesión anónima.

`POST /respuestas/` puede incluir `reglas` en la respuesta (evaluación automática tras guardar).

## Operadores (`operador` en regla)

| Valor | Descripción |
|-------|-------------|
| `equals` | Igualdad |
| `not_equals` | Distinto |
| `contains` | Contiene (texto) |
| `gt` | Mayor que (número) |
| `lt` | Menor que (número) |
| `in` | Valor en lista |

## Acciones (`accion` en regla)

| Valor | Efecto en frontend |
|-------|-------------------|
| `mostrar` | Mostrar pregunta destino |
| `ocultar` | Ocultar pregunta |
| `habilitar` | Habilitar edición |
| `deshabilitar` | Deshabilitar (solo lectura) |
| `hacer_obligatoria` | Marcar obligatoria |
| `hacer_opcional` | Quitar obligatoriedad |
| `saltar_a_pregunta` | Navegar a pregunta (`pregunta_destino_codigo`) |
| `saltar_a_seccion` | Navegar a sección (`seccion_destino_codigo`) |
| `finalizar_formulario` | Disparar flujo de finalización |
| `no_aplica_formulario` | Marcar formulario como no aplicable |

## Regla en estructura (origen)

```json
{
  "operador": "equals",
  "valor_esperado": "si",
  "accion": "mostrar",
  "mensaje": "Complete la siguiente sección",
  "pregunta_destino_codigo": "P_DETALLE",
  "seccion_destino_codigo": null
}
```

## Respuesta JSON (`ResultadoReglas`)

```json
{
  "preguntas_ocultas": ["P_SECRETA"],
  "preguntas_visibles": ["P_EDAD", "P_NOMBRE"],
  "preguntas_deshabilitadas": [],
  "preguntas_habilitadas": ["P_EDAD"],
  "preguntas_obligatorias": ["P_EDAD"],
  "preguntas_opcionales": ["P_COMENTARIO"],
  "saltar_a_pregunta": null,
  "saltar_a_seccion": null,
  "finalizar_formulario": false,
  "no_aplica_formulario": false,
  "mensajes": ["Debe completar la sección de salud."]
}
```

## Cómo debe reaccionar el frontend

| Campo resultado | Acción UI |
|-----------------|-----------|
| `preguntas_ocultas` | `display: none` o no renderizar |
| `preguntas_visibles` | Mostrar si estaban ocultas por regla |
| `preguntas_deshabilitadas` | `disabled`, no enviar cambios |
| `preguntas_habilitadas` | Permitir edición |
| `preguntas_obligatorias` | Validación local + indicador visual |
| `preguntas_opcionales` | Quitar asterisco obligatorio |
| `saltar_a_pregunta` | Scroll/focus a pregunta por `codigo` |
| `saltar_a_seccion` | Cambiar sección activa |
| `finalizar_formulario` | Llamar validar + finalizar o mostrar confirmación |
| `no_aplica_formulario` | Pantalla “no aplica” / bloquear envío |
| `mensajes` | Toast, alerta o banner informativo |

## Orden de aplicación recomendado

1. Aplicar visibilidad (`ocultas` / `visibles`).
2. Aplicar habilitación.
3. Actualizar obligatoriedad.
4. Ejecutar saltos de navegación.
5. Mostrar mensajes.
6. Evaluar `finalizar_formulario` / `no_aplica_formulario`.

## Offline

En offline, el frontend puede re-evaluar reglas localmente solo si replica la lógica; la **fuente autorizada** es el backend. Tras sync, volver a llamar `evaluar-reglas`.

## Documentos relacionados

- [04_endpoints_protegidos.md](./04_endpoints_protegidos.md)
- [05_modelos_json.md](./05_modelos_json.md)
