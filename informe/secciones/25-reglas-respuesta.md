# 2.5 Reglas propias

El enunciado pide como mínimo 2 reglas de Suricata y 1 de Wazuh. Se crearon **6 reglas de detección en Suricata** (más una de verificación de la cadena IDS → SIEM) y **9 en Wazuh**. Cada una responde a un ataque de la tabla 2.4. No hizo falta un decodificador propio: nginx usa el nativo `web-accesslog` y Suricata el de JSON. El texto completo de las reglas está en `config/` del repositorio (anexo A).

**Tabla 1. Reglas propias de Suricata** (`config/suricata/local.rules`)

| sid | Ataque | Lógica de detección | MITRE ATT&CK |
|---|---|---|---|
| 1000001 | 1. Escaneo | Paquetes solo SYN; `detection_filter` de 25 en 10 s por IP de origen | T1046 |
| 1000002 | 2. Fuerza bruta | `/vulnerabilities/brute/` con `password=`; 10 en 60 s por IP de origen | T1110.001 |
| 1000003 | 3. SQLi | `union` … `select` en la URI normalizada | T1190 |
| 1000004 | 3. SQLi | PCRE de tautología (`' or 'x'='x`, `' and 1=1`) | T1190 |
| 1000005 | 3. Path traversal | `../` repetido hacia `etc/passwd`, `etc/shadow` o `proc/self` | T1190 |
| 1000006 | 4. Web shell | POST a `/upload` cuyo cuerpo contiene `<?php` | T1505.003 |

**Tabla 2. Reglas propias de Wazuh** (`config/wazuh-manager/tiendacr_rules.xml`)

| ID | Nivel | Regla padre | Qué detecta | Ataque | MITRE ATT&CK |
|---|---|---|---|---|---|
| 100100 | 3 | 31100 (access log) | Cada intento de login web | 2 | — |
| **100101** | **10** | Correlación de 100100 | 10 intentos en 60 s desde la misma IP → **respuesta activa** | 2 | T1110.001 |
| 100110 | 12 | 554 (FIM: archivo nuevo) | Archivo nuevo en `/opt/dvwa/uploads` | 4 | T1505.003 |
| 100111 | 10 | 550 (FIM: modificado) | Archivo modificado en las subidas | 4 | T1505.003 |
| 100112 | 12 | 550 / 554 | Cambio en `authorized_keys` (persistencia) | 4 | T1098.004 |
| 100120 | 8 | 86601 (Suricata) | Eleva el sid 1000001 | 1 | T1046 |
| 100121 | 10 | 86601 | Eleva el sid 1000002 | 2 | T1110.001 |
| 100122 | 12 | 86601 | Eleva los sids 1000003 a 1000005 | 3 | T1190 |
| 100123 | 12 | 86601 | Eleva el sid 1000006 | 4 | T1505.003 |

**Validación:**

- `suricata -T` cargó **53 508 reglas, con 0 fallos** (53 501 de ET Open más 7 propias).
- Con `wazuh-logtest`, una línea de acceso a `/vulnerabilities/brute/` activa la regla **100100**, un JSON con el sid 1000003 activa la **100122** (nivel 12, T1190) y uno con el sid 1000001 activa la **100120** (T1046).

**Lección aprendida:** OS_Regex de Wazuh **no admite clases de caracteres** como `[345]`. La primera versión de la regla 100122 nunca se activaba; `wazuh-logtest` lo reveló y se corrigió con alternativas (`^1000003$|^1000004$|^1000005$`).

# 2.6 Respuesta automática

**Configuración:**

| Parámetro | Valor |
|---|---|
| Comando | `firewall-drop` (iptables, cadenas INPUT y FORWARD) |
| Disparadores | 100101 (fuerza bruta web) y 5763 (fuerza bruta SSH, regla nativa) |
| Dónde se aplica | Solo el agente 001 |
| Duración del bloqueo | 600 s |
| Lista blanca | 127.0.0.1, .1 (laptop) y .20 (SIEM) |

**Prueba controlada:** se escribieron 11 líneas sintéticas en el access log con una IP inexistente (.99), sin tráfico real.

| Momento | Evento |
|---|---|
| 19:40:34.425 | Primera línea escrita en el access log |
| 19:40:35.108 | Alerta **100101** en el SIEM |
| 19:40:35.496 | `DROP` aplicado en el objetivo (**1,07 s** en total) |

La regla DROP quedó en la **posición 1 de INPUT**, antes de las cadenas de UFW, así que bloquea incluso a una IP que UFW permite. Con el ataque real: ✏️ s hasta el bloqueo de Kali.

**Riesgo de bloquear tráfico legítimo:**

1. **Falsos positivos por umbral:** un usuario que olvida su clave o un monitor automatizado pueden generar el mismo patrón.
2. **IP compartidas (NAT corporativo):** bloquear una IP puede bloquear a muchos clientes.
3. **Suplantación de origen:** en ataques sin conexión (SYN), un atacante puede hacer que el SOC bloquee a un tercero. Por eso el escaneo (100120) **solo alerta**.
4. **Autobloqueo del SOC:** si el SIEM o el analista quedan bloqueados, se pierde visibilidad.

**Mitigaciones aplicadas:**

- Bloqueo temporal.
- Lista blanca.
- Solo reglas correlacionadas de alta certeza.
- Bloqueo solo en el servidor atacado.
- Cada bloqueo queda registrado en `active-responses.log`.

**Mejora propuesta para producción:**

- Primero un límite de velocidad o un CAPTCHA, y bloqueo solo si el patrón continúa.
- Aprobación humana para bloqueos de más de 1 h.
