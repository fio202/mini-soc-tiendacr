#!/usr/bin/env bash
# Endurecimiento comun para siem y target:
#  - SSH solo con llaves, sin root, sin contrasenas
#  - UFW con denegacion por defecto; SSH solo desde las IP del equipo
# Variables: TEAM_IPS (lista separada por espacios)
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

echo "[common] Actualizando paquetes base"
apt-get update -q
apt-get install -y -q ufw curl jq ca-certificates gnupg chrony >/dev/null
timedatectl set-timezone America/Costa_Rica

# Interfaz de la red solo-anfitrion (la que tiene una IP 192.168.56.x)
LAB_IF=$(ip -o -4 addr show | awk '$4 ~ /^192\.168\.56\./ {print $2; exit}')
NAT_IF=$(ip -o -4 route show default | awk '{print $5; exit}')
echo "[common] LAB_IF=$LAB_IF NAT_IF=$NAT_IF"

echo "[common] Endureciendo SSH"
# El primer valor leido gana en sshd, por eso el prefijo 00-
cat > /etc/ssh/sshd_config.d/00-hardening.conf <<'EOF'
# TiendaCR - politica de acceso administrativo
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
PermitEmptyPasswords no
MaxAuthTries 3
LoginGraceTime 30
X11Forwarding no
AllowUsers vagrant
EOF
sshd -t
systemctl reload ssh

echo "[common] Configurando UFW (denegacion por defecto)"
ufw --force reset >/dev/null
ufw default deny incoming
ufw default allow outgoing
ufw default deny routed
# Canal de gestion de Vagrant: solo el NAT interno de VirtualBox (10.0.2.2), no expuesto a la red
ufw allow in on "$NAT_IF" from 10.0.2.2 to any port 22 proto tcp comment 'R00 gestion vagrant (NAT VirtualBox)'
for ip in $TEAM_IPS; do
  ufw allow in on "$LAB_IF" from "$ip" to any port 22 proto tcp comment "R01 SSH admin desde $ip"
done
ufw logging medium
ufw --force enable
ufw status numbered
