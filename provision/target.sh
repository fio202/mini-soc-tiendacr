#!/usr/bin/env bash
# Servidor objetivo: DVWA (Docker) detras de nginx + Suricata + agente Wazuh
# Variables: WAZUH_SERIES, SIEM_IP, TARGET_IP, TEAM_IPS
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
LAB_IF=$(ip -o -4 addr show | awk '$4 ~ /^192\.168\.56\./ {print $2; exit}')
CFG=/vagrant/config

echo "[target] Paquetes: docker, nginx, suricata"
apt-get install -y -q docker.io docker-compose-v2 nginx suricata suricata-update >/dev/null
systemctl enable --now docker

# ---------------------------------------------------------------- DVWA
echo "[target] Desplegando DVWA en contenedores"
mkdir -p /opt/dvwa/uploads
chown 33:33 /opt/dvwa/uploads            # www-data dentro del contenedor
install -m 644 "$CFG/dvwa/compose.yml" /opt/dvwa/compose.yml
if [ ! -f /opt/dvwa/.env ]; then           # claves aleatorias, solo en la VM
  umask 077
  cat > /opt/dvwa/.env <<EOF
DVWA_DB_PASSWORD=$(openssl rand -hex 16)
DVWA_DB_ROOT_PASSWORD=$(openssl rand -hex 16)
DVWA_SECURITY_LEVEL=low
EOF
fi
for i in 1 2 3 4 5; do
  docker compose -f /opt/dvwa/compose.yml --env-file /opt/dvwa/.env pull -q && break
  echo "[target] Reintentando descarga de imagenes ($i)"; sleep 10
done
docker compose -f /opt/dvwa/compose.yml --env-file /opt/dvwa/.env up -d

if [ ! -f /opt/dvwa/.db_initialized ]; then
  echo "[target] Inicializando base de datos de DVWA"
  for i in $(seq 1 60); do
    curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:4280/setup.php | grep -q 200 && break
    sleep 3
  done
  JAR=$(mktemp)
  for i in $(seq 1 10); do   # MariaDB puede tardar en aceptar conexiones
    TOKEN=$(curl -s -c "$JAR" -b "$JAR" http://127.0.0.1:4280/setup.php | grep -oP "name='user_token' value='\K[^']+")
    # El POST responde 302; el resultado se muestra en el GET siguiente (sigue la redireccion con -L)
    if curl -s -L -c "$JAR" -b "$JAR" --data "create_db=Create+%2F+Reset+Database&user_token=${TOKEN}" \
         http://127.0.0.1:4280/setup.php | grep -q "Setup successful"; then
      touch /opt/dvwa/.db_initialized && echo "[target] BD de DVWA creada"; break
    fi
    echo "[target] BD aun no disponible, reintento $i"; sleep 6
  done
  rm -f "$JAR"
fi

# ---------------------------------------------------------------- nginx
echo "[target] Configurando nginx como proxy inverso"
echo 'net.ipv4.ip_nonlocal_bind=1' > /etc/sysctl.d/90-tiendacr.conf && sysctl -q --system
rm -f /etc/nginx/sites-enabled/default
install -m 644 "$CFG/nginx/tiendacr.conf" /etc/nginx/sites-available/tiendacr.conf
ln -sf /etc/nginx/sites-available/tiendacr.conf /etc/nginx/sites-enabled/tiendacr.conf
nginx -t && systemctl restart nginx

# ---------------------------------------------------------------- Suricata
echo "[target] Configurando Suricata en $LAB_IF"
Y=/etc/suricata/suricata.yaml
[ -f $Y.orig ] || cp $Y $Y.orig
cp $Y.orig $Y
sed -i 's|^\(\s*\)HOME_NET: .*|\1HOME_NET: "[192.168.56.10/32]"|' $Y
sed -i 's|^\(\s*\)EXTERNAL_NET: .*|\1EXTERNAL_NET: "!$HOME_NET"|' $Y
sed -i "0,/^\s*- interface: eth0/s//  - interface: $LAB_IF/" $Y
sed -i 's|^\(\s*\)checksum-validation: yes|\1checksum-validation: no|' $Y
sed -i 's|^default-rule-path: .*|default-rule-path: /var/lib/suricata/rules|' $Y
grep -q '/etc/suricata/rules/local.rules' $Y || \
  sed -i '/^rule-files:/a\  - /etc/suricata/rules/local.rules' $Y
[ -f /etc/default/suricata ] && sed -i "s/^IFACE=.*/IFACE=$LAB_IF/" /etc/default/suricata
mkdir -p /etc/suricata/rules
install -m 644 "$CFG/suricata/local.rules" /etc/suricata/rules/local.rules
suricata-update -q --no-test || true      # reglas ET Open
suricata -T -c $Y
systemctl enable suricata && systemctl restart suricata

# ---------------------------------------------------------------- Agente Wazuh
if ! dpkg -s wazuh-agent >/dev/null 2>&1; then
  echo "[target] Instalando agente Wazuh ${WAZUH_SERIES}"
  curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | \
    gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import
  chmod 644 /usr/share/keyrings/wazuh.gpg
  echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" \
    > /etc/apt/sources.list.d/wazuh.list
  apt-get update -q
  WAZUH_MANAGER="$SIEM_IP" WAZUH_AGENT_NAME="tiendacr-web" \
    apt-get install -y -q "wazuh-agent=${WAZUH_SERIES}.*" >/dev/null
fi
OSSEC=/var/ossec/etc/ossec.conf
if ! grep -q 'TiendaCR' $OSSEC; then
  cat "$CFG/wazuh-agent/ossec-tiendacr.conf" >> $OSSEC
fi
systemctl daemon-reload
systemctl enable wazuh-agent && systemctl restart wazuh-agent

# ---------------------------------------------------------------- Firewall
echo "[target] Reglas de firewall de la aplicacion"
for ip in $TEAM_IPS; do
  ufw allow in on "$LAB_IF" from "$ip" to "$TARGET_IP" port 80 proto tcp comment "R02 HTTP TiendaCR desde $ip"
done
ufw reload
ufw status numbered
echo "[target] Listo. Aplicacion: http://$TARGET_IP/"
