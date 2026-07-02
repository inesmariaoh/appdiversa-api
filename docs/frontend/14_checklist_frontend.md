# 14 — Checklist Frontend

Checklist de implementación del frontend dinámico AppDiversa. Marcar cada ítem al completarlo.

---

## Configuración e interfaz

- [ ] Consumir `GET /interfaz/configuracion/` al iniciar
- [ ] Aplicar `color_primario`, `color_secundario`, `color_acento`
- [ ] Cargar logos y favicon desde URLs del API
- [ ] Mostrar textos legales (`terminos`, `autorizacion_datos`)
- [ ] Configurar meta SEO (`meta_titulo_seo`, `meta_descripcion_seo`)
- [ ] Soporte `idioma` en query de configuración
- [ ] Soporte `incluir_accesibilidad` cuando se requiera
- [ ] Pantalla de error si configuración no carga (fallback mínimo)

## Formularios

- [ ] Consumir `GET /formularios/disponibles/`
- [ ] Mostrar cards/lista con `nombre`, `descripcion`, `tiempo_estimado_minutos`
- [ ] Respetar `fecha_inicio` / `fecha_fin` de vigencia
- [ ] Indicar `permite_offline` en UI
- [ ] Consumir `GET /formularios/{uuid}/estructura/`
- [ ] Renderizar secciones ordenadas por `orden`
- [ ] Renderizar preguntas dinámicamente por `tipo_pregunta`
- [ ] No codificar preguntas en código fuente
- [ ] Mostrar textos del formulario (`introduccion`, `objetivo`, `textos[]`)

## Sesión anónima

- [ ] Generar `uuid_sesion` en cliente (UUID v4)
- [ ] `POST /sesiones/` con `uuid_formulario`
- [ ] Almacenar `token_cliente` de forma segura
- [ ] Enviar headers `X-Sesion-Anonima` + `X-Token-Sesion` en mutaciones
- [ ] Alternativa: `uuid_sesion` + `token_cliente` en body
- [ ] Manejar 403 token inválido (recrear sesión o mensaje al usuario)
- [ ] Manejar sesión finalizada (403 en mutaciones)

## Respuestas

- [ ] `POST /respuestas/` al cambiar valor
- [ ] Enviar `codigo_pregunta` y `valor` según tipo
- [ ] Enviar `origen_respuesta`: `web` online, `offline` en cola local
- [ ] Enviar `fecha_respuesta_cliente` opcional
- [ ] Procesar `reglas` en respuesta de guardado
- [ ] Mapear tipos: texto, número, fecha, hora, booleano, JSON, geolocalización
- [ ] Validación local según `valor_minimo`, `valor_maximo`, `expresion_regular`

## Motor de reglas

- [ ] `POST evaluar-reglas` tras cambios relevantes
- [ ] `POST preguntas/{codigo}/evaluar-reglas` tras respuesta individual
- [ ] Ocultar / mostrar preguntas según resultado
- [ ] Habilitar / deshabilitar campos
- [ ] Actualizar obligatoriedad visual
- [ ] Navegación `saltar_a_pregunta` / `saltar_a_seccion`
- [ ] Manejar `finalizar_formulario` y `no_aplica_formulario`
- [ ] Mostrar `mensajes` de reglas al usuario

## Catálogos

- [ ] Cargar catálogos vía `catalogo_asociado.endpoint_items`
- [ ] Jerarquías con `codigo_padre` y `/hijos/`
- [ ] Autocomplete con `busqueda` + `limite`
- [ ] Dependencias padre-hijo (`pregunta_padre_catalogo`)
- [ ] Validar valor contra catálogo antes de enviar (UX)
- [ ] Manejar error 400 valor no pertenece a catálogo

## Offline e IndexedDB

- [ ] Detectar pérdida de conexión (`navigator.onLine` + heartbeat)
- [ ] Persistir estructura de formulario en IndexedDB
- [ ] Persistir sesión y `token_cliente`
- [ ] Cola de operaciones con `uuid_local`, `version_cliente`, `fecha_cliente`
- [ ] Calcular `checksum` SHA-256 antes de sync
- [ ] **No** sincronizar respuesta por respuesta; solo batch
- [ ] `POST /sincronizacion/` al reconectar
- [ ] Procesar `duplicadas`, `conflictos`, `errores` del batch
- [ ] Reintentos solo para operaciones en error
- [ ] Incrementar `version_cliente` solo al editar localmente
- [ ] Indicador visual “pendiente de sincronizar”

## Sincronización

- [ ] Enviar `dispositivo` y `version_app` en batch
- [ ] Transaccionalidad: errores parciales no bloquean UI
- [ ] Registrar conflictos para revisión (si UI admin futura)
- [ ] Sync antes de validar/finalizar

## Validación y finalización

- [ ] `POST validar-finalizacion` antes de enviar
- [ ] Listar `preguntas_pendientes` con navegación
- [ ] `POST finalizar` solo si `es_valido`
- [ ] Manejar 400 con pendientes sin cerrar sesión
- [ ] `GET resumen` en pantalla de confirmación
- [ ] Textos de confirmación desde configuración interfaz

## Resumen y post-envío

- [ ] Mostrar respuestas consolidadas del resumen
- [ ] Estado `finalizada` en UI
- [ ] Preparar hook para registro Keycloak futuro (`permite_registro_final`)

## Archivos

- [ ] Subida multipart `POST /archivos/` con sesión
- [ ] Seleccionar `tipo_archivo` y `origen` correctos
- [ ] Respetar tamaños máximos en validación cliente
- [ ] Preguntas `archivo`, `firma`, `audio`, `video`
- [ ] Usar `url` de metadatos para preview (públicos)
- [ ] No intentar DELETE (requiere API interna)

## Internacionalización

- [ ] Parámetro `idioma` en endpoints públicos
- [ ] `GET /internacionalizacion/traducciones/` para overrides
- [ ] Combinar traducciones con estructura de formulario
- [ ] Contenido accesible (`lectura_facil`, `texto_alternativo`)

## Analítica (solo admin / no MVP público)

- [ ] No exponer `X-API-INTERNA` en bundle público
- [ ] Documentar separación frontend usuario vs herramientas BI

## Manejo de errores

- [ ] Parsear siempre `{"detalle": "..."}`
- [ ] No mostrar stack traces ni tipos de error del sistema
- [ ] 403 → mensaje de sesión / permisos
- [ ] 404 → recurso no encontrado
- [ ] 400 → validación con mensaje funcional
- [ ] Timeout y errores de red → modo offline

## UX: loading, skeleton, retry

- [ ] Skeleton al cargar formularios y estructura
- [ ] Loading en guardado de respuestas
- [ ] Retry automático con backoff para lecturas públicas
- [ ] Retry manual para sync batch fallido
- [ ] Debounce en autocomplete de catálogos

## Responsive y PWA

- [ ] Layout responsive (móvil, tablet, desktop)
- [ ] Touch-friendly en firmas y geolocalización
- [ ] Manifest PWA (favicon, nombre desde configuración)
- [ ] Service Worker **no requerido por backend** (decisión frontend)
- [ ] Offline-first donde `permite_offline=true`

## Accesibilidad (WCAG)

- [ ] Labels asociados a cada pregunta dinámica
- [ ] Navegación por teclado en formulario multi-sección
- [ ] Contraste según colores de interfaz (validar WCAG AA)
- [ ] `contenido_accesible` cuando `incluir_accesibilidad=true`
- [ ] Soporte `accion_lengua_senas_habilitada` y `url_lengua_senas`
- [ ] Anuncios para lectores de pantalla en reglas (mensajes)

## Testing

- [ ] Tests unitarios de mapeo tipo_pregunta → componente
- [ ] Tests de integración con API mock (OpenAPI contract)
- [ ] Tests E2E: crear sesión → responder → finalizar
- [ ] Tests E2E offline: cola → sync → finalizar
- [ ] Tests de reglas con fixtures del backend

## Calidad

- [ ] Lighthouse performance / accessibility / best practices
- [ ] SonarQube en repositorio frontend (calidad A)
- [ ] WCAG 2.1 AA auditoría en formulario dinámico
- [ ] No reducir cobertura de tests al agregar formularios nuevos

## Seguridad frontend

- [ ] No loguear `token_cliente` completo
- [ ] No incluir `API_INTERNA_TOKEN` en build público
- [ ] Sanitizar HTML en textos de formulario si se renderiza rich text
- [ ] CSP headers en despliegue

## Documentación

- [ ] Equipo alineado con [openapi_export.json](./openapi_export.json)
- [ ] Actualizar checklist al cambiar contratos API

---

## Documentos de referencia

| # | Documento |
|---|-----------|
| 01 | [Arquitectura](./01_arquitectura_frontend_backend.md) |
| 02 | [Flujo completo](./02_flujo_completo_aplicacion.md) |
| 03 | [Endpoints públicos](./03_endpoints_publicos.md) |
| 04 | [Endpoints protegidos](./04_endpoints_protegidos.md) |
| 05 | [Modelos JSON](./05_modelos_json.md) |
| 06 | [Offline](./06_flujo_offline.md) |
| 07 | [Catálogos](./07_catalogos.md) |
| 08 | [Reglas](./08_motor_reglas.md) |
| 09 | [Archivos](./09_archivos.md) |
| 10 | [Finalización](./10_finalizacion.md) |
| 11 | [Seguridad](./11_seguridad.md) |
| 12 | [Swagger](./12_swagger.md) |
| 13 | [Power BI](./13_powerbi.md) |
