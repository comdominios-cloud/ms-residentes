#!/usr/bin/env bash
#
# Carga los datos de prueba en las cuatro bases de produccion.
#
# Se corre en la maquina de base de datos (condominio-db-01). Detecta solo los
# contenedores de PostgreSQL, MySQL y MongoDB, lee de ellos el usuario y la
# contrasena, y ejecuta los cuatro scripts de carga dentro de contenedores
# temporales: no hace falta instalar Python ni Node en la maquina.
#
#   bash cargar-datos-produccion.sh
#
set -uo pipefail

RAIZ="${RAIZ:-$HOME/carga-condominios}"
REPOS=(ms-residentes ms-usuarios ms-pagos ms-incidencias)

rojo()  { printf '\033[31m%s\033[0m\n' "$*"; }
verde() { printf '\033[32m%s\033[0m\n' "$*"; }
info()  { printf '\033[36m==>\033[0m %s\n' "$*"; }

# ---------------------------------------------------------------- comprobar
command -v docker >/dev/null || { rojo "no encuentro docker"; exit 1; }
command -v git    >/dev/null || { rojo "no encuentro git"; exit 1; }

# Busca el contenedor cuya imagen empieza con el nombre del motor.
contenedor_de() {
  docker ps --format '{{.Names}}\t{{.Image}}' \
    | awk -v m="$1" 'tolower($2) ~ "^"m { print $1; exit }'
}

# Lee una variable de entorno de un contenedor en marcha.
env_de() {
  docker inspect "$1" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null \
    | awk -F= -v k="$2" '$1==k { sub(/^[^=]*=/,""); print; exit }'
}

info "Buscando los contenedores de base de datos"
C_PG=$(contenedor_de postgres)
C_MY=$(contenedor_de mysql)
C_MG=$(contenedor_de mongo)

for par in "PostgreSQL:$C_PG" "MySQL:$C_MY" "MongoDB:$C_MG"; do
  motor="${par%%:*}"; nom="${par#*:}"
  if [[ -z "$nom" ]]; then
    rojo "  no encontre un contenedor de $motor en marcha"
  else
    echo "  $motor  ->  $nom"
  fi
done
[[ -z "$C_PG$C_MY$C_MG" ]] && { rojo "No hay ninguna base en marcha. Levantalas primero."; exit 1; }

PG_USER=$(env_de "$C_PG" POSTGRES_USER); PG_PASS=$(env_de "$C_PG" POSTGRES_PASSWORD)
MY_USER=$(env_de "$C_MY" MYSQL_USER);    MY_PASS=$(env_de "$C_MY" MYSQL_PASSWORD)
[[ -z "$MY_USER" ]] && { MY_USER=root; MY_PASS=$(env_de "$C_MY" MYSQL_ROOT_PASSWORD); }

echo
info "Credenciales detectadas"
echo "  PostgreSQL: usuario ${PG_USER:-(no encontrado)}"
echo "  MySQL:      usuario ${MY_USER:-(no encontrado)}"
echo "  MongoDB:    sin autenticacion"
echo
echo "Esto BORRA los datos actuales y carga 20.000 registros en cada base."
read -r -p "Continuar? [s/N] " ok
[[ "${ok,,}" == s ]] || { echo "cancelado"; exit 0; }

# ------------------------------------------------------------------ repos
mkdir -p "$RAIZ" && cd "$RAIZ"
for r in "${REPOS[@]}"; do
  if [[ -d "$r/.git" ]]; then (cd "$r" && git pull -q --ff-only)
  else git clone -q "https://github.com/comdominios-cloud/$r.git"; fi
done
verde "Repositorios al dia"

fallos=0
paso() { echo; info "$1"; }

# --------------------------------------------------- 1 · residentes (PG)
if [[ -n "$C_PG" ]]; then
  paso "PostgreSQL · condominio_residentes"
  docker run --rm --network host -v "$RAIZ/ms-residentes:/app" -w /app python:3.11-slim sh -c \
    "pip install -q faker 'psycopg[binary]' python-dotenv && \
     POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_DB=condominio_residentes \
     POSTGRES_USER='$PG_USER' POSTGRES_PASSWORD='$PG_PASS' \
     python docs/seed_fake_data.py --limpiar" || { rojo "  fallo"; ((fallos++)); }

  paso "PostgreSQL · condominio_usuarios"
  docker run --rm --network host -v "$RAIZ/ms-usuarios:/app" -w /app python:3.11-slim sh -c \
    "pip install -q faker 'psycopg[binary]' python-dotenv bcrypt && \
     POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_DB=condominio_usuarios \
     POSTGRES_USER='$PG_USER' POSTGRES_PASSWORD='$PG_PASS' \
     python docs/seed_fake_data.py --limpiar" || { rojo "  fallo"; ((fallos++)); }

  # El --limpiar borra la cuenta con la que se entra al frontend: la reponemos.
  paso "Restaurando la cuenta de demostracion"
  docker exec -i "$C_PG" psql -U "$PG_USER" -d condominio_usuarios <<'SQL' >/dev/null 2>&1
INSERT INTO usuarios (residente_id, email, password_hash, rol) VALUES
  (NULL, 'admin@condominio.com',
   '$2b$12$k2l7LY/mmNy6g2MddikGjeUoTtWIAkUJ0fgGaEJilFBlkljn12lna', 'ADMIN')
ON CONFLICT (email) DO NOTHING;
SQL
  verde "  admin@condominio.com / condominio123"
fi

# --------------------------------------------------------- 2 · pagos (MySQL)
if [[ -n "$C_MY" ]]; then
  paso "MySQL · condominio_pagos"
  docker run --rm --network host -v "$RAIZ/ms-pagos:/app" -w /app python:3.11-slim sh -c \
    "pip install -q faker pymysql python-dotenv && \
     MYSQL_HOST=localhost MYSQL_PORT=3306 MYSQL_DATABASE=condominio_pagos \
     MYSQL_USER='$MY_USER' MYSQL_PASSWORD='$MY_PASS' \
     python docs/seed_fake_data.py --limpiar" || { rojo "  fallo"; ((fallos++)); }
fi

# --------------------------------------------------- 3 · incidencias (Mongo)
if [[ -n "$C_MG" ]]; then
  paso "MongoDB · condominio_incidencias"
  docker run --rm --network host -v "$RAIZ/ms-incidencias:/app" -w /app node:20-slim sh -c \
    "npm install --silent --no-audit --no-fund @faker-js/faker mongoose dotenv && \
     MONGO_HOST=localhost MONGO_PORT=27017 MONGO_DB=condominio_incidencias \
     node docs/seed_fake_data.js" || { rojo "  fallo"; ((fallos++)); }
fi

# ------------------------------------------------------------------ conteo
echo; info "Conteo final"
[[ -n "$C_PG" ]] && docker exec "$C_PG" psql -U "$PG_USER" -d condominio_residentes -t -c \
  "select 'residentes', count(*) from residentes" 2>/dev/null | sed 's/^/  /'
[[ -n "$C_PG" ]] && docker exec "$C_PG" psql -U "$PG_USER" -d condominio_usuarios -t -c \
  "select 'usuarios', count(*) from usuarios" 2>/dev/null | sed 's/^/  /'
[[ -n "$C_MY" ]] && docker exec "$C_MY" mysql -u"$MY_USER" -p"$MY_PASS" -N -e \
  "select 'pagos', count(*) from condominio_pagos.pagos" 2>/dev/null | sed 's/^/  /'
[[ -n "$C_MG" ]] && docker exec "$C_MG" mongosh --quiet condominio_incidencias --eval \
  'print("  incidencias " + db.incidencias.countDocuments())' 2>/dev/null

echo
if (( fallos )); then rojo "Termino con $fallos error(es)"; exit 1; fi
verde "Listo. Las cuatro bases cargadas."
