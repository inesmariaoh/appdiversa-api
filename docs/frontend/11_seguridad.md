# 11 — Seguridad

Modelo de seguridad mínima pre-frontend implementado en el backend. **Keycloak no está integrado.**

## Flujo anónimo MVP

1. Cliente genera `uuid_sesion` (UUID).
2. `POST /sesiones/` crea sesión y devuelve `token_cliente` (o conserva el enviado).
3. Cliente almacena **ambos** de forma segura (memoria + IndexedDB cifrado recomendado).
4. Mutaciones envían credenciales en headers o body.

## token_cliente

| Propiedad | Detalle |
|-----------|---------|
| Generación | `secrets.token_urlsafe(32)` si el cliente no envía uno |
| Transmisión | Header `X-Token-Sesion` o body `token_cliente` |
| Validación | Comparación segura en servidor |
| Sesión finalizada | Mutaciones rechazadas (403) |

**Mensajes 403**

- `"La sesión anónima no existe."`
- `"El token de sesión no es válido."`
- `"La sesión ya fue finalizada."`

## Headers de sesión

```http
X-Sesion-Anonima: {uuid_sesion}
X-Token-Sesion: {token_cliente}
```

Prioridad de lectura del UUID: path URL → header → body.

## API_INTERNA (temporal)

Variable de entorno servidor: `API_INTERNA_TOKEN`.

```http
X-API-INTERNA: {valor_configurado}
```

| Uso | Frontend MVP |
|-----|--------------|
| Analítica, exportaciones, notificaciones | **No** (solo admin/BI) |
| DELETE archivos | **No** |
| Descarga archivos privados | **No** |
| POST archivos sin sesión | **No** |

**Mensajes 403**

- `"El acceso interno de la API no está autorizado."`
- `"El acceso interno de la API no está disponible en este entorno."`

Este mecanismo será **reemplazado por Keycloak**; no usar como solución definitiva en el frontend.

## Keycloak (futuro)

- Header previsto en auditoría: `X-Keycloak-User-Id`.
- Campos `usuario_keycloak` en archivos y exportaciones preparados.
- `permite_registro_final` en formulario indica registro post-envío futuro.
- El frontend MVP **no implementa login**.

## Clasificación de endpoints

| Tipo | Credencial |
|------|------------|
| Público lectura | Ninguna |
| Crear sesión | Ninguna (emite token) |
| Mutación anónima | Sesión + token |
| Administración / BI | API interna |

Ver [03_endpoints_publicos.md](./03_endpoints_publicos.md) y [04_endpoints_protegidos.md](./04_endpoints_protegidos.md).

## Qué NUNCA debe hacer el frontend

1. **No** almacenar `API_INTERNA_TOKEN` en el cliente público.
2. **No** sincronizar offline respuesta por respuesta; solo **batch**.
3. **No** omitir `token_cliente` en mutaciones tras crear sesión.
4. **No** registrar tokens completos en logs del cliente.
5. **No** asumir que todos los endpoints son públicos (`AllowAny` global no implica sin credenciales en mutaciones).
6. **No** finalizar sin validar en servidor.
7. **No** codificar preguntas o reglas en código fuente.
8. **No** exponer mensajes de error técnicos del sistema al usuario (usar `detalle` funcional).

## Formato de errores

```json
{"detalle": "Mensaje funcional en español"}
```

Códigos habituales: 400 validación, 403 permiso, 404 recurso no encontrado.

## Auditoría (backend)

El servidor registra accesos denegados, sincronización y conflictos **sin** almacenar tokens completos. El frontend no consume auditoría en MVP.

## Documentos relacionados

- [04_endpoints_protegidos.md](./04_endpoints_protegidos.md)
- [06_flujo_offline.md](./06_flujo_offline.md)
