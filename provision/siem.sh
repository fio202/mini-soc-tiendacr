#!/usr/bin/env bash
# Servidor SIEM: Wazuh all-in-one (indexer + manager + dashboard)
# Variables: WAZUH_SERIES, TARGET_IP, HOST_IP
set -euo pipefail
LAB_IF=$(ip -o -4 addr show | awk '$4 ~ /^192\.168\.56\./ {print $2; exit}')

if ! systemctl is-active --quiet wazuh-manager; then
  echo "[siem] Instalando Wazuh ${WAZUH_SERIES} (tarda 10-20 min)"
  cd /root
  curl -sSO "https://packages.wazuh.com/${WAZUH_SERIES}/wazuh-install.sh"
  bash wazuh-install.sh -a -o > /root/wazuh-install.log 2>&1
  # Las credenciales quedan SOLO dentro de la VM (/root), nunca en el repositorio
  tar -O -xf /root/wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt > /root/wazuh-passwords.txt
  chmod 600 /root/wazuh-passwords.txt /root/wazuh-install-files.tar
fi

echo "[siem] Reglas de firewall del SIEM"
ufw allow in on "$LAB_IF" from "$TARGET_IP" to any port 1514 proto tcp comment 'R10 eventos del agente (target)'
ufw allow in on "$LAB_IF" from "$TARGET_IP" to any port 1515 proto tcp comment 'R11 registro del agente (target)'
ufw allow in on "$LAB_IF" from "$HOST_IP"   to any port 443  proto tcp comment 'R12 panel Wazuh solo para el equipo'
ufw reload
ufw status numbered

echo "[siem] Listo. Panel: https://192.168.56.20  (usuario admin; clave en /root/wazuh-passwords.txt)"
