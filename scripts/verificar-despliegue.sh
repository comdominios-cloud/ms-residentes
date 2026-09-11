#!/usr/bin/env bash
# ============================================================
# Verificacion del despliegue completo - CS2032 Condominios
# ============================================================
# Corre esto ANTES de la asesoria. En unos segundos te dice que
# esta arriba, que esta caido y de quien depende cada cosa.
#
#   ./scripts/verificar-despliegue.sh
#
# El ALB usa ruteo POR RUTA sobre el puerto 80: cada regla del listener
# manda una ruta a su target group. Por eso aca se prueban rutas y no puertos.
# ============================================================

ALB="${ALB:-http://alb-condominio-678852222.us-east-1.elb.amazonaws.com}"
FRONT="${FRONT:-https://main.d25obrvgff3lqx.amplifyapp.com}"
USUARIO_DEMO="${USUARIO_DEMO:-admin@condominio.com}"
PASS_DEMO="${PASS_DEMO:-condominio123}"
TIMEOUT="${TIMEOUT:-8}"

# Documento que YA existe en el seed: sirve para probar el token sin insertar
# datos, porque la API responde 409 en vez de crear.
DOC_EXISTENTE="${DOC_EXISTENTE:-45781230}"

verde=$'\e[32m'; rojo=$'\e[31m'; amarillo=$'\e[33m'; gris=$'\e[90m'; fin=$'\e[0m'
ok=0; fallas=0; avisos=0

titulo () { printf "\n%s== %s ==%s\n" "$gris" "$1" "$fin"; }
bien ()  { printf "  ${verde}OK${fin}    %-40s %s\n" "$1" "$2"; ok=$((ok+1)); }
mal ()   { printf "  ${rojo}FALLA${fin} %-40s %s\n" "$1" "$2"; fallas=$((fallas+1)); }
aviso () { printf "  ${amarillo}AVISO${fin} %-40s %s\n" "$1" "$2"; avisos=$((avisos+1)); }

codigo () { curl -s -m "$TIMEOUT" -o /dev/null -w "%{http_code}" "$@" 2>/dev/null; }
cuerpo () { curl -s -m "$TIMEOUT" "$@" 2>/dev/null; }

# ------------------------------------------------------------
titulo "Balanceador"
# ------------------------------------------------------------
c=$(codigo "$ALB/")
case "$c" in
  200) bien "ALB responde" "HTTP 200" ;;
  503) mal "ALB sin destinos sanos" "instancias apagadas o contenedores caidos" ;;
  000) mal "ALB inalcanzable" "sin respuesta" ;;
  *)   aviso "ALB responde" "HTTP $c" ;;
esac

# ------------------------------------------------------------
titulo "Microservicios (via ruteo por ruta)"
# ------------------------------------------------------------

# --- ms-residentes: si /residentes trae filas, el servicio Y su base andan ---
filas=$(cuerpo "$ALB/residentes" | grep -o '"documento"' | wc -l)
c=$(codigo "$ALB/residentes")
if [ "$c" = "200" ] && [ "$filas" -gt 0 ]; then
  bien "ms-residentes" "$filas residentes desde PostgreSQL"
elif [ "$c" = "200" ]; then
  mal "ms-residentes" "responde pero sin datos: falta cargar el seed"
elif [ "$c" = "404" ]; then
  mal "ms-residentes" "404: falta la regla de ruta en el ALB (@Brisseth-raton)"
else
  mal "ms-residentes" "HTTP $c"
fi

# --- ms-usuarios: el login prueba servicio y base a la vez ---
respuesta=$(cuerpo -X POST "$ALB/auth/login" -H "Content-Type: application/json" \
  -d "{\"email\":\"$USUARIO_DEMO\",\"password\":\"$PASS_DEMO\"}")
token=$(printf '%s' "$respuesta" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$token" ]; then
  bien "ms-usuarios" "login correcto, token emitido"
else
  mal "ms-usuarios" "sin token: servicio caido, sin base, o falta la regla /auth"
fi

# --- el resto, informativo ---
for par in "ms-pagos:/cuotas:@sebastianperez72" \
           "ms-incidencias:/incidencias:@fabianbot1331" \
           "ms-ficha-residente:/ficha/1:@Brisseth-raton" \
           "ms-analitico:/analitica/morosidad-por-edificio:@carloscondor1610"; do
  IFS=: read -r nombre ruta duenio <<< "$par"
  c=$(codigo "$ALB$ruta")
  case "$c" in
    200) bien "$nombre" "responde en $ruta" ;;
    404) aviso "$nombre" "sin desplegar o sin regla de ruta ($duenio)" ;;
    000) aviso "$nombre" "sin respuesta ($duenio)" ;;
    *)   aviso "$nombre" "HTTP $c ($duenio)" ;;
  esac
done

# ------------------------------------------------------------
titulo "Rutas de lectura que usa el frontend"
# ------------------------------------------------------------
for ruta in /residentes /residentes/1 /unidades /edificios; do
  c=$(codigo "$ALB$ruta")
  if [ "$c" = "200" ]; then
    bien "GET $ruta" "HTTP 200"
  elif [ "$c" = "404" ]; then
    mal "GET $ruta" "falta la regla de ruta en el ALB"
  else
    mal "GET $ruta" "HTTP $c"
  fi
done

# ------------------------------------------------------------
titulo "Autenticacion entre microservicios"
# ------------------------------------------------------------
if [ -n "$token" ]; then
  # El token lo emitio ms-usuarios y lo verifica ms-residentes con el mismo
  # JWT_SECRET, sin llamarse entre si. Con un documento que ya existe:
  #   409 -> el token paso y llego a la validacion de negocio
  #   401 -> el token fue rechazado (JWT_SECRET distinto)
  #   500 -> imagen desactualizada en la VM
  c=$(codigo -X POST "$ALB/residentes" \
        -H "Authorization: Bearer $token" -H "Content-Type: application/json" \
        -d "{\"unidad_id\":1,\"nombres\":\"Prueba\",\"apellidos\":\"Verificacion\",\"documento\":\"$DOC_EXISTENTE\"}")
  case "$c" in
    409) bien "token aceptado por ms-residentes" "409, no se insertaron datos" ;;
    401) mal "token RECHAZADO" "el JWT_SECRET no coincide entre los dos .env" ;;
    500) mal "error interno en ms-residentes" "imagen vieja en la VM: desplegar osomar/ms-residentes:0.2.0" ;;
    201) aviso "token aceptado" "201: se creo un residente, borrar el documento $DOC_EXISTENTE" ;;
    *)   aviso "respuesta inesperada" "HTTP $c" ;;
  esac

  c=$(codigo -X POST "$ALB/residentes" -H "Content-Type: application/json" \
        -d '{"unidad_id":1,"nombres":"X","apellidos":"Y","documento":"99999999"}')
  [ "$c" = "401" ] && bien "escritura sin token rechazada" "401" \
                   || mal "escritura sin token" "deberia dar 401 y dio $c"
else
  aviso "prueba del token" "se omite: no hubo login"
fi

# ------------------------------------------------------------
titulo "Frontend"
# ------------------------------------------------------------
c=$(codigo "$FRONT/")
[ "$c" = "200" ] && bien "Amplify sirve la SPA" "HTTP 200" || mal "Amplify" "HTTP $c"

# Sin esto el frontend carga pero ninguna llamada a la API funciona.
c=$(codigo "$FRONT/api/residentes/residentes")
case "$c" in
  200)     bien "proxy /api/ hacia los microservicios" "HTTP 200" ;;
  301|302) mal "proxy /api/ sin configurar" "faltan los rewrites en Amplify (@alxgr-08)" ;;
  404)     mal "proxy /api/ sin configurar" "faltan los rewrites en Amplify (@alxgr-08)" ;;
  502|504) mal "proxy /api/ sin destino" "el rewrite existe pero el ALB no responde" ;;
  *)       mal "proxy /api/" "HTTP $c" ;;
esac

# ------------------------------------------------------------
titulo "Resumen"
# ------------------------------------------------------------
printf "  %s%s correctas%s, %s%s fallas%s, %s%s avisos%s\n" \
  "$verde" "$ok" "$fin" "$rojo" "$fallas" "$fin" "$amarillo" "$avisos" "$fin"

if [ "$fallas" -eq 0 ]; then
  printf "\n  ${verde}Lo evaluado esta operativo.${fin}\n\n"; exit 0
fi
printf "\n  ${amarillo}Revisar lo de arriba antes de la asesoria.${fin}\n\n"
exit 1
