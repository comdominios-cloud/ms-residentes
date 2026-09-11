# Despliegue en AWS

Guia para poner `ms-residentes` (9001) y `ms-usuarios` (9006) a correr en la VM
de produccion, con sus bases en la VM de base de datos.

> Infraestructura creada por [@Brisseth-raton](https://github.com/Brisseth-raton).
> Datos de referencia: VM de base de datos en la IP privada `172.31.30.16`,
> contenedor de PostgreSQL `condominio-postgres`.

---

## Antes de empezar

Necesitas de @Brisseth-raton:

1. La llave **`vockey.pem`** para entrar por SSH a las maquinas.
2. El **usuario y password** del contenedor `condominio-postgres`.
3. Que agregue en el ALB un **target group por puerto** (9001 y 9006) con sus
   reglas de ruta. Sin eso, los microservicios corren pero nadie puede llegar
   desde afuera: el Security Group solo acepta trafico del balanceador.

---

## Paso 1 — Crear las bases de datos

Las dos bases viven dentro del contenedor de PostgreSQL que ya existe. **No** se
crea un contenedor nuevo: asi se mantienen los 3 motores que pidio el ACL.

Entrar por SSH a la VM de base de datos y ejecutar:

```bash
# Crear las dos bases
docker exec -i condominio-postgres psql -U <usuario> -c "CREATE DATABASE condominio_residentes;"
docker exec -i condominio-postgres psql -U <usuario> -c "CREATE DATABASE condominio_usuarios;"
```

Copiar los archivos de esquema y datos desde tu maquina:

```bash
scp -i vockey.pem ms-residentes/docs/schema.sql    ubuntu@<ip-publica-db>:~/residentes-schema.sql
scp -i vockey.pem ms-residentes/docs/seed_data.sql ubuntu@<ip-publica-db>:~/residentes-seed.sql
scp -i vockey.pem ms-usuarios/docs/schema.sql      ubuntu@<ip-publica-db>:~/usuarios-schema.sql
scp -i vockey.pem ms-usuarios/docs/seed_data.sql   ubuntu@<ip-publica-db>:~/usuarios-seed.sql
```

Y cargarlos, respetando el orden (primero el esquema, despues los datos):

```bash
docker exec -i condominio-postgres psql -U <usuario> -d condominio_residentes < residentes-schema.sql
docker exec -i condominio-postgres psql -U <usuario> -d condominio_residentes < residentes-seed.sql
docker exec -i condominio-postgres psql -U <usuario> -d condominio_usuarios   < usuarios-schema.sql
docker exec -i condominio-postgres psql -U <usuario> -d condominio_usuarios   < usuarios-seed.sql
```

Comprobar que quedaron cargadas:

```bash
docker exec -i condominio-postgres psql -U <usuario> -d condominio_residentes -c "SELECT COUNT(*) FROM residentes;"   # 8
docker exec -i condominio-postgres psql -U <usuario> -d condominio_usuarios   -c "SELECT COUNT(*) FROM usuarios;"     # 4
```

---

## Paso 2 — Generar el secreto de los tokens

**En la VM de produccion**, no en tu maquina y nunca en el repositorio:

```bash
openssl rand -hex 32
```

Guardar ese valor: va a ir en los **dos** `.env`. Si no coincide entre los dos
servicios, `ms-usuarios` firmara tokens que `ms-residentes` va a rechazar.

---

## Paso 3 — Crear los `.env` en la VM de produccion

Estos archivos se escriben directamente en la maquina. **No** se suben a GitHub
ni viajan dentro de la imagen de Docker: la imagen es generica y la configuracion
es lo que la vuelve "este servicio en esta maquina".

```bash
mkdir -p ~/condominio && cd ~/condominio
```

`~/condominio/ms-residentes.env`:

```bash
cat > ms-residentes.env <<'ENV'
APP_NAME=ms-residentes
APP_PORT=8000
PUBLISHED_PORT=9001
APP_ENV=production
LOG_LEVEL=info

POSTGRES_HOST=172.31.30.16
POSTGRES_PORT=5432
POSTGRES_DB=condominio_residentes
POSTGRES_USER=<usuario>
POSTGRES_PASSWORD=<password>

JWT_SECRET=<el valor generado en el paso 2>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
ENV
```

`~/condominio/ms-usuarios.env`:

```bash
cat > ms-usuarios.env <<'ENV'
APP_NAME=ms-usuarios
APP_PORT=8000
PUBLISHED_PORT=9006
APP_ENV=production
LOG_LEVEL=info

POSTGRES_HOST=172.31.30.16
POSTGRES_PORT=5432
POSTGRES_DB=condominio_usuarios
POSTGRES_USER=<usuario>
POSTGRES_PASSWORD=<password>

JWT_SECRET=<EL MISMO valor del paso 2>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
ENV
```

Restringir los permisos, para que solo el dueno pueda leerlos:

```bash
chmod 600 ms-residentes.env ms-usuarios.env
```

> `POSTGRES_HOST` es la **IP privada** de la VM de base de datos. No se usa la
> publica: el trafico viaja por dentro de la VPC, que es mas rapido y no sale a
> Internet. El Security Group solo permite el 5432 desde el SG de produccion.

---

## Paso 4 — Levantar los contenedores

`~/condominio/docker-compose.yml`:

```yaml
services:
  ms-residentes:
    image: osomar/ms-residentes:0.2.0
    container_name: ms-residentes
    ports:
      - "9001:8000"
    env_file: ms-residentes.env
    restart: unless-stopped

  ms-usuarios:
    image: osomar/ms-usuarios:0.1.0
    container_name: ms-usuarios
    ports:
      - "9006:8000"
    env_file: ms-usuarios.env
    restart: unless-stopped
```

```bash
docker compose pull
docker compose up -d
docker compose ps
```

No construye nada: baja las imagenes ya publicadas en Docker Hub. Este mismo
procedimiento se repite **igual en las dos VM de produccion gemelas**.

---

## Paso 5 — Comprobar

Desde la propia VM de produccion:

```bash
curl http://localhost:9001/health
curl http://localhost:9006/health
```

Las dos tienen que responder `"database":"ok"`. Si dicen `"error"`, el problema
esta entre la VM y la base: revisar `POSTGRES_HOST`, las credenciales o la regla
del Security Group para el 5432.

Prueba del token entre los dos servicios:

```bash
TOKEN=$(curl -s -X POST http://localhost:9006/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@condominio.com","password":"condominio123"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:9001/residentes \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"unidad_id":3,"nombres":"Prueba","apellidos":"Despliegue","documento":"70000001"}'
```

Tiene que devolver **201**: el token que emitio `ms-usuarios` fue aceptado por
`ms-residentes` sin que los servicios se llamen entre si.

---

## Paso 6 — Acceso desde afuera

Con el Security Group actual, los puertos 9001 y 9006 **solo aceptan trafico del
balanceador**. Para llegar desde Postman o desde el frontend hace falta que el
ALB tenga un target group por puerto con sus reglas de ruta.

Una vez configurado, en la coleccion de Postman se cambian las variables:

| Variable | Valor |
|----------|-------|
| `base_url` | `http://alb-condominio-678852222.us-east-1.elb.amazonaws.com` |
| `usuarios_url` | la misma, con la ruta que enrute al 9006 |

No hay que tocar los requests uno por uno: todos usan esas variables.

---

## Recordatorio de seguridad

- El `.env` **nunca** se commitea ni entra en la imagen (lo evita el `.dockerignore`).
- El `JWT_SECRET` de produccion tiene que ser **distinto** al de desarrollo.
- La password de PostgreSQL en produccion no puede ser la de desarrollo.
- Los usuarios de prueba traen la password `condominio123`: sirve para la demo,
  no para nada real.
