#!/usr/bin/env bash
# Instala/recarga las reglas propias de Suricata (idempotente).
# Uso: vagrant provision target --provision-with rules
set -euo pipefail
install -m 644 /vagrant/config/suricata/local.rules /etc/suricata/rules/local.rules
suricata -T -c /etc/suricata/suricata.yaml      # valida sintaxis antes de aplicar
systemctl restart suricata
echo "[target] Reglas propias de Suricata cargadas"
