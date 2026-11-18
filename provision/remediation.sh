#!/usr/bin/env bash
# Activa o revierte la remediacion del punto 2.8 (para comparar antes/despues).
#   vagrant provision target --provision-with remediate     -> estado remediado
#   vagrant provision target --provision-with vulnerable    -> estado original (antes)
# Variable: MODE = remediate | vulnerable
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
CFG=/vagrant/config
ENVF=/opt/dvwa/.env

case "$MODE" in
  remediate)
    echo "[remediacion] Actualizando paquetes del sistema (CVE del host)"
    apt-get update -q && apt-get upgrade -y -q >/dev/null
    echo "[remediacion] Nivel de seguridad de la aplicacion: impossible"
    sed -i 's/^DVWA_SECURITY_LEVEL=.*/DVWA_SECURITY_LEVEL=impossible/' "$ENVF"
    echo "[remediacion] Imagen de la aplicacion actualizada"
    docker compose -f /opt/dvwa/compose.yml --env-file "$ENVF" pull -q
    SITE="$CFG/nginx/tiendacr-remediado.conf"
    ;;
  vulnerable)
    echo "[remediacion] Revirtiendo al estado original (nivel low, sin controles en nginx)"
    sed -i 's/^DVWA_SECURITY_LEVEL=.*/DVWA_SECURITY_LEVEL=low/' "$ENVF"
    SITE="$CFG/nginx/tiendacr.conf"
    ;;
  *) echo "MODE debe ser remediate o vulnerable"; exit 1 ;;
esac

docker compose -f /opt/dvwa/compose.yml --env-file "$ENVF" up -d
install -m 644 "$SITE" /etc/nginx/sites-available/tiendacr.conf
nginx -t && systemctl reload nginx
echo "[remediacion] Estado aplicado: $MODE"
