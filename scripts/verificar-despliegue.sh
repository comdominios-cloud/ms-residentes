#!/usr/bin/env bash
# ============================================================
# Verificacion del despliegue completo - CS2032 Condominios
# ============================================================
# Corre esto ANTES de la asesoria. En unos segundos te dice que
# esta arriba, que esta caido y de quien depende cada cosa.
#
#   ./scripts/verificar-despliegue.sh
#
# Se puede apuntar a otro entorno con variables de entorno:
#   ALB=http://otro-balanceador FRONT=https://otro.amplifyapp.com ./scripts/verificar-despliegue.sh
# ============================================================

ALB="${ALB:-http://alb-condominio-678852222.us-east-1.elb.amazonaws.com}"
FRONT="${FRONT:-https://main.d25obrvgff3lqx.amplifyapp.com}"
USUARIO_DEMO="${USUARIO_DEMO:-admin@condominio.com}"
PASS_DEMO="${PASS_DEMO:-condominio123}"
TIMEOUT="${TIMEOUT:-8}"

# Documento que YA existe en el seed de ms-residentes: sirve para probar el
# token sin insertar datos, porque la API responde 409 en vez de crear.
DOC_EXISTENTE="${DOC_EXISTENTE:-45781230}"

verde=$'\e[32m'; rojo=$'\e[31m'; amarillo=$'\e[33m'; gris=$'\e[90m'; fin=$'\e[0m'
ok=0; fallas=0

titulo () { printf "\n%s== %s ==%s\n" "$gris" "$1" "$fin"; }

bien ()  { printf "  ${verde}OK${fin}    %-42s %s\n" "$1" "$2"; ok=$((ok+1)); }
mal ()   { printf "  ${rojo}FALLA${fin} %-42s %s\n" "$1" "$2"; fallas=$((fallas+1)); }
aviso () { printf "  ${amarillo}AVISO${fin} %-42s %s\n" "$1" "$2"; }

# Devuelve el codigo HTTP, o 000 si no hubo respuesta.
codigo () { curl -s -m "$TIMEOUT" -o /dev/null -w "%{http_code}" "$@" 2>/dev/null; }
cuerpo () { curl -s -m "$TIMEOUT" "$@" 2>/dev/null; }

# ------------------------------------------------------------
titulo "Balanceador"
# ------------------------------------------------------------
c=$(codigo "$ALB/")
case "$c" in
  200|301|302|404) bien "ALB responde" "HTTP $c" ;;
  503) mal "ALB sin destinos sanos" "HTTP 503 - revisar si las instancias estan prendidas" ;;
  000) mal "ALB inalcanzable" "sin respuesta - instancias apagadas o DNS mal" ;;
  *)   aviso "ALB responde raro" "HTTP $c" ;;
esac

# ------------------------------------------------------------
titulo "Microservicios"
# ------------------------------------------------------------
# nombre:puerto:responsable
servicios=(
  "ms-residentes:9001:@Osomar1705"
  "ms-usuarios:9006:@Osomar1705"
  "ms-pagos:9002:@sebastianperez72"
  "ms-incidencias:9003:@fabianbot1331"
  "ms-ficha-residente:9004:@Brisseth-raton"
  "ms-analitico:9005:@carloscondor1610"
)

for s in "${servicios[@]}"; do
  IFS=: read -r nombre puerto duenio <<< "$s"
  url="$ALB:$puerto/health"
  c=$(codigo "$url")

  if [ "$c" = "200" ]; then
    # /health devuelve 200 aunque la base falle: hay que mirar el cuerpo.
    if cuerpo "$url" | grep -q '"database":"ok"'; then
      bien "$nombre ($puerto)" "vivo, base conectada"
    else
      mal "$nombre ($puerto)" "vivo pero SIN base - revisar POSTGRES_HOST y credenciales"
    fi
  elif [ "$c" = "000" ]; then
    mal "$nombre ($puerto)" "sin respuesta - falta listener en el ALB o el contenedor no corre ($duenio)"
  else
    mal "$nombre ($puerto)" "HTTP $c ($duenio)"
  fi
done

# ------------------------------------------------------------
titulo "Autenticacion entre microservicios"
# ------------------------------------------------------------
respuesta=$(cuerpo -X POST "$ALB:9006/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$USUARIO_DEMO\",\"password\":\"$PASS_DEMO\"}")

token=$(printf '%s' "$respuesta" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$token" ]; then
  bien "login en ms-usuarios" "token emitido"

  # El token lo emitio ms-usuarios; lo verifica ms-residentes con el mismo
  # JWT_SECRET, sin llamarse entre si. Usamos un documento que ya existe:
  #   409 -> el token paso y llego a la validacion de negocio
  #   401 -> el token fue rechazado (JWT_SECRET distinto entre servicios)
  c=$(codigo -X POST "$ALB:9001/residentes" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{\"unidad_id\":1,\"nombres\":\"Prueba\",\"apellidos\":\"Verificacion\",\"documento\":\"$DOC_EXISTENTE\"}")

  case "$c" in
    409) bien "token aceptado por ms-residentes" "409, no se insertaron datos" ;;
    401) mal "token RECHAZADO por ms-residentes" "el JWT_SECRET no coincide entre los dos .env" ;;
    201) aviso "token aceptado" "201: se creo un residente, borrar el documento $DOC_EXISTENTE" ;;
    000) mal "ms-residentes inalcanzable" "no se pudo probar el token" ;;
    *)   aviso "respuesta inesperada" "HTTP $c" ;;
  esac
else
  mal "login en ms-usuarios" "sin token - servicio caido o credenciales de demo cambiadas"
  aviso "" "se omite la prueba del token entre servicios"
fi

# ------------------------------------------------------------
titulo "Frontend"
# ------------------------------------------------------------
c=$(codigo "$FRONT/")
if [ "$c" = "200" ]; then
  bien "Amplify sirve la SPA" "HTTP 200"
else
  mal "Amplify no responde" "HTTP $c"
fi

# El proxy es lo que evita el bloqueo por mixed content: si esto falla, el
# frontend carga pero ninguna llamada a la API funciona.
c=$(codigo "$FRONT/api/usuarios/health")
case "$c" in
  200)     bien "proxy /api/ hacia los microservicios" "HTTP 200" ;;
  301|302) mal "proxy /api/ sin configurar" "Amplify redirige: faltan los rewrites" ;;
  404)     mal "proxy /api/ sin configurar" "faltan los rewrites en Amplify" ;;
  502|504) mal "proxy /api/ sin destino" "el rewrite existe pero el ALB no responde en ese puerto" ;;
  000)     mal "proxy /api/ inalcanzable" "sin respuesta" ;;
  *)       mal "proxy /api/" "HTTP $c" ;;
esac

# ------------------------------------------------------------
titulo "Resumen"
# ------------------------------------------------------------
printf "  %s%s correctas%s, %s%s fallas%s\n" "$verde" "$ok" "$fin" "$rojo" "$fallas" "$fin"

if [ "$fallas" -eq 0 ]; then
  printf "\n  ${verde}Todo operativo.${fin}\n\n"
  exit 0
fi

printf "\n  ${amarillo}Revisar lo de arriba antes de la asesoria.${fin}\n\n"
exit 1
