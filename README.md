# AppDiversa API

Backend de AppDiversa 2.0: motor de formularios parametrizables. La estructura de cada formulario, sus preguntas, reglas y flujos se define desde la base de datos y el administrador Django, sin codificar encuestas específicas en el código fuente.

## Tecnologías

- Python 3.12
- Django 5.x
- Django REST Framework
- MySQL 8.0
- django-cors-headers
- django-environ
- gunicorn
- whitenoise
- Docker y Docker Compose
- pytest + pytest-django

## Requisitos previos

**Entorno virtual:**

- Python 3.12
- MySQL 8.x (local o contenedor Docker en puerto 3307)
- Cliente de compilación para `mysqlclient` en Windows (Visual Studio Build Tools)

**Docker:**

- Docker Desktop o Docker Engine
- Docker Compose v2

## Instalación inicial

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio> appdiversa-api
cd appdiversa-api
```

### 2. Configurar variables de entorno

**Entorno virtual (MySQL local o contenedor en 3307):**

```bash
copy .env.example .env
```

**Docker Compose:**

```bash
copy .env.docker.example .env
```

Editar `.env` según el modo de ejecución elegido.

## Ejecución local con entorno virtual

```bash
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

El API estará disponible en `http://127.0.0.1:8000/api/v1/`.

Endpoint de verificación: `GET http://127.0.0.1:8000/api/v1/salud/`

**Conectar al MySQL del contenedor Docker desde el entorno virtual:**

Si solo se ejecuta el servicio `db` con Docker, usar en `.env`:

```
DB_HOST=localhost
DB_PORT=3307
DB_PASSWORD=appdiversa_pass
```

**MySQL instalado localmente:**

```sql
CREATE DATABASE appdiversa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'appdiversa_user'@'localhost' IDENTIFIED BY 'appdiversa_pass';
GRANT ALL PRIVILEGES ON appdiversa.* TO 'appdiversa_user'@'localhost';
FLUSH PRIVILEGES;
```

Usar `DB_HOST=localhost` y `DB_PORT=3306` en `.env`.

## Ejecución local con Docker

```bash
docker compose up --build
```

Con los servicios en ejecución:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py test
```

El API estará disponible en `http://127.0.0.1:8000/api/v1/`.

| Servicio | Contenedor | Puerto |
|----------|------------|--------|
| Backend Django | `appdiversa_api` | 8000 |
| MySQL 8.0 | `appdiversa_mysql` | 3307 (host) → 3306 (contenedor) |

## Pruebas

Las pruebas pueden ejecutarse de dos formas:

**Local con entorno virtual:**

```bash
python manage.py test
```

**Con Docker:**

```bash
docker compose exec backend python manage.py test
```

**Con pytest (entorno virtual):**

```bash
pytest
```

**Recomendación:**

- Durante desarrollo rápido: entorno virtual.
- Antes de subir cambios o desplegar: Docker, para validar el ambiente completo (backend + MySQL).

## Validación del proyecto

**Entorno virtual:**

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
```

**Docker:**

```bash
docker compose up --build
docker compose exec backend python manage.py check
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py test
```

## Estructura del proyecto

```
appdiversa-api/
├── appdiversa_core/          # Configuración central del proyecto
│   ├── settings/             # base, local, dev, prod
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── aplicaciones/
│   ├── formularios/          # Motor de formularios parametrizables
│   ├── respuestas/           # Respuestas de formularios
│   ├── sesiones_anonimas/    # Flujo anónimo (MVP)
│   ├── sincronizacion/       # Sincronización offline idempotente
│   ├── auditoria/            # Registro de auditoría
│   ├── analitica/            # Normalización de respuestas para BI
│   ├── catalogos/            # Catálogos parametrizables empresariales
│   └── comun/                # Utilidades y rutas comunes
├── Dockerfile
├── docker-compose.yml
├── Procfile
├── render-build.sh
├── .dockerignore
├── manage.py
├── requirements.txt
├── .env.example
├── .env.docker.example
├── pytest.ini
└── README.md
```

## Entornos de configuración

| Módulo de settings | Uso |
|--------------------|-----|
| `appdiversa_core.settings.local` | Desarrollo local |
| `appdiversa_core.settings.dev` | Servidor de desarrollo desplegado |
| `appdiversa_core.settings.prod` | Producción |

Configurar `DJANGO_SETTINGS_MODULE` en `.env` según el entorno.

Todas las credenciales y secretos se leen desde variables de entorno; no se almacenan en el código fuente.

## Despliegue en Render

El proyecto esta preparado para desplegarse en [Render](https://render.com) con **MySQL externo** (PlanetScale, Aiven, Railway, RDS, etc.).

### Archivos de despliegue

| Archivo | Proposito |
|---------|-----------|
| `Procfile` | Comando de arranque con Gunicorn |
| `render-build.sh` | Instalacion de dependencias y `collectstatic` |
| `appdiversa_core/settings/prod.py` | Seguridad HTTPS, cookies seguras y WhiteNoise |

### Configuracion del servicio web en Render

1. Crear un **Web Service** conectado al repositorio de GitHub.
2. **Runtime:** Python 3.12 (o usar el `Dockerfile` existente si se prefiere contenedor).
3. **Build Command:**

   ```bash
   ./render-build.sh
   ```

   En Windows local el script es Bash; Render lo ejecuta en Linux. Alternativa equivalente:

   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput
   ```

4. **Start Command:** Render detecta el `Procfile` automaticamente. Si se configura manualmente:

   ```bash
   gunicorn appdiversa_core.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
   ```

5. **Release Command** (recomendado, ejecuta migraciones en cada despliegue):

   ```bash
   python manage.py migrate --noinput
   ```

### Variables de entorno en Render

| Variable | Ejemplo / notas |
|----------|-----------------|
| `DJANGO_SETTINGS_MODULE` | `appdiversa_core.settings.prod` |
| `SECRET_KEY` | Clave aleatoria larga (obligatoria) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `tu-api.onrender.com,tu-dominio.com` |
| `DB_NAME` | Nombre de la base MySQL externa |
| `DB_USER` | Usuario MySQL |
| `DB_PASSWORD` | Contrasena MySQL |
| `DB_HOST` | Host del servicio MySQL |
| `DB_PORT` | `3306` (o el puerto del proveedor) |
| `CORS_ALLOWED_ORIGINS` | `https://tu-frontend.onrender.com` |
| `FRONTEND_URL` | URL publica del frontend |
| `API_INTERNA_TOKEN` | Token interno temporal |
| `NOTIFICACIONES_PROVEEDOR` | `dummy` o `smtp` segun entorno |
| `EMAIL_*` | Solo si se usa SMTP real |

Consultar `.env.example` para la lista completa de variables opcionales.

### Probar Gunicorn en local antes de desplegar

```bash
set DJANGO_SETTINGS_MODULE=appdiversa_core.settings.local
python manage.py collectstatic --noinput
gunicorn appdiversa_core.wsgi:application --bind 127.0.0.1:8000
```

En PowerShell:

```powershell
$env:DJANGO_SETTINGS_MODULE = "appdiversa_core.settings.local"
python manage.py collectstatic --noinput
gunicorn appdiversa_core.wsgi:application --bind 127.0.0.1:8000
```

### Subir el proyecto a GitHub

```bash
git init
git add .
git status
git commit -m "Preparar AppDiversa API para despliegue en Render"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/appdiversa-api.git
git push -u origin main
```

Antes del primer commit, verificar que `.env`, `media/`, `staticfiles/` y `venv/` no aparezcan en `git status`.

### Recomendaciones antes de produccion

- Generar `SECRET_KEY` unica y nunca reutilizar la de desarrollo.
- Mantener `DEBUG=False` y revisar `ALLOWED_HOSTS` con el dominio real de Render.
- Configurar `CORS_ALLOWED_ORIGINS` solo con los dominios del frontend autorizados.
- Ejecutar migraciones en cada despliegue (`migrate --noinput`).
- El disco de Render es efimero: usar almacenamiento externo (S3, Cloudinary, etc.) para `media/` en produccion.
- Activar respaldos automaticos en el servicio MySQL externo.
- Rotar credenciales SMTP y de base de datos periodicamente.
- Ejecutar la suite de pruebas antes de cada release: `python manage.py test` o `pytest`.
- Planificar integracion de Keycloak para reemplazar el token interno temporal (`API_INTERNA_TOKEN`).

El proyecto tambien puede desplegarse con el `Dockerfile` existente si se prefiere contenedor en lugar del buildpack Python de Render.

## API

Todas las rutas de la API están bajo el prefijo `/api/v1/`.

| Ruta | Descripción |
|------|-------------|
| `/api/v1/salud/` | Verificación de salud del servicio |
| `/api/v1/formularios/` | Formularios |
| `/api/v1/respuestas/` | Respuestas |
| `/api/v1/sesiones-anonimas/` | Sesiones anónimas |
| `/api/v1/sincronizacion/` | Sincronización offline por lotes |
| `/api/v1/auditoria/` | Auditoría |
| `/api/v1/analitica/` | Analítica (respuestas planas para BI) |
| `/api/v1/catalogos/` | Catálogos parametrizables |

## Sincronización offline

El motor de sincronización (`aplicaciones/sincronizacion`) es el único mecanismo autorizado para enviar respuestas capturadas offline. El frontend nunca debe sincronizar respuesta por respuesta; siempre debe enviar un **batch** (lote) de operaciones.

### Flujo general

1. El dispositivo almacena temporalmente en **IndexedDB** (Web) o SQLite (React Native futuro): estructura del formulario, respuestas parciales, cola de sincronización y estado.
2. Al recuperar conexión, el frontend envía un lote a `POST /api/v1/sincronizacion/`.
3. El backend procesa cada operación de forma independiente y transaccional; una operación fallida no cancela las demás.
4. El backend retorna resumen: procesadas, actualizadas, duplicadas, conflictos y errores.

### Identificador `uuid_local`

Cada respuesta offline genera un `uuid_local` único en el dispositivo. Este identificador:

- Es **único** en el servidor (`UNIQUE` en `Respuesta`).
- **Nunca cambia** tras crearse.
- Garantiza **idempotencia**: reenviar el mismo `uuid_local` no crea duplicados.

### Versionado y conflictos

Cada respuesta offline lleva `version_cliente` (entero que incrementa en cada modificación local) y `fecha_modificacion_cliente`. Reglas:

- Si `version_cliente` recibida es **mayor**, se actualiza.
- Si es **menor**, se registra conflicto (estrategia inicial **Last Write Wins** con desempate por fecha).
- Si es **igual**, la operación se marca como duplicada.
- Los conflictos se registran en `ConflictoSincronizacion` sin perder información del cliente ni del servidor.

### Autenticación del batch

El endpoint exige sesión anónima válida (`uuid_sesion` + `token_cliente` en body o headers `X-Sesion-Anonima` / `X-Token-Sesion`).

### Checksum

Opcionalmente cada operación puede incluir `checksum` (SHA-256 del payload canónico). Si no coincide, la operación se rechaza con error funcional.

### Reintentos

El modelo `OperacionSincronizacion` registra `numero_reintentos` y `ultimo_error` para soportar reintentos desde el frontend sin duplicar datos.

### Ejemplo de solicitud

```json
{
  "uuid_sesion": "…",
  "token_cliente": "…",
  "dispositivo": "web-indexeddb",
  "version_app": "1.0.0",
  "operaciones": [
    {
      "uuid_local": "…",
      "codigo_pregunta": "P1",
      "valor": 42,
      "version_cliente": 1,
      "fecha_cliente": "2026-06-28T10:00:00+00:00",
      "checksum": "…"
    }
  ]
}
```

## Catálogos parametrizables

El módulo `aplicaciones/catalogos` administra listas reutilizables (países, departamentos, municipios, ocupaciones, grupos étnicos, tipos de discapacidad, áreas de residencia, estratos, sexos al nacer, identidades de género, orientaciones sexuales y otros dominios) desde Django Admin y expone su contenido por API para el frontend.

Cada catálogo puede contener items con jerarquía mediante `item_padre`, lo que permite estructuras como país → departamento → municipio, además de catálogos simples como sexo, género o estrato.

El modelo `CatalogoGeografico` en formularios permanece como especialización geográfica compatible; en una fase posterior puede integrarse o sincronizarse con este motor general.

Las preguntas tipo `select`, `autocomplete`, `radio` o `checkbox` del motor de formularios podrán consumir estos catálogos mediante parametrización en una fase posterior.

Endpoints principales:

| Ruta | Descripción |
|------|-------------|
| `GET /api/v1/catalogos/` | Lista catálogos activos |
| `GET /api/v1/catalogos/{codigo}/items/` | Items del catálogo (filtros: `codigo_padre`, `solo_activos`) |
| `GET /api/v1/catalogos/{codigo}/items/{codigo_item}/hijos/` | Hijos directos de un item |

## Carga DIVIPOLA

Los departamentos y municipios de Colombia se cargan desde el dataset oficial **DIVIPOLA — Códigos municipios** (Datos Abiertos Colombia, recurso Socrata `gdxc-w37w`) mediante un comando de gestión. Los datos quedan disponibles en los catálogos parametrizables `departamentos` y `municipios`, consumibles por los endpoints existentes de catálogos.

**Importación desde la API (requiere conexión a internet):**

```bash
docker compose exec backend python manage.py importar_divipola
```

**Simulación sin persistir cambios:**

```bash
docker compose exec backend python manage.py importar_divipola --dry-run
```

**Importación desde archivo local JSON o CSV (sin internet):**

```bash
docker compose exec backend python manage.py importar_divipola --archivo divipola.json
```

El comando es idempotente: puede ejecutarse varias veces sin duplicar registros. Al finalizar muestra un resumen con departamentos y municipios creados, actualizados y errores detectados.

## Autenticación

El MVP opera con flujo anónimo (`AllowAny`). La integración con Keycloak se implementará en una fase posterior.
