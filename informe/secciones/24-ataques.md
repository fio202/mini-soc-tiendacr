# 2.4 Ataques controlados y detecciones

**Condiciones:**

- **Origen:** `tiendacr-kali` (192.168.56.30). **Objetivo:** `tiendacr-web` (192.168.56.10) en el estado vulnerable.
- Solo recursos propios, en una red aislada y sin pruebas de denegación de servicio.

**Medición del tiempo hasta la alerta:**

- La hora de inicio se toma en Kali justo antes de cada ataque.
- La primera alerta de cada regla se extrae del SIEM con `scripts/alertas-ataque.py`, que calcula la diferencia (T+).
- Todas las VM usan la misma zona horaria (UTC-6).
- El procedimiento completo está en `docs/2.4-ataques-y-detecciones.md`.

| N.º | Ataque | Comando o herramienta | Evidencia en registros | Regla que lo detectó | Tiempo hasta la alerta | MITRE ATT&CK |
|---|---|---|---|---|---|---|
| 1 | Reconocimiento: escaneo de puertos y servicios | ✏️ | `eve.json` (sid 1000001 + ET SCAN); `ufw.log` ([UFW BLOCK]) | Suricata **1000001** → Wazuh **100120** ✏️ | ✏️ s | T1046 Network Service Discovery |
| 2 | Fuerza bruta al login de la aplicación | ✏️ | Access log (GET repetidos a `/vulnerabilities/brute/`); `eve.json` (1000002); `active-responses.log` | Wazuh **100100 → 100101**; Suricata **1000002** → **100121** ✏️ | ✏️ s (alerta) · ✏️ s (bloqueo) | T1110.001 Password Guessing |
| 3 | Explotación web: ✏️ SQLi / traversal | ✏️ | Access log (payload, código y tamaño de respuesta); `eve.json` (1000003-1000005) | Suricata **1000003/4/5** → Wazuh **100122** ✏️ | ✏️ s | T1190 Exploit Public-Facing Application |
| 4 | Subida de web shell y modificación de archivos | ✏️ | `eve.json` (1000006); FIM en `/opt/dvwa/uploads` (hash SHA-256) | Suricata **1000006** → **100123**; FIM 554 → **100110** ✏️ | ✏️ s | T1505.003 Web Shell |

**Por qué el ataque 2 es contra el login de la aplicación y no contra SSH:** SSH solo acepta llaves (2.2). Una fuerza bruta de contraseñas contra SSH no tiene nada que adivinar, y eso es evidencia de que el control funciona.

**Justificación del ataque 4:** es la continuación natural de un acceso inicial (persistencia). Permite demostrar una detección de **host** (FIM en tiempo real), además de las de red.

**Observaciones:**

- **Ataque 1:** ✏️ (puertos que vio el atacante: deberían ser solo 22 y 80).
- **Ataque 2:** ✏️ (¿se obtuvo la contraseña antes del bloqueo? Posición de la regla DROP en iptables).
- **Ataque 3:** ✏️ (datos obtenidos).
- **Ataque 4:** ✏️ (archivo y hash).

Las capturas de cada ataque están en el anexo B.
