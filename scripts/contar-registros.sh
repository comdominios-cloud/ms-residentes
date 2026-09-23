#!/usr/bin/env bash
# ============================================================
# Conteo de registros en las cuatro bases de datos
# ============================================================
#   APIGW=https://xxxxx.execute-api.us-east-1.amazonaws.com ./scripts/contar-registros.sh
#
# Dos formas de contar, segun como responda cada microservicio:
#
#  - ms-residentes pagina. Preguntar "existe el registro N?" con
#    limit=1&offset=N devuelve una respuesta minuscula, asi que se localiza
#    el total por busqueda binaria en unas quince peticiones.
#
#  - ms-pagos y ms-incidencias devuelven la coleccion completa. Ahi no queda
#    mas que descargarla, y son varios MB, asi que las cuatro descargas se
#    lanzan a la vez en vez de una detras de otra.
# ============================================================
set -uo pipefail

APIGW="${APIGW:-}"
[ -z "$APIGW" ] && { echo "Falta APIGW=https://xxxxx.execute-api.us-east-1.amazonaws.com" >&2; exit 2; }

verde=$'\e[32m'; gris=$'\e[90m'; fin=$'\e[0m'
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT

# Cuenta los elementos de una lista JSON leyendo del flujo, sin cargarla entera.
largo () { python3 -c 'import sys,json
try:
    d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else 0)
except Exception: print(0)'; }

hay_en () { [ "$(curl -s -m 15 "$APIGW$1?limit=1&offset=$2" | largo)" -gt 0 ]; }

# Busca el total sin descargar la coleccion: duplica hasta pasarse y afina.
contar_binario () {
  local ruta="$1" bajo=0 alto=1 medio
  hay_en "$ruta" 0 || { echo 0; return; }
  while hay_en "$ruta" "$alto"; do bajo=$alto; alto=$(( alto * 2 )); done
  while [ $(( alto - bajo )) -gt 1 ]; do
    medio=$(( (bajo + alto) / 2 ))
    if hay_en "$ruta" "$medio"; then bajo=$medio; else alto=$medio; fi
  done
  echo "$(( bajo + 1 ))"
}

contar_directo () { curl -s -m 120 "$APIGW$1" | largo; }

echo "  contando..." >&2
contar_binario /unidades    > "$TMP/unidades"    &
contar_binario /residentes  > "$TMP/residentes"  &
contar_directo /edificios   > "$TMP/edificios"   &
contar_directo /cuotas      > "$TMP/cuotas"      &
contar_directo /pagos       > "$TMP/pagos"       &
contar_directo /incidencias > "$TMP/incidencias" &
contar_directo /reservas    > "$TMP/reservas"    &
wait

fila () { printf "  %-14s %-16s %'d\n" "$1" "$2" "$(cat "$TMP/$1")"; }

printf "\n%s== PostgreSQL · condominio_residentes ==%s\n" "$gris" "$fin"
fila edificios   ms-residentes
fila unidades    ms-residentes
fila residentes  ms-residentes

printf "\n%s== MySQL · condominio_pagos ==%s\n" "$gris" "$fin"
fila cuotas ms-pagos
fila pagos  ms-pagos

printf "\n%s== MongoDB · condominio_incidencias ==%s\n" "$gris" "$fin"
fila incidencias ms-incidencias
fila reservas    ms-incidencias

printf "\n  %sEl enunciado exige un minimo de 20.000 registros en una tabla de cada base.%s\n\n" "$verde" "$fin"
