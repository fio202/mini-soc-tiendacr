# Anexos

## Anexo A. Repositorio

**URL:** https://github.com/fio202/mini-soc-tiendacr

| Ruta | Contenido |
|---|---|
| `Vagrantfile`, `provision/` | Definición y aprovisionamiento de las tres VM |
| `config/suricata/local.rules` | Reglas propias de Suricata |
| `config/wazuh-manager/` | Reglas propias de Wazuh y respuesta activa |
| `config/wazuh-agent/` | Configuración adicional del agente (registros y FIM) |
| `config/nginx/` | Proxy inverso en sus versiones original y remediada |
| `scripts/alertas-ataque.py` | Extracción de la evidencia de detección (tiempo hasta la alerta) |
| `docs/` | Documentación por sección y diagrama |
| `evidencias/` | Capturas del panel y de los registros |

## Anexo B. Evidencias

<span class="todo">COMPLETAR: insertar las capturas, con las IP públicas y los identificadores difuminados.</span>

| Figura | Contenido | Archivo |
|---|---|---|
| B1 | Agente `tiendacr-web` activo en el panel | `evidencias/agente-activo.png` |
| B2 | `ufw status verbose` del objetivo y del SIEM | `evidencias/ufw-*.png` |
| B3 | Ataque 1: alertas de escaneo en el panel | `evidencias/ataque1-*.png` |
| B4 | Ataque 2: alerta 100101 y bloqueo en iptables | `evidencias/ataque2-*.png` |
| B5 | Ataque 3: alerta 100122 y línea del access log | `evidencias/ataque3-*.png` |
| B6 | Ataque 4: alerta FIM 100110 | `evidencias/ataque4-*.png` |
| B7 | Antes y después de los ataques 2 y 3 | `evidencias/remediacion-*.png` |

El texto completo de las reglas propias está en el repositorio: `config/suricata/local.rules` (Suricata) y `config/wazuh-manager/tiendacr_rules.xml` (Wazuh).
