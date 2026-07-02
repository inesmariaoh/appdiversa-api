#!/usr/bin/env bash
# Restaura el dump local de AppDiversa en MySQL de Aiven (SSL obligatorio).
# Uso desde Git Bash o WSL en Windows:
#   export AIVEN_PASSWORD='tu_password_de_aiven'
#   ./scripts/restaurar_dump_aiven.sh dumps/appdiversa_dump_20260701.sql

set -o errexit

DUMP_FILE="${1:-dumps/appdiversa_dump_20260701.sql}"
AIVEN_HOST="${AIVEN_HOST:-appdiversa-mysql-appdiversa.e.aivencloud.com}"
AIVEN_PORT="${AIVEN_PORT:-13375}"
AIVEN_USER="${AIVEN_USER:-avnadmin}"
AIVEN_DB="${AIVEN_DB:-defaultdb}"
CA_FILE="${CA_FILE:-dumps/ca.pem}"

if [[ ! -f "$DUMP_FILE" ]]; then
  echo "No se encontro el archivo dump: $DUMP_FILE"
  exit 1
fi

if [[ -z "${AIVEN_PASSWORD:-}" ]]; then
  echo "Defina la variable AIVEN_PASSWORD con la contrasena de Aiven."
  exit 1
fi

if [[ ! -f "$CA_FILE" ]]; then
  echo "Advertencia: no se encontro $CA_FILE; se usara --ssl-mode=REQUIRED sin verificar CA."
  SSL_ARGS=(--ssl-mode=REQUIRED)
else
  SSL_ARGS=(--ssl-mode=VERIFY_CA --ssl-ca="$CA_FILE")
fi

echo "Restaurando $DUMP_FILE en ${AIVEN_HOST}:${AIVEN_PORT}/${AIVEN_DB} ..."

mysql \
  --host="$AIVEN_HOST" \
  --port="$AIVEN_PORT" \
  --user="$AIVEN_USER" \
  --password="$AIVEN_PASSWORD" \
  --database="$AIVEN_DB" \
  "${SSL_ARGS[@]}" \
  < "$DUMP_FILE"

echo "Restauracion completada."
