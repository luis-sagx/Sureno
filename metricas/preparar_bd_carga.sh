#!/usr/bin/env bash
# Clona la base de produccion a una base de PRUEBA para ejecutar las pruebas de
# carga sin tocar los datos reales (riesgo RY-01 del SQAP).
#
#   ./metricas/preparar_bd_carga.sh              # clonar Sureno -> Sureno_carga (en Atlas)
#   ./metricas/preparar_bd_carga.sh --local      # clonar Atlas -> Mongo local en Docker
#   ./metricas/preparar_bd_carga.sh --verificar  # solo comparar conteos, no copiar
#   ./metricas/preparar_bd_carga.sh --limpiar    # borrar la base de carga al terminar
#
# Lee MONGO_URI y MONGO_DB_NAME desde backend/.env. Usa la imagen mongo:7 de
# Docker, asi que no hace falta instalar mongodump/mongosh en el sistema.
#
# La copia es SOLO LECTURA sobre la base de origen: mongodump nunca la modifica.
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${RAIZ}/backend/.env"
IMG="mongo:7"
DESTINO="Sureno_carga"
MODO="atlas"

VERDE='\033[32m'; ROJO='\033[31m'; AMAR='\033[33m'; CIAN='\033[1;36m'; NC='\033[0m'
paso() { printf "\n${CIAN}==> %s${NC}\n" "$1"; }
err()  { printf "${ROJO}ERROR: %s${NC}\n" "$1" >&2; }

ACCION="clonar"
for arg in "$@"; do
  case "$arg" in
    --local)     MODO="local" ;;
    --verificar) ACCION="verificar" ;;
    --limpiar)   ACCION="limpiar" ;;
    --destino=*) DESTINO="${arg#*=}" ;;
    -h|--help)   sed -n '2,$p' "$0" | sed -n '/^#/!q;p' | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) err "opcion desconocida: $arg"; exit 2 ;;
  esac
done

# ------------------------------------------------------------------ checks ---
command -v docker >/dev/null || { err "docker no esta instalado."; exit 1; }
[[ -f "$ENV_FILE" ]] || { err "no existe $ENV_FILE"; exit 1; }

# shellcheck disable=SC1090
set -a; source "$ENV_FILE"; set +a
ORIGEN="${MONGO_DB_NAME:-Sureno}"

[[ -n "${MONGO_URI:-}" ]] || { err "MONGO_URI no definido en $ENV_FILE"; exit 1; }
[[ "$ORIGEN" != "$DESTINO" ]] || { err "origen y destino son la misma base ($ORIGEN)."; exit 1; }

# Host sin credenciales, para poder mostrarlo sin filtrar la password.
HOST_SEGURO=$(printf '%s' "$MONGO_URI" | sed -E 's|^(mongodb(\+srv)?://)[^@]*@|\1<credenciales>@|')

printf "\n${CIAN}Preparacion de la BD de carga — SQAP Sureno${NC}\n"
printf "  Cluster : %s\n" "$HOST_SEGURO"
printf "  Origen  : %s (produccion — solo se lee)\n" "$ORIGEN"
if [[ "$MODO" == "local" ]]; then
  printf "  Destino : %s en Mongo LOCAL (docker, puerto 27017)\n" "$ORIGEN"
else
  printf "  Destino : %s en el MISMO cluster de Atlas\n" "$DESTINO"
fi

# --------------------------------------------------------------- funciones ---
mongosh_uri() {   # $1 = uri, $2 = script js
  docker run --rm --network host "$IMG" mongosh "$1" --quiet --eval "$2"
}

comparar() {      # $1 = uri origen, $2 = db origen, $3 = uri destino, $4 = db destino
  local js
  js=$(cat <<JS
const o = db.getSiblingDB("$2");
const nombres = o.getCollectionNames().sort();
let salida = [];
nombres.forEach(n => salida.push(n + "=" + o[n].countDocuments()));
print(salida.join(","));
JS
)
  local izq der
  izq=$(mongosh_uri "$1" "$js" | tr -d '\r')
  js=${js//\"$2\"/\"$4\"}
  der=$(mongosh_uri "$3" "$js" | tr -d '\r')

  printf "\n  %-22s %10s %10s   %s\n" "COLECCION" "ORIGEN" "COPIA" "ESTADO"
  printf '  %.0s─' {1..62}; printf '\n'
  local fallos=0
  IFS=',' read -ra pares <<< "$izq"
  for p in "${pares[@]}"; do
    [[ -z "$p" ]] && continue
    local col="${p%%=*}" n1="${p##*=}" n2
    n2=$(printf '%s' "$der" | tr ',' '\n' | grep -E "^${col}=" | cut -d= -f2)
    [[ -z "$n2" ]] && n2="—"
    if [[ "$n1" == "$n2" ]]; then
      printf "  %-22s %10s %10s   ${VERDE}OK${NC}\n" "$col" "$n1" "$n2"
    else
      printf "  %-22s %10s %10s   ${ROJO}DIFIERE${NC}\n" "$col" "$n1" "$n2"
      ((fallos++))
    fi
  done
  printf '  %.0s─' {1..62}; printf '\n'
  return $fallos
}

# ------------------------------------------------------------------ limpiar --
if [[ "$ACCION" == "limpiar" ]]; then
  paso "Borrando la base de carga"
  if [[ "$MODO" == "local" ]]; then
    docker rm -f mongo-carga >/dev/null 2>&1 && printf "${VERDE}Contenedor mongo-carga eliminado.${NC}\n"
  else
    # dropDatabase requiere un rol que el usuario de la app puede no tener en
    # Atlas (dbAdmin). Se intenta, y si falla se borran las colecciones una a
    # una, que solo necesita permiso de escritura sobre la base.
    salida=$(mongosh_uri "$MONGO_URI" "
      const c = db.getSiblingDB('$DESTINO');
      try { c.dropDatabase(); print('DROPDB_OK'); }
      catch (e) {
        print('DROPDB_DENEGADO: ' + e.codeName);
        let fallos = 0;
        c.getCollectionNames().forEach(n => {
          try { c[n].drop(); } catch (e2) { fallos++; print('  no se pudo borrar ' + n); }
        });
        print(fallos === 0 ? 'COLECCIONES_OK' : 'COLECCIONES_FALLO');
      }
      print('RESTANTES=' + c.getCollectionNames().length);
    " 2>&1)

    restantes=$(printf '%s' "$salida" | grep -oE 'RESTANTES=[0-9]+' | cut -d= -f2)
    if [[ "$restantes" == "0" ]]; then
      if printf '%s' "$salida" | grep -q DROPDB_DENEGADO; then
        printf "${AMAR}Sin permiso de dropDatabase; se borraron todas las colecciones.${NC}\n"
        printf "${AMAR}La base %s queda vacia (Atlas la oculta sola).${NC}\n" "$DESTINO"
      else
        printf "${VERDE}Base %s eliminada del cluster.${NC}\n" "$DESTINO"
      fi
    else
      err "quedan $restantes coleccion(es) en $DESTINO. Borralas desde la UI de Atlas."
      printf '%s\n' "$salida"
      exit 1
    fi
  fi
  exit 0
fi

# ---------------------------------------------------------------- verificar --
if [[ "$ACCION" == "verificar" ]]; then
  paso "Comparando conteos de documentos"
  if [[ "$MODO" == "local" ]]; then
    comparar "$MONGO_URI" "$ORIGEN" "mongodb://localhost:27017" "$ORIGEN"
  else
    comparar "$MONGO_URI" "$ORIGEN" "$MONGO_URI" "$DESTINO"
  fi
  st=$?
  (( st == 0 )) && printf "${VERDE}La copia coincide con el origen.${NC}\n\n" \
                || printf "${ROJO}%d coleccion(es) no coinciden. Vuelve a clonar.${NC}\n\n" "$st"
  exit $st
fi

# ------------------------------------------------------------------ clonar ---
printf "\n${AMAR}Se va a ESCRIBIR en el destino. El origen no se modifica.${NC}\n"
read -rp "Continuar? [s/N] " ok
[[ "$ok" =~ ^[sS]$ ]] || { echo "Cancelado."; exit 0; }

if [[ "$MODO" == "local" ]]; then
  paso "1/3  Levantando Mongo local (docker, puerto 27017)"
  docker rm -f mongo-carga >/dev/null 2>&1
  docker run -d --name mongo-carga -p 27017:27017 "$IMG" >/dev/null
  printf "Esperando a que acepte conexiones"
  for _ in $(seq 1 30); do
    if docker exec mongo-carga mongosh --quiet --eval 'db.runCommand({ping:1})' >/dev/null 2>&1; then
      printf " ${VERDE}listo${NC}\n"; break
    fi
    printf '.'; sleep 1
  done

  paso "2/3  Copiando $ORIGEN de Atlas al Mongo local"
  docker run --rm --network host "$IMG" sh -c \
    "mongodump --uri='$MONGO_URI' --db='$ORIGEN' --archive | \
     mongorestore --uri='mongodb://localhost:27017' --archive --drop" || {
       err "fallo la copia"; exit 1; }

  paso "3/3  Verificando"
  comparar "$MONGO_URI" "$ORIGEN" "mongodb://localhost:27017" "$ORIGEN"; st=$?
  URI_CARGA="mongodb://localhost:27017"; DB_CARGA="$ORIGEN"
  # URI local: no contiene credenciales, es seguro mostrarla.
  URI_MOSTRABLE="MONGO_URI=\"$URI_CARGA\" "
else
  paso "1/2  Clonando $ORIGEN -> $DESTINO en el mismo cluster"
  docker run --rm --network host "$IMG" sh -c \
    "mongodump --uri='$MONGO_URI' --db='$ORIGEN' --archive | \
     mongorestore --uri='$MONGO_URI' --archive --drop \
                  --nsFrom='${ORIGEN}.*' --nsTo='${DESTINO}.*'" || {
       err "fallo la copia"; exit 1; }

  paso "2/2  Verificando"
  comparar "$MONGO_URI" "$ORIGEN" "$MONGO_URI" "$DESTINO"; st=$?
  URI_CARGA="$MONGO_URI"; DB_CARGA="$DESTINO"
  # NUNCA imprimir MONGO_URI en modo Atlas: lleva la password en claro y el
  # comando puede acabar en una grabacion de pantalla. El backend ya la lee
  # de backend/.env, asi que basta con sobrescribir el nombre de la base.
  URI_MOSTRABLE=""
fi

if (( st != 0 )); then
  err "la copia no coincide con el origen. Revisa antes de lanzar la carga."
  exit 1
fi

FLAG_MODO=""
[[ "$MODO" == "local" ]] && FLAG_MODO="--local "

printf "\n${VERDE}Copia lista.${NC} Ahora:\n\n"
cat <<EOF
  # 1) Backend contra la BD de carga (terminal aparte)
  cd backend
  ${URI_MOSTRABLE}MONGO_DB_NAME="$DB_CARGA" ../venv/bin/python app.py

  # 2) Prueba de carga
  cd backend
  ../venv/bin/locust -f Tests/carga/locustfile.py --host http://127.0.0.1:5000 \\
      --users 50 --spawn-rate 5 --run-time 2m --headless \\
      --html Tests/evidencias/reporte_carga.html --csv Tests/evidencias/carga

  # 3) Recalcular metricas y verificar reportes
  python3 metricas/calcular_metricas.py
  ./metricas/ver_reportes.sh

  # 4) Al terminar, borrar la BD de carga
  ./metricas/preparar_bd_carga.sh ${FLAG_MODO}--limpiar
EOF
