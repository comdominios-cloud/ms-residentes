# ms-residentes

Microservicio de **edificios, unidades (departamentos), residentes y usuarios**
del Sistema de Administracion de Condominios.

> CS2032 Cloud Computing - UTEC | Proyecto: Sistema de Administracion de Condominios

## Responsable

[@Osomar1705](https://github.com/Osomar1705) — API con base de datos (Python).
Ver [INTEGRANTE.md](INTEGRANTE.md).

> **Camino critico del avance del 50%.** De este microservicio dependen la
> ingesta de @carloscondor1610 (lee su PostgreSQL) y el frontend de @alxgr-08
> (consume su API y su login).

## Dominio

Es la fuente de verdad sobre *quien vive donde* y *quien puede entrar al
sistema*. Administra el catalogo de edificios, las unidades de cada edificio,
las personas asociadas a cada unidad (propietarios e inquilinos) y las **cuentas
de usuario**: register, login, alta y baja.

Este microservicio **no llama** a ningun otro. Es consumido por
**ms-ficha-residente**, que es el consumidor de APIs del proyecto.

```
web-condominio ──> balanceador ──> ms-residentes :9001 ──> PostgreSQL :5432
                                         ^                 (VM de base de datos)
                                         ├── ms-ficha-residente (consume esta API)
                                         └── ingesta01 (lee la BD y la vuelca a S3)
```

## Stack

| Elemento    | Tecnologia                |
|-------------|---------------------------|
| Lenguaje    | Python 3.12               |
| Framework   | FastAPI                   |
| Base de datos | **PostgreSQL 16** (SQL) |
| ORM         | SQLAlchemy + psycopg      |
| Autenticacion | passlib (hash) + JWT    |
| Documentacion | Swagger-UI en `/docs`   |
| Contenedor  | Docker                    |

**Tablas relacionadas:** `edificios` -> `unidades` -> `residentes` -> `usuarios`
(la relacion exigida por el curso es **unidades <- residentes**).
Ver [docs/schema.sql](docs/schema.sql) y [docs/der.md](docs/der.md).

## Puerto asignado

**9001** publicado · **8000** dentro del contenedor.

El curso asigno el rango **9000-12000** para los microservicios; ese es el puerto
que se habilita en el Security Group.

| Microservicio | Publicado | Interno |
|---------------|-----------|---------|
| ms-residentes | **9001**  | 8000    |
| ms-pagos      | 9002      | 8080    |
| ms-incidencias| 9003      | 3003    |
| ms-ficha-residente | 9004 | 8004    |
| ms-analitico  | 9005      | 8005    |
| web-condominio (dev) | 5173 | —     |

Las bases de datos **no** entran en ese rango: PostgreSQL 5432, MySQL 3306,
MongoDB 27017, alcanzables solo desde los Security Groups de la VM de produccion
y la VM de ingesta.

## Endpoints REST planificados

> Andamiaje: aun no implementados.

### Usuarios (pedido explicito del ACL)

| # | Metodo | Ruta | Descripcion | Consumido por |
|---|--------|------|-------------|---------------|
| 1 | `POST` | `/auth/register` | Registra una cuenta nueva | **frontend** |
| 2 | `POST` | `/auth/login` | Autentica y devuelve el token | **frontend** |
| 3 | `GET`  | `/usuarios` | Lista de cuentas | frontend |
| 4 | `POST` | `/usuarios` | Crea una cuenta (admin) | frontend |
| 5 | `DELETE` | `/usuarios/{usuario_id}` | Elimina/desactiva una cuenta | frontend |

### Residentes y unidades

| # | Metodo | Ruta | Descripcion | Consumido por |
|---|--------|------|-------------|---------------|
| 6 | `GET`  | `/edificios` | Lista los edificios del condominio | frontend |
| 7 | `GET`  | `/unidades?edificio_id=` | Lista unidades, filtrables por edificio | frontend |
| 8 | `GET`  | `/unidades/{unidad_id}` | Detalle de una unidad | ms-ficha-residente |
| 9 | `GET`  | `/residentes` | Lista paginada de residentes | **frontend** |
| 10| `GET`  | `/residentes/{residente_id}` | Detalle de un residente con su unidad | **frontend**, ms-ficha-residente |
| 11| `POST` | `/residentes` | Registra un nuevo residente en una unidad | frontend |
| 12| `PUT`  | `/residentes/{residente_id}` | Actualiza datos del residente | frontend |
| 13| `DELETE` | `/residentes/{residente_id}` | Da de baja a un residente | frontend |
| 14| `GET`  | `/health` | Health check del servicio | infra |

Documentacion interactiva: `http://<ip-vm-produccion>:9001/docs` (Swagger-UI).

## Variables de entorno

Copiar [.env.example](.env.example) a `.env` y completar. **Nunca** commitear `.env`.

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| `APP_NAME` | Nombre del servicio | `ms-residentes` |
| `APP_PORT` | Puerto dentro del contenedor | `8000` |
| `PUBLISHED_PORT` | Puerto publicado en la VM | `9001` |
| `APP_ENV` | Entorno de ejecucion | `development` / `production` |
| `LOG_LEVEL` | Nivel de logging | `info` |
| `POSTGRES_HOST` | IP privada de la VM de base de datos | *(sin valor en el repo)* |
| `POSTGRES_PORT` | Puerto de PostgreSQL | `5432` |
| `POSTGRES_DB` | Nombre de la base | `condominio_residentes` |
| `POSTGRES_USER` | Usuario de la base | *(sin valor en el repo)* |
| `POSTGRES_PASSWORD` | Password del usuario | *(sin valor en el repo)* |
| `DATABASE_URL` | Cadena de conexion completa | `postgresql+psycopg://user:pass@host:5432/condominio_residentes` |
| `JWT_SECRET` | Secreto para firmar el token | *(sin valor en el repo)* |
| `JWT_ALGORITHM` | Algoritmo de firma | `HS256` |
| `JWT_EXPIRE_MINUTES` | Vigencia del token | `60` |

## Como levantar con Docker

### Solo el microservicio

```bash
cp .env.example .env      # completar credenciales
docker build -t ms-residentes .
docker run --rm -p 9001:8000 --env-file .env ms-residentes
```

Luego abrir `http://localhost:9001/docs`.

### Con PostgreSQL incluido (desarrollo local)

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports: ["5432:5432"]
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./docs/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql

  ms-residentes:
    build: .
    ports: ["9001:8000"]
    env_file: .env
    depends_on: [postgres]

volumes:
  pg_data:
```

```bash
docker compose up --build
```

### En AWS

PostgreSQL corre como contenedor en la **VM de base de datos** (una de los 3
contenedores de esa maquina) y el microservicio en la **VM de produccion**, asi
que `POSTGRES_HOST` apunta a la **IP privada** de la VM de base de datos, no a
`localhost`.

La imagen se publica en **Docker Hub** para que las 2 VM de produccion gemelas
hagan `pull` de la misma version:

```bash
docker build -t <usuario>/ms-residentes:0.1.0 .
docker push <usuario>/ms-residentes:0.1.0
```

## Estructura

```
app/
├── main.py       # instancia FastAPI (stub)
├── routers/      # endpoints por recurso (auth, usuarios, residentes, unidades)
├── models/       # modelos SQLAlchemy
├── schemas/      # esquemas Pydantic
├── security/     # hash de passwords y emision/validacion de JWT
└── db/           # sesion y conexion a PostgreSQL
docs/
├── der.md              # diagrama entidad-relacion (placeholder)
├── schema.sql          # DDL inicial (PostgreSQL)
└── seed_fake_data.py   # carga masiva de 20,000 registros (placeholder)
tests/
```

## Estado

Andamiaje inicial. Sin endpoints ni logica de negocio implementados.
