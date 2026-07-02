# 05 — Modelos JSON

Contratos JSON devueltos o aceptados por la API, basados en serializers implementados.

---

## ConfiguracionInterfaz

`GET /interfaz/configuracion/`

```json
{
  "nombre_aplicativo": "AppDiversa",
  "nombre_corto": "Diversa",
  "descripcion_aplicativo": "Motor de formularios",
  "texto_pie_pagina": "© 2026",
  "texto_titulo_seccion_encuestas": "Formularios disponibles",
  "texto_descripcion_seccion_encuestas": "Seleccione un formulario",
  "email_soporte": "soporte@ejemplo.com",
  "texto_terminos_condiciones": "Texto legal...",
  "texto_autorizacion_datos": "Autorización...",
  "texto_verificacion_exitosa_titulo": "Verificación exitosa",
  "texto_verificacion_exitosa_cuerpo": "Cuerpo...",
  "texto_confirmacion_envio_titulo": "Enviado",
  "texto_confirmacion_envio_subtitulo": "Gracias",
  "meta_titulo_seo": "AppDiversa",
  "meta_descripcion_seo": "Descripción SEO",
  "accion_lengua_senas_habilitada": true,
  "url_lengua_senas": "https://...",
  "texto_lengua_senas": "Lengua de señas",
  "logo_principal": "http://localhost:8000/media/...",
  "logo_secundario": null,
  "logo_institucional": null,
  "favicon": null,
  "color_primario": "#0066CC",
  "color_secundario": "#004499",
  "color_acento": "#FF6600",
  "contenido_accesible": {}
}
```

`contenido_accesible` solo si `incluir_accesibilidad=true`.

---

## FormularioDisponible

```json
{
  "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "codigo": "encuesta_salud",
  "nombre": "Encuesta de salud",
  "descripcion": "Descripción",
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
```

`tipo_formulario`: `encuesta`, `registro`, `consentimiento`, `matriz`, `otro`.

---

## FormularioEstructura

```json
{
  "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "codigo": "encuesta_salud",
  "nombre": "Encuesta de salud",
  "descripcion": "Descripción larga",
  "introduccion": "Texto introductorio",
  "objetivo": "Objetivo del estudio",
  "tipo_formulario": "encuesta",
  "imagen_portada": "http://localhost:8000/media/...",
  "version": {
    "id": 1,
    "numero_version": 1
  },
  "textos": [
    {
      "tipo": "consentimiento",
      "titulo": "Consentimiento",
      "contenido": "HTML o texto",
      "orden": 1
    }
  ],
  "secciones": [
    {
      "codigo": "sec_01",
      "titulo": "Datos generales",
      "descripcion": "",
      "texto_ayuda": "",
      "orden": 1,
      "preguntas": []
    }
  ]
}
```

---

## Seccion

Campos en `secciones[]`: `codigo`, `titulo`, `descripcion`, `texto_ayuda`, `orden`, `preguntas`.

---

## Pregunta

```json
{
  "codigo": "P_EDAD",
  "texto": "¿Cuál es su edad?",
  "descripcion": "",
  "tooltip": "Edad en años cumplidos",
  "tipo_pregunta": "numero",
  "es_obligatoria": true,
  "es_pregunta_filtro": false,
  "permite_otro": false,
  "permite_observacion": false,
  "orden": 1,
  "longitud_minima": null,
  "longitud_maxima": null,
  "valor_minimo": "0",
  "valor_maximo": "120",
  "expresion_regular": "",
  "mensaje_error": "",
  "usa_catalogo": false,
  "catalogo_asociado": null,
  "pregunta_padre_catalogo": null,
  "permite_busqueda_catalogo": false,
  "limite_items_catalogo": null,
  "fuente_opciones": "opciones_fijas",
  "opciones": [],
  "filas_matriz": [],
  "columnas_matriz": [],
  "reglas_origen": []
}
```

**Tipos de pregunta** (`tipo_pregunta`): `texto_corto`, `texto_largo`, `numero`, `fecha`, `hora`, `fecha_hora`, `radio`, `checkbox`, `select`, `select_multiple`, `autocomplete`, `likert`, `matriz`, `archivo`, `firma`, `geolocalizacion`, `audio`, `video`.

**Catálogo asociado** (si `usa_catalogo=true`):

```json
{
  "codigo": "municipios",
  "nombre": "Municipios",
  "endpoint_items": "/api/v1/catalogos/municipios/items/"
}
```

---

## Opcion

```json
{
  "codigo": "OP_SI",
  "etiqueta": "Sí",
  "valor": "si",
  "tooltip": "",
  "orden": 1,
  "es_excluyente": false,
  "activa_otro": false
}
```

---

## Catalogo

```json
{
  "codigo": "departamentos",
  "nombre": "Departamentos",
  "descripcion": "Departamentos del país",
  "tipo_catalogo": "jerarquico",
  "orden": 1
}
```

---

## ItemCatalogo

```json
{
  "codigo": "05",
  "codigo_catalogo": "departamentos",
  "nombre": "Antioquia",
  "descripcion": "",
  "valor": "05",
  "codigo_padre": null,
  "codigo_externo": "",
  "metadatos": {},
  "orden": 1,
  "esta_activo": true
}
```

---

## Respuesta (listado sesión)

```json
{
  "codigo_pregunta": "P_EDAD",
  "tipo_pregunta": "numero",
  "valor_numero": "35.0000",
  "valor_texto": "",
  "valor_json": null,
  "valor_booleano": null,
  "valor_fecha": null,
  "valor_hora": null,
  "valor_fecha_hora": null,
  "origen_respuesta": "web",
  "version_respuesta": 2,
  "fecha_respuesta_cliente": "2026-06-28T10:30:00Z",
  "fecha_respuesta_servidor": "2026-06-28T10:30:05Z"
}
```

**Guardar respuesta — salida**

```json
{
  "uuid_sesion": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "codigo_pregunta": "P_EDAD",
  "version_respuesta": 1,
  "origen_respuesta": "web",
  "requiere_sincronizacion": false,
  "esta_eliminado": false,
  "reglas": {
    "preguntas_ocultas": [],
    "preguntas_visibles": ["P_EDAD"],
    "preguntas_deshabilitadas": [],
    "preguntas_habilitadas": [],
    "preguntas_obligatorias": [],
    "preguntas_opcionales": [],
    "saltar_a_pregunta": null,
    "saltar_a_seccion": null,
    "finalizar_formulario": false,
    "no_aplica_formulario": false,
    "mensajes": []
  }
}
```

---

## SesionAnonima

```json
{
  "uuid_sesion": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "estado": "en_proceso",
  "token_cliente": "xY9kL2mN3pQ4rS5tU6vW7xY8zA9bC0dE1fG2hI3jK4"
}
```

---

## Resumen

```json
{
  "uuid_sesion": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "estado": "finalizada",
  "formulario": {
    "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "codigo": "encuesta_salud",
    "nombre": "Encuesta de salud"
  },
  "version": {
    "numero_version": 1
  },
  "respuestas": [
    {
      "seccion_codigo": "sec_01",
      "seccion_titulo": "Datos generales",
      "pregunta_codigo": "P_EDAD",
      "pregunta_texto": "¿Cuál es su edad?",
      "tipo_pregunta": "numero",
      "valor": 35,
      "observacion": ""
    }
  ]
}
```

---

## Analitica (registro plano)

```json
{
  "uuid_sesion": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "estado_sesion": "finalizada",
  "fecha_inicio_sesion": "2026-06-28T09:00:00+00:00",
  "fecha_ultima_actividad": "2026-06-28T10:00:00+00:00",
  "formulario_uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "formulario_codigo": "encuesta_salud",
  "formulario_nombre": "Encuesta de salud",
  "tipo_formulario": "encuesta",
  "numero_version": 1,
  "seccion_codigo": "sec_01",
  "seccion_titulo": "Datos generales",
  "pregunta_codigo": "P_EDAD",
  "pregunta_texto": "¿Cuál es su edad?",
  "tipo_pregunta": "numero",
  "usa_catalogo": false,
  "catalogo_codigo": null,
  "catalogo_nombre": null,
  "respuesta_valor": 35,
  "respuesta_texto": "",
  "respuesta_numero": "35.0000",
  "respuesta_json": null,
  "observacion": "",
  "origen_respuesta": "web",
  "version_respuesta": 1,
  "fecha_respuesta_cliente": "2026-06-28T10:30:00+00:00",
  "fecha_respuesta_servidor": "2026-06-28T10:30:05+00:00",
  "es_anonima": true,
  "es_offline": false
}
```

---

## ArchivoRepositorio

```json
{
  "uuid": "1d5cc128-286e-4433-acc4-cfb13950bd98",
  "nombre_original": "documento.pdf",
  "extension": "pdf",
  "mime_type": "application/pdf",
  "tamano_bytes": 102400,
  "checksum_sha256": "abc123...",
  "tipo_archivo": "documento",
  "es_publico": false,
  "origen": "respuesta",
  "estado": "activo",
  "descripcion": "",
  "metadatos": {},
  "fecha_carga": "2026-06-28T12:00:00Z",
  "usuario_keycloak": "",
  "uuid_sesion": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "url": "http://localhost:8000/api/v1/archivos/1d5cc128-286e-4433-acc4-cfb13950bd98/descargar/"
}
```

---

## Sincronizacion (batch salida)

```json
{
  "operaciones_procesadas": 3,
  "operaciones_actualizadas": 2,
  "duplicadas": 1,
  "conflictos": [
    {
      "uuid_local": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "mensaje": "Conflicto de versiones entre cliente y servidor.",
      "respuesta_id": 42
    }
  ],
  "errores": [
    {
      "uuid_local": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "mensaje": "El checksum de la operación no es válido."
    }
  ]
}
```

---

## Exportacion

```json
{
  "uuid": "e5f6a7b8-c9d0-1234-efab-567890abcdef",
  "tipo": "respuestas",
  "estado": "finalizada",
  "usuario": "admin",
  "fecha_inicio": "2026-06-28T14:00:00Z",
  "fecha_fin": "2026-06-28T14:00:05Z",
  "archivo_uuid": "1d5cc128-286e-4433-acc4-cfb13950bd98",
  "formato": "csv",
  "parametros": {"formulario_codigo": "encuesta_salud"},
  "registros_exportados": 150,
  "error": ""
}
```

---

## Notificacion

```json
{
  "uuid": "f6a7b8c9-d0e1-2345-fabc-678901abcdef",
  "codigo_plantilla": "confirmacion_envio",
  "canal": "email",
  "destinatario": "usuario@ejemplo.com",
  "estado": "enviada",
  "fecha_programada": null,
  "fecha_envio": "2026-06-28T15:00:00Z",
  "asunto_generado": "Confirmación",
  "contenido_generado": "Su formulario fue enviado.",
  "variables_utilizadas": {},
  "respuesta_proveedor": {},
  "numero_intentos": 1,
  "error_envio": ""
}
```

---

## TraduccionContenido

```json
{
  "id": 1,
  "codigo_idioma": "es",
  "entidad": "Pregunta",
  "entidad_uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "campo": "texto",
  "valor_traducido": "Texto traducido",
  "lectura_facil": "Texto lectura fácil",
  "texto_alternativo": "ALT",
  "transcripcion": "",
  "archivo_audio": null,
  "archivo_video": null,
  "archivo_imagen": null,
  "archivo_lengua_senas": null,
  "metadatos": {},
  "esta_activa": true
}
```

---

## Documentos relacionados

- [03_endpoints_publicos.md](./03_endpoints_publicos.md)
- [04_endpoints_protegidos.md](./04_endpoints_protegidos.md)
