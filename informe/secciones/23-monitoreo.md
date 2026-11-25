# 2.3 Monitoreo

| Requisito del enunciado | Implementación | Verificación (17/11/2026) |
|---|---|---|
| SIEM central con agente en el objetivo | Wazuh 4.14 *all-in-one* en `tiendacr-siem`; agente `tiendacr-web` (ID 001) | `agent_control -l`: agente **Active** |
| Registros de autenticación | Journal (sshd, sudo, PAM) | Regla 5715 "sshd: authentication success" recibida |
| Integridad de archivos (FIM) | Tiempo real con `report_changes` sobre `/opt/dvwa/uploads`, `/etc/nginx`, `/etc/ssh`, `authorized_keys`, `/etc/ufw` y `/etc/suricata` | Reglas 554 (archivo creado) y 553 (archivo borrado) en `/etc/nginx` |
| Detección de vulnerabilidades | Módulo del manager más `syscollector` del agente | Miles de CVE inventariadas, casi todas del kernel (ver 1.3) |
| IDS de red integrado al panel | Suricata en `eth1` (AF_PACKET), ET Open (~53 500 reglas) más reglas propias; el agente lee `eve.json` (JSON) | La alerta de prueba sid 1000000 llega al SIEM como regla 86601 |
| Registros web | El access log de nginx en el host lo lee el agente (decodificador nativo `web-accesslog`) | Reglas 31101 y 31151 recibidas durante las pruebas |

**Decisiones de diseño:**

1. **nginx delante de DVWA.** Deja en el host un registro web que el agente puede leer y permite publicar el contenedor solo en `127.0.0.1`.
2. **Suricata en la interfaz del laboratorio.** Inspecciona solo el tráfico de la red protegida, no el de gestión (NAT).
3. **`checksum-validation: no`.** Evita que Suricata descarte flujos válidos por la descarga de checksums de la tarjeta virtual.
4. **El directorio de subidas de la aplicación está montado en el host.** Así el FIM puede detectar una web shell.
