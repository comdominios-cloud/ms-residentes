# ms-residentes

Microservicio de **edificios, unidades (departamentos) y residentes** del
Sistema de Administracion de Condominios.

> CS2032 Cloud Computing - UTEC | Proyecto: Sistema de Administracion de Condominios

## Responsable

[@Osomar1705](https://github.com/Osomar1705) — API con base de datos (Python).
Ver [INTEGRANTE.md](INTEGRANTE.md).

> **Camino critico del avance del 50%.** De este microservicio dependen la
> ingesta de @carloscondor1610 (lee su PostgreSQL) y el frontend de @alxgr-08
> (consume su API y su login).

## Dominio

Es la fuente de verdad sobre *quien vive donde*. Administra el catalogo de
edificios, las unidades de cada edificio y las personas asociadas a cada unidad
(propietarios e inquilinos).

Las **cuentas de acceso** (register, login) **no viven aca**: son del
microservicio [ms-usuarios](https://github.com/comdominios-cloud/ms-usuarios),
que tiene su propia base. Esta API solo **verifica** la firma de los tokens que
ese servicio emite, usando el mismo `JWT_SECRET`. No hay llamada HTTP entre los
dos: la verificacion es local.

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
| Autenticacion | verifica JWT emitidos por ms-usuarios |
| Documentacion | Swagger-UI en `/docs`   |
| Contenedor  | Docker                    |

**Tablas relacionadas:** `edificios` -> `unidades` -> `residentes`
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
| ms-usuarios   | 9006      | 8000    |
| web-condominio (dev) | 5173 | —     |

Las bases de datos **no** entran en ese rango: PostgreSQL 5432, MySQL 3306,
MongoDB 27017, alcanzables solo desde los Security Groups de la VM de produccion
y la VM de ingesta.

## Endpoints REST planificados

> Andamiaje: aun no implementados.

| # | Metodo | Ruta | Descripcion | Consumido por |
|---|--------|------|-------------|---------------|
| 1 | `GET`  | `/edificios` | Lista los edificios del condominio | frontend |
| 2 | `GET`  | `/edificios/{edificio_id}` | Detalle de un edificio | frontend |
| 3 | `GET`  | `/unidades?edificio_id=` | Lista unidades, filtrables por edificio | frontend |
| 4 | `GET`  | `/unidades/{unidad_id}` | Detalle de una unidad con su edificio | ms-ficha-residente |
| 5 | `GET`  | `/residentes` | Lista paginada de residentes | **frontend** |
| 6 | `GET`  | `/residentes/{residente_id}` | Detalle de un residente con su unidad | **frontend**, ms-ficha-residente |
| 7 | `POST` | `/residentes` | Registra un residente *(requiere token)* | frontend |
| 8 | `PUT`  | `/residentes/{residente_id}` | Actualiza el residente *(requiere token)* | frontend |
| 9 | `DELETE` | `/residentes/{residente_id}` | Baja logica *(requiere token)* | frontend |
| 10| `GET`  | `/health` | Health check, comprueba tambien la BD | infra |

Las lecturas son **publicas**; las escrituras exigen un token emitido por
`ms-usuarios`.

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
| `JWT_SECRET` | Secreto para **verificar** los tokens. Tiene que ser el mismo que usa ms-usuarios para firmarlos | *(sin valor en el repo)* |
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

El repo trae un [docker-compose.yml](docker-compose.yml) que levanta la API y su
PostgreSQL juntos:

```bash
cp .env.example .env      # completar credenciales
docker compose up -d --build
```

Al arrancar por primera vez, PostgreSQL ejecuta automaticamente
[docs/schema.sql](docs/schema.sql) y [docs/seed_data.sql](docs/seed_data.sql), asi
que la base queda con las tablas creadas y 20 filas de prueba.

| Que | Donde |
|-----|-------|
| API | http://localhost:9001 |
| Swagger-UI | http://localhost:9001/docs |
| PostgreSQL desde tu maquina | `localhost:55432` |

> El puerto **55432** es solo el mapeo hacia el host: se eligio asi porque muchas
> maquinas ya tienen un PostgreSQL del sistema ocupando el 5432. Dentro de la red
> de Docker la API se conecta a `postgres:5432` normalmente.

### Token para los endpoints protegidos

El login vive en `ms-usuarios` (puerto 9006). Para escribir en esta API hay que
pedirle un token a ese servicio:

```bash
curl -X POST http://localhost:9006/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@condominio.com","password":"condominio123"}'
```

y mandarlo aca como `Authorization: Bearer <token>`. Los dos servicios tienen que
compartir el mismo `JWT_SECRET`.

### Comandos utiles

```bash
docker compose logs -f api      # ver los logs de la API
docker compose down             # apagar (la data del volumen se conserva)
docker compose down -v          # apagar Y borrar la data
```

### En la VM de produccion

La imagen esta publicada en Docker Hub:
**[`osomar/ms-residentes`](https://hub.docker.com/r/osomar/ms-residentes)**
(tags `0.2.0` y `latest`).

> **`0.1.0` esta obsoleta**: es anterior a la separacion de `ms-usuarios`, todavia
> incluye los endpoints de auth y el modelo `Usuario`. Desplegada contra el
> esquema actual devuelve 500 al escribir, porque busca una tabla `usuarios` que
> ya no existe en `condominio_residentes`. Usar **`0.2.0`**.

En la VM basta con el archivo [docker-compose.prod.yml](docker-compose.prod.yml)
y un `.env` con la IP privada de la VM de base de datos:

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

No construye nada: baja la imagen ya armada. Las **dos VM de produccion gemelas**
usan el mismo archivo y el mismo tag, asi corren identica version.

Para publicar una version nueva de la imagen:

```bash
docker build -t osomar/ms-residentes:0.2.0 .
docker push osomar/ms-residentes:0.2.0
```

> El [.dockerignore](.dockerignore) deja el `.env` fuera de la imagen. Sin el,
> las credenciales viajarian dentro de la imagen publicada.

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
├── routers/      # endpoints por recurso (edificios, unidades, residentes)
├── models/       # modelos SQLAlchemy
├── schemas/      # esquemas Pydantic
├── config.py     # lee y valida las variables de entorno
├── security/     # verificacion de los JWT que emite ms-usuarios
└── db/           # sesion y conexion a PostgreSQL
docs/
├── der.md              # diagrama entidad-relacion (placeholder)
├── schema.sql          # DDL inicial (PostgreSQL)
├── seed_data.sql       # 20 filas de prueba para el avance
└── seed_fake_data.py   # carga masiva de 20,000 registros (placeholder)
tests/
postman/
└── ms-residentes.postman_collection.json   # 23 requests para la demo
```

## Despliegue en AWS

Paso a paso en [DESPLIEGUE.md](DESPLIEGUE.md): crear la base en la VM de base de
datos, armar el `.env` en la VM de produccion y levantar los contenedores desde
Docker Hub.

## Verificar el despliegue

[scripts/verificar-despliegue.sh](scripts/verificar-despliegue.sh) comprueba en
unos segundos toda la cadena: el balanceador, los 6 microservicios con su base,
la emision del token en ms-usuarios y que ms-residentes lo acepte, el frontend
en Amplify y el proxy `/api/`.

```bash
./scripts/verificar-despliegue.sh
```

Cada falla dice de quien depende. **Correrlo antes de la asesoria**: las
instancias se apagan solas y el ALB pasa a 503 sin aviso.

La prueba del token no inserta datos: intenta crear un residente con un documento
que ya existe en el seed, asi la respuesta esperada es `409`. Si devuelve `401`,
el `JWT_SECRET` no coincide entre los dos `.env`.

## Estado

**Funcionando en local.** Endpoints de edificios, unidades y residentes sobre
PostgreSQL, con datos de prueba cargados y las escrituras protegidas con los
tokens de ms-usuarios.

Pendiente: desplegar en la VM de produccion de AWS y publicar la imagen en
Docker Hub.
