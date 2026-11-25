# 2.8 Remediación y reevaluación

Los controles se aplican y se revierten con el mismo provisionador:

- `vagrant provision target --provision-with remediate` aplica el estado remediado.
- `--provision-with vulnerable` vuelve al estado original.

Así, los ataques 2 y 3 se repiten en idénticas condiciones antes y después.

| # | Vulnerabilidad | Control aplicado | Verificación (sin tráfico de ataque) |
|---|---|---|---|
| C1 | La aplicación en nivel `low`: SQLi, traversal y login sin protección | Nivel **impossible** (consultas preparadas, token anti-CSRF, bloqueo de cuenta). nginx **reescribe la cookie `security`** para que el cliente no pueda bajarlo. | Con la cookie `security=low`, la aplicación muestra **impossible** |
| C2 | Intentos de login ilimitados | `limit_req` de 10 por minuto por IP (ráfaga de 5) en `/login.php` y `/vulnerabilities/brute/` → **429** | `200 200 200 200 429 429 …` |
| C3 | Ejecución de archivos subidos | **403** a `.php`, `.phtml` y `.phar` bajo `/hackable/uploads/` | 403 |
| C4 | Clickjacking, MIME sniffing y XSS | Cabeceras CSP, `X-Frame-Options`, `X-Content-Type-Options` y `Referrer-Policy` | Las 4 presentes |
| C5 | Paquetes con CVE | `apt upgrade` y revisión de imágenes; instalar un kernel HWE compatible y reiniciar siguen pendientes. | 7.541 hallazgos (7.517 del kernel 6.8.0-86) siguen en el panel |

**Riesgo residual C5:** el kernel `6.8.0-86` **no quedó actualizado** con `apt upgrade` en la evidencia disponible. Es necesario instalar el kernel HWE compatible, reiniciar el servidor, verificar `uname -r` y volver a revisar las CVE con Wazuh. Hasta entonces, las vulnerabilidades asociadas al kernel permanecen como riesgo residual y **debe revisarse el puntaje R08** antes de afirmar que todos los riesgos altos desaparecieron.

**Comparación antes / después** (misma herramienta y mismos parámetros):

| Ataque | Antes | Después | Detección después |
|---|---|---|---|
| 2. Fuerza bruta | Respuestas **200**; a los ~10 intentos salta la 100101 y `firewall-drop` bloquea a Kali. **No** se obtuvo contraseña | Respuestas **200** solo las primeras 6; desde la **7.ª** petición nginx responde **429**. **Sin contraseña** | 100100/100101 y los 4xx por el límite de velocidad |
| 3. SQLi | Se extraen los **5 usuarios con sus hashes MD5** | **0 filas extraídas** (consultas preparadas, nivel *impossible*) | **100122 sigue apareciendo** (T+46,9 s): el IDS ve el intento |

> **Punto clave:** después de remediar, la alerta de SQLi no desaparece, y eso es correcto. El IDS ve el *intento*. La reevaluación se mide por el **impacto** (datos o contraseña obtenidos), no por la ausencia de alertas.

**Riesgo residual:** los ID y las valoraciones inherentes coinciden con la matriz de la sección 1.3.

| ID | Riesgo | Inherente | Controles principales | P | I | **Residual** | Tratamiento |
|---|---|---|---|---|---|---|---|
| R01 | Inyección SQL | 25 Crítico | C1, Suricata 1000003/4, Wazuh 100122 | 1 | 5 | **5 Medio** | Mitigar |
| R02 | Fuerza bruta al login web | 20 Crítico | C1, C2, 100101 + firewall-drop | 2 | 4 | **8 Medio** | Mitigar |
| R03 | Acceso SSH no autorizado | 20 Crítico | Solo llaves, sin root, IP del equipo, 5763 + firewall-drop | 1 | 5 | **5 Medio** | Mitigar |
| R04 | Web shell y ejecución remota | 20 Crítico | C1, C3, FIM 100110, Suricata 1000006 | 1 | 5 | **5 Medio** | Mitigar |
| R05 | Path traversal / LFI | 16 Alto | C1, Suricata 1000005 | 1 | 4 | **4 Bajo** | Mitigar |
| R06 | XSS con robo de sesión | 12 Alto | C1, C4 | 2 | 3 | **6 Medio** | Mitigar |
| R07 | Servicios internos expuestos | 20 Crítico | Denegación por defecto, BD sin publicar, Docker en 127.0.0.1 | 1 | 5 | **5 Medio** | Evitar y mitigar |
| R08 | Paquetes vulnerables | 12 Alto | C5 parcial (kernel sin actualizar), detección de vulnerabilidades | 3 | 4 | **12 Alto** | Mitigar parcialmente |
| R09 | Pérdida de visibilidad del SIEM | 8 Medio | SIEM separado con firewall propio | 1 | 4 | **4 Bajo** | Aceptar (laboratorio) / Transferir (producción) |
| R10 | La respuesta automática bloquea clientes | 9 Medio | Bloqueo de 600 s, lista blanca, alta certeza | 2 | 3 | **6 Medio** | Aceptar |
| R11 | Credenciales en el repositorio | 12 Alto | `.gitignore`, claves generadas en las VM | 1 | 4 | **4 Bajo** | Mitigar |
| R12 | Reconocimiento | 5 Medio | Superficie mínima, detección 1000001/100120 | 5 | 1 | **5 Medio** | Aceptar |

**Resultado:**

- Antes de los controles: **5 críticos, 4 altos y 3 medios**.
- Después: **0 críticos y 1 alto** (R08, por el kernel sin actualizar); quedan 8 medios y 3 bajos.

**Mejoras pendientes:**

- Instalar el kernel HWE, reiniciar y reevaluar R08 con Wazuh.
- WAF con ModSecurity y OWASP CRS.
- MFA.
- Respaldos cifrados.
- Suricata en modo IPS.
