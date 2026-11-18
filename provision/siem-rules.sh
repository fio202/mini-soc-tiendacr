#!/usr/bin/env bash
# Instala reglas propias y respuesta activa en el manager Wazuh (idempotente).
# Uso: vagrant provision siem --provision-with rules
set -euo pipefail
CFG=/vagrant/config/wazuh-manager
OSSEC=/var/ossec/etc/ossec.conf

install -o root -g wazuh -m 660 "$CFG/tiendacr_rules.xml" /var/ossec/etc/rules/tiendacr_rules.xml

python3 - "$OSSEC" "$CFG/active-response.xml" <<'PY'
import sys, re
path, ar_path = sys.argv[1], sys.argv[2]
conf = open(path).read()
ar = open(ar_path).read()
# 1) Bloque de respuesta activa (reemplaza el anterior si existe)
conf = re.sub(r"\n  <!-- TiendaCR: respuesta activa.*?</active-response>\n", "\n", conf, flags=re.S)
i = conf.index("</ossec_config>")
conf = conf[:i] + ar + conf[i:]
# 2) Lista blanca: la laptop del equipo y el propio SIEM nunca se bloquean
for ip in ("192.168.56.1", "192.168.56.20"):
    if f"<white_list>{ip}</white_list>" not in conf:
        conf = conf.replace("<white_list>127.0.0.1</white_list>",
                            f"<white_list>127.0.0.1</white_list>\n    <white_list>{ip}</white_list>", 1)
open(path, "w").write(conf)
PY

/var/ossec/bin/wazuh-analysisd -t       # valida reglas y configuracion antes de reiniciar
systemctl restart wazuh-manager
echo "[siem] Reglas TiendaCR y respuesta activa instaladas"
