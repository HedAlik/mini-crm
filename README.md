# Mini CRM · Seguimiento de solicitudes

API REST para registrar clientes y dar seguimiento a sus solicitudes (estados `pendiente`, `en_proceso`, `resuelta`), con una pantalla web simple para listar solicitudes y cambiar su estado.

**Stack:** Python 3.12+ · Flask 3 · SQLite · pytest · Docker · GitHub Actions

## Requisitos

- Python 3.11 o superior (probado con 3.12 y 3.13)
- (Opcional) Docker y Docker Compose

## Instalación y ejecución local

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt   # app + pytest (la imagen Docker solo instala requirements.txt)

python scripts/init_db.py          # crea data/crm.db y aplica migraciones (--seed para datos de ejemplo)
python -m flask --app app:create_app run --port 8000
```

- API: <http://localhost:8000>
- Interfaz: <http://localhost:8000/>

> La app también aplica las migraciones pendientes al arrancar, así que `init_db.py` es opcional.

### Con Docker

```bash
docker compose up --build
# luego: http://localhost:8000
```

La base de datos se guarda en el volumen `crm-data`, así que sobrevive a reinicios del contenedor.

### Pruebas

```bash
python -m pytest -v
```

Cada prueba usa una base de datos temporal aislada (`tmp_path`), así que no ensucia `data/`.

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `DATABASE_PATH` | `data/crm.db` | Ruta del archivo SQLite |

No hay credenciales ni secretos. `.env` está en `.gitignore`; ver `.env.example`.

## Modelo de datos

```
clientes (1) ────< (N) solicitudes
```

| Tabla | Columnas | Restricciones |
|---|---|---|
| `clientes` | `id`, `nombre`, `email`, `creado_en` | PK `id`; `email` UNIQUE; `nombre` no vacío |
| `solicitudes` | `id`, `cliente_id`, `descripcion`, `estado`, `creado_en`, `actualizado_en` | PK `id`; FK `cliente_id → clientes.id` (ON DELETE RESTRICT); `CHECK estado IN (...)`; índices en `cliente_id` y `estado` |

Migración: [`migrations/001_init.sql`](migrations/001_init.sql). Las migraciones aplicadas se registran en la tabla `schema_migrations`, así que ejecutar el script dos veces es seguro.

## Endpoints

Todas las respuestas son JSON. Los errores tienen la forma `{"error": "...", "detalles": {"campo": "motivo"}}`.

| Método | Ruta | Descripción | Éxito | Errores |
|---|---|---|---|---|
| GET | `/health` | Estado del servicio | 200 | — |
| POST | `/clientes` | Crear cliente | 201 | 400, 409, 422 |
| GET | `/clientes` | Listar clientes | 200 | — |
| POST | `/solicitudes` | Crear solicitud | 201 | 400, 422 |
| GET | `/solicitudes` | Listar solicitudes (filtros opcionales `?estado=` y `?cliente_id=`) | 200 | 422 |
| PATCH | `/solicitudes/{id}/estado` | Cambiar estado | 200 | 400, 404, 422 |

**Criterio de códigos HTTP**

- `400` el cuerpo no es un objeto JSON.
- `422` el JSON es válido pero los datos no (campo faltante, estado inválido, cliente inexistente).
- `404` el recurso de la URL no existe (`/solicitudes/999/estado`).
- `409` conflicto con datos existentes (email duplicado).

### Ejemplos de peticiones

```bash
# Crear cliente
curl -X POST localhost:8000/clientes -H 'Content-Type: application/json' \
  -d '{"nombre":"Ana Prueba","email":"ana@example.com"}'
# 201 → {"id":1,"nombre":"Ana Prueba","email":"ana@example.com","creado_en":"..."}

# Crear solicitud (estado por defecto: pendiente)
curl -X POST localhost:8000/solicitudes -H 'Content-Type: application/json' \
  -d '{"cliente_id":1,"descripcion":"No llega mi factura"}'
# 201

# Cliente inexistente
curl -X POST localhost:8000/solicitudes -H 'Content-Type: application/json' \
  -d '{"cliente_id":999,"descripcion":"x"}'
# 422 → {"error":"Datos inválidos","detalles":{"cliente_id":"el cliente no existe"}}

# Cambiar estado
curl -X PATCH localhost:8000/solicitudes/1/estado -H 'Content-Type: application/json' \
  -d '{"estado":"en_proceso"}'
# 200

# Estado inválido
curl -X PATCH localhost:8000/solicitudes/1/estado -H 'Content-Type: application/json' \
  -d '{"estado":"cerrada"}'
# 422 → {"error":"Datos inválidos","detalles":{"estado":"debe ser uno de: pendiente, en_proceso, resuelta"}}

# Listar con filtro
curl 'localhost:8000/solicitudes?estado=en_proceso'
```

La salida real de estas peticiones está en [`evidencia/curl.md`](evidencia/curl.md).

## Estructura

```
app/
  __init__.py      fábrica create_app, manejadores de error, ruta de la UI
  db.py            conexión SQLite (FK activadas) y runner de migraciones
  routes.py        endpoints
  validation.py    reglas de validación de entrada
  static/index.html  interfaz (HTML + JS sin dependencias)
migrations/001_init.sql
scripts/init_db.py
tests/test_api.py
requirements.txt · requirements-dev.txt
evidencia/         salida de pytest, curl y captura de la UI
Dockerfile · docker-compose.yml · .github/workflows/ci.yml
```

## Decisiones técnicas

- **Flask en lugar de FastAPI.** Ambos estaban sugeridos. Elegí Flask porque es el que tenía disponible y probado en mi entorno; con el alcance del ejercicio la validación manual es corta y explícita. Con más tiempo, FastAPI + Pydantic daría validación y documentación OpenAPI automáticas.
- **SQLite con `sqlite3` de la biblioteca estándar, sin ORM.** Para dos tablas, SQL directo es más fácil de leer y de explicar. Todas las consultas están parametrizadas (`?`), así que no hay inyección SQL. El único SQL dinámico es el `WHERE` de los filtros, y solo concatena fragmentos fijos; los valores siempre van como parámetros.
- **Validación en dos capas.** La API valida y devuelve mensajes claros por campo. Además, la base de datos impone FK y `CHECK` como segunda defensa, por si alguien escribe directo en la BD o hay un bug en la API (hay una prueba específica para esto).
- **`PRAGMA foreign_keys = ON` en cada conexión.** SQLite **no** aplica las llaves foráneas por defecto; sin esto, la FK estaría declarada pero no se cumpliría.
- **Ruta específica para el estado** (`PATCH /solicitudes/{id}/estado`): el único cambio permitido es el de estado, y la ruta lo deja explícito.
- **Email normalizado a minúsculas** para que `Ana@x.com` y `ana@x.com` no cuenten como clientes distintos.
- **`cliente_id: true` se rechaza**: en Python `bool` es subclase de `int` y `True == 1`, lo que habría permitido asignar la solicitud al cliente 1.
- **Los ids se acotan al rango de SQLite** (máximo 2⁶³−1). Python acepta enteros de cualquier tamaño, pero SQLite lanza `OverflowError` con uno mayor, lo que devolvía un 500. Ahora un id fuera de rango responde 422 (en el cuerpo o en `?cliente_id=`) o 404 (en la URL). El filtro `?cliente_id=` solo acepta dígitos ASCII, porque `"²".isdigit()` es `True` pero `int("²")` falla.
- **Dependencias separadas:** `requirements.txt` (solo la app, lo que instala Docker) y `requirements-dev.txt` (añade pytest, para desarrollo y CI).
- **La interfaz usa `textContent`**, no `innerHTML`, para que el texto del usuario no se interprete como HTML (evita XSS). Comprobado con la descripción `<b>Cambio de plan</b>` (ver `evidencia/ui.png`).
- **Los errores 500 no exponen trazas** al cliente.
- **Docker** usa un usuario sin privilegios y un volumen para persistir la BD.

## Pruebas

18 pruebas en [`tests/test_api.py`](tests/test_api.py):

- **Camino exitoso:** flujo completo (crear cliente → crear solicitud → cambiar estado → listar); listado y filtros.
- **Errores:** cliente inexistente (422), estado inválido al crear y al actualizar (422, y el estado original se conserva), solicitud inexistente (404), email duplicado (409), datos de cliente inválidos (422 ×3), cuerpo no JSON (400), `cliente_id` booleano (422).
- **Integridad en la BD:** SQLite rechaza FK y estados inválidos aunque no se pase por la API.
- **Regresiones:** ids fuera del rango de SQLite o con dígitos no ASCII responden 422/404 en lugar de 500 (×4); `init_db.py --seed` ejecutado dos veces no duplica datos.

Salida real: [`evidencia/pytest.md`](evidencia/pytest.md).

## Depuración (tarea 4)

> Completar durante la sesión con el fallo que entregue el entrevistador.

- **Síntoma / cómo reproducirlo:**
- **Causa raíz:**
- **Corrección (commit):**
- **Prueba de regresión añadida:**

## Uso de IA

**Herramienta:** Claude (Anthropic), modelo Claude Opus 5.5, en modo agente: generó el código y lo ejecutó en un entorno aislado.

**Prompts representativos**

1. *«Necesito un plan y que realices específicamente lo que hace el siguiente PDF»* (adjuntando el enunciado de la evaluación).
2. *(Completa con tus propios prompts de seguimiento, por ejemplo:)* «Explícame por qué la validación de `cliente_id` excluye `bool`».
3. *(Ej.:)* «Agrega una prueba que reproduzca el fallo X antes de corregirlo».

**Qué acepté**

- *(Edita según tu revisión.)* La estructura del proyecto, el esquema SQL con FK y `CHECK`, y el criterio 400/404/409/422.

**Qué modifiqué o decidí**

- Se usó Flask en lugar de FastAPI porque FastAPI no estaba instalado en el entorno de la IA y no se podía instalar. Preferí una solución verificada a una sin ejecutar.
- Corregí `.dockerignore` al probar Docker en mi equipo: no excluía `.venv`, y patrones como `__pycache__` solo aplicaban a la raíz (en `.dockerignore` las rutas son relativas a la raíz del contexto). Los cambié a `.venv`, `**/__pycache__`, `**/.pytest_cache` y `**/*.db`; el contexto de build quedó en ~16 KB.
- En una revisión del código encontré que ids enormes (`10**20`) o con dígitos no ASCII (`²`) provocaban un error 500. Primero escribí pruebas que lo reproducían (fallaban), luego acoté los ids al rango de SQLite y validé el filtro con dígitos ASCII. En la misma revisión hice idempotente el `--seed` y separé `requirements-dev.txt`.
- *(Añade aquí lo que cambies tú.)*

**Cómo verifiqué**

- Ejecuté `pytest` (13/13 en verde; 18/18 tras añadir las pruebas de regresión) → `evidencia/pytest.md`.
- Levanté el servidor real y probé cada endpoint con `curl`, incluidos los casos de error → `evidencia/curl.md`.
- Probé la interfaz en un navegador headless (crear cliente, crear solicitud, cambiar estado, inyección de HTML) → `evidencia/ui.png`.
- Ejecuté `init_db.py` dos veces para confirmar que las migraciones son idempotentes.
- Levanté el proyecto con `docker compose up --build` (Docker Desktop 29.9 sobre WSL 2, Windows 11): el contenedor queda `healthy`, `/health` y la interfaz responden, se puede crear un cliente (el usuario sin privilegios escribe en el volumen) y los datos persisten tras `docker compose down` + `up`.
- Subí el repositorio a GitHub ([HedAlik/mini-crm](https://github.com/HedAlik/mini-crm)): el workflow de CI pasa en verde (pruebas + build de la imagen Docker), ver la pestaña **Actions**.
- Revisé el código línea por línea para poder explicarlo en la revisión.

## Limitaciones y siguientes pasos

- Se usa el servidor de desarrollo de Flask; en producción iría detrás de `gunicorn`.
- Sin autenticación ni autorización (fuera del alcance del ejercicio).
- Sin paginación en los listados.
- No se restringen las transiciones de estado (por ejemplo, de `resuelta` a `pendiente`); se podría añadir una máquina de estados si el negocio lo requiere.
- SQLite es suficiente para la prueba; para concurrencia real migraría a PostgreSQL (el SQL es casi el mismo, solo cambian `AUTOINCREMENT`→`SERIAL`/`IDENTITY` y `datetime('now')`→`now()`).
