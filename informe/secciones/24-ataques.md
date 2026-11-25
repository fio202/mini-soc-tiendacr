# 2.4 Ataques controlados y detecciones

**Condiciones:**

- **Origen:** `tiendacr-kali` (192.168.56.30). **Objetivo:** `tiendacr-web` (192.168.56.10) en el estado vulnerable.
- Solo recursos propios, en una red aislada y sin pruebas de denegación de servicio.

**Medición del tiempo hasta la alerta:**

- La hora de inicio se toma en Kali justo antes de cada ataque.
- La primera alerta de cada regla se extrae del SIEM con `scripts/alertas-ataque.py`, que calcula la diferencia (T+).
- Todas las VM usan la misma zona horaria (UTC-6).
- El procedimiento completo está en `docs/2.4-ataques-y-detecciones.md`.
- Las técnicas se clasificaron con la matriz MITRE ATT&CK para empresas (MITRE, s.f.).

| N.º | Ataque | Comando o herramienta | Evidencia en registros | Regla que lo detectó | Tiempo hasta la alerta | MITRE ATT&CK |
|---|---|---|---|---|---|---|
| 1 | Reconocimiento: escaneo de puertos y servicios | `sudo nmap -sS -sV 192.168.56.10` | `eve.json` (sid 1000001 + ET SCAN); `ufw.log` ([UFW BLOCK]) | Suricata **1000001** → Wazuh **100120** | **21,1** | T1046 Network Service Discovery |
| 2 | Fuerza bruta al login de la aplicación | `hydra -l admin -P fasttrack.txt -t 4 … http-get-form` | Access log (GET repetidos a `/vulnerabilities/brute/`); `eve.json` (1000002); `active-responses.log` | Wazuh **100100 → 100101**; Suricata **1000002** → **100121** | **19,2** (alerta) · **19,2** (bloqueo) | T1110.001 Password Guessing |
| 3 | Explotación web: inyección SQL (`' UNION SELECT user, password FROM users#`) | Petición `GET` a `/vulnerabilities/sqli/` con el payload `UNION` | Access log (payload, código 200 y tamaño); `eve.json` (1000003) | Suricata **1000003** → Wazuh **100122** (nivel 12) | **4,1** | T1190 Exploit Public-Facing Application |
| 4 | Subida de web shell y modificación de archivos | Subida de `prueba.php` por *File Upload* y acceso a `/hackable/uploads/prueba.php` | `eve.json` (1000006); FIM en `/opt/dvwa/uploads` (hash SHA-256) | Suricata **1000006** → **100123**; FIM 554 → **100110** | **15,7** (FIM) · **17,2** (100123) | T1505.003 Web Shell |

**Por qué el ataque 2 es contra el login de la aplicación y no contra SSH:** SSH solo acepta llaves (2.2). Una fuerza bruta de contraseñas contra SSH no tiene nada que adivinar, y eso es evidencia de que el control funciona.

**Justificación del ataque 4:** es la continuación natural de un acceso inicial (persistencia). Permite demostrar una detección de **host** (FIM en tiempo real), además de las de red.

**Observaciones:**

- **Ataque 1:** el escaneo solo vio los puertos **22/tcp (OpenSSH 9.6p1)** y **80/tcp (nginx)**; UFW filtró (`no-response`) los 998 restantes, incluido el 3306 de MariaDB. La regla 100120 alertó a los 21,1 s.
- **Ataque 2:** hydra **no obtuvo la contraseña** (`0 valid password found`): a los ~10 intentos saltó la 100101 y `firewall-drop` insertó un `DROP` de 192.168.56.30 en la **posición 1 de INPUT**, con lo que hydra se detuvo por *too many connection errors*.
- **Ataque 3:** se extrajeron los 5 usuarios de DVWA con sus hashes MD5 (por ejemplo `admin : 5f4dcc3b…`, que es «password»). La 100122 alertó a los 4,1 s.
- **Ataque 4:** `prueba.php` se subió y **se ejecutó** (devolvió «TiendaCR prueba de integridad»). El FIM detectó el archivo `added` con SHA-256 `ab98b95a…` a los 15,7 s y la 100123 a los 17,2 s.

Las capturas de cada ataque están en el anexo B.
