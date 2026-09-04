# ms-residentes

Microservicio de **edificios, unidades (departamentos) y residentes/propietarios**
del Sistema de Administracion de Condominios.

> CS2032 Cloud Computing - UTEC | Proyecto: Sistema de Administracion de Condominios

## Responsable

Integrante a cargo de **API con BD #1**. Este repositorio es **autonomo**: se
desarrolla, prueba y despliega sin depender del avance de los demas
microservicios.

## Dominio

Es la fuente de verdad sobre *quien vive donde*. Administra el catalogo de
edificios del condominio, las unidades que contiene cada edificio y las
personas asociadas a cada unidad (propietarios e inquilinos).

Este microservicio **no llama** a ningun otro. Es consumido por
**ms-ficha-residente**, que es el consumidor de APIs del proyecto y arma la
ficha consolidada del residente.

```
web-condominio ──> API Gateway ──> ms-residentes ──> MySQL
                                        ^
                                        └── ms-ficha-residente (consume esta API)
```

## Stack

| Elemento    | Tecnologia                |
|-------------|---------------------------|
| Lenguaje    | Python 3.12               |
| Framework   | FastAPI                   |
| Base de datos | MySQL 8 (SQL)           |
| ORM         | SQLAlchemy                |
| Documentacion | Swagger-UI en `/docs`   |
| Contenedor  | Docker                    |

**Tablas relacionadas:** `edificios` -> `unidades` -> `residentes`
(la relacion exigida por el curso es **unidades <- residentes**).
Ver [docs/schema.sql](docs/schema.sql) y [docs/der.md](docs/der.md).

## Puerto asignado

**8001**

| Microservicio       | Puerto |
|---------------------|--------|
| ms-residentes       | **8001** |
| ms-pagos            | 8002   |
| ms-incidencias      | 8003   |
| ms-ficha-residente  | 8004   |
| ms-analitico        | 8005   |
| web-condominio (dev)| 5173   |

## Endpoints REST planificados

> Andamiaje: aun no implementados.

| # | Metodo | Ruta | Descripcion | Consumido por |
|---|--------|------|-------------|---------------|
| 1 | `GET`  | `/edificios` | Lista los edificios del condominio | frontend |
| 2 | `GET`  | `/unidades?edificio_id=` | Lista unidades, filtrables por edificio | frontend |
| 3 | `GET`  | `/unidades/{unidad_id}` | Detalle de una unidad | ms-ficha-residente |
| 4 | `GET`  | `/residentes` | Lista paginada de residentes | **frontend** |
| 5 | `GET`  | `/residentes/{residente_id}` | Detalle de un residente con su unidad | **frontend**, ms-ficha-residente |
| 6 | `POST` | `/residentes` | Registra un nuevo residente en una unidad | frontend |
| 7 | `PUT`  | `/residentes/{residente_id}` | Actualiza datos del residente | frontend |
| 8 | `DELETE` | `/residentes/{residente_id}` | Da de baja a un residente | frontend |
| 9 | `GET`  | `/health` | Health check del servicio | infra |

Los dos endpoints que consume directamente el **frontend** son
`GET /residentes` y `GET /residentes/{residente_id}`.

Documentacion interactiva: `http://localhost:8001/docs` (Swagger-UI).

## Variables de entorno

Copiar [.env.example](.env.example) a `.env` y completar. **Nunca** commitear `.env`.

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| `APP_NAME` | Nombre del servicio | `ms-residentes` |
| `APP_PORT` | Puerto de escucha | `8001` |
| `APP_ENV` | Entorno de ejecucion | `development` / `production` |
| `LOG_LEVEL` | Nivel de logging | `info` |
| `MYSQL_HOST` | Host de MySQL | `mysql` (nombre del servicio en Compose) |
| `MYSQL_PORT` | Puerto de MySQL | `3306` |
| `MYSQL_DATABASE` | Nombre de la base | `condominio_residentes` |
| `MYSQL_USER` | Usuario de la base | *(sin valor en el repo)* |
| `MYSQL_PASSWORD` | Password del usuario | *(sin valor en el repo)* |
| `MYSQL_ROOT_PASSWORD` | Password de root (solo local) | *(sin valor en el repo)* |
| `DATABASE_URL` | Cadena de conexion completa | `mysql+pymysql://user:pass@mysql:3306/condominio_residentes` |

## Como levantar con Docker

### Solo el microservicio

```bash
cp .env.example .env      # completar credenciales
docker build -t ms-residentes .
docker run --rm -p 8001:8001 --env-file .env ms-residentes
```

Luego abrir `http://localhost:8001/docs`.

### Con MySQL incluido (docker compose)

En el despliegue final este servicio se levanta junto a su MySQL desde el
`docker-compose.yml` de la instancia EC2. Ejemplo minimo:

```yaml
services:
  mysql:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
    ports: ["3306:3306"]
    volumes:
      - mysql_data:/var/lib/mysql
      - ./docs/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql

  ms-residentes:
    build: .
    ports: ["8001:8001"]
    env_file: .env
    depends_on: [mysql]

volumes:
  mysql_data:
```

```bash
docker compose up --build
```

## Estructura

```
app/
├── main.py       # instancia FastAPI (stub)
├── routers/      # endpoints por recurso
├── models/       # modelos SQLAlchemy
├── schemas/      # esquemas Pydantic
└── db/           # sesion y conexion a MySQL
docs/
├── der.md              # diagrama entidad-relacion (placeholder)
├── schema.sql          # DDL inicial
└── seed_fake_data.py   # carga masiva de 20,000 registros (placeholder)
tests/
```

## Estado

Andamiaje inicial. Sin endpoints ni logica de negocio implementados.
