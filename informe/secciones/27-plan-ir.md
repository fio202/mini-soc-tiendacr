# 2.7 Plan de respuesta a incidentes

**Incidente de referencia:** inyección SQL contra la aplicación de TiendaCR (ataque 3; T1190).
**Marco:** NIST SP 800-61 Rev. 2.
**Escalamiento por severidad:**

| Severidad | Criterio | Escalamiento |
|---|---|---|
| **SEV-1** | Explotación exitosa (datos extraídos o web shell, regla 100110) | IR lead y gerencia de inmediato |
| **SEV-2** | Intento dirigido sin evidencia de éxito (alertas 100122 sin datos filtrados) | IR lead en 15 min |
| **SEV-3** | Reconocimiento o fuerza bruta bloqueada automáticamente | Revisión en el turno |
| **SEV-4** | Evento aislado | Solo registro |

**Roles:**

| Rol | Responsabilidades | Titular | Suplente |
|---|---|---|---|
| Analista SOC (N1) | Triaje de alertas, apertura del incidente, evidencia inicial | ✏️ Integrante 1 | ✏️ Integrante 2 |
| Responsable de incidentes (IR lead) | Severidad, decisiones de contención, bitácora, cierre | ✏️ Integrante 2 | ✏️ Integrante 1 |
| Administrador de sistemas | Contención y erradicación (firewall, contenedores, nginx) | ✏️ Integrante 1 | ✏️ Integrante 2 |
| Gerencia de TiendaCR (simulado) | Aprobar sacar la tienda de línea; comunicación externa | — | — |
| Asesoría legal (simulado) | Evaluar las obligaciones de notificación (Ley 8968) | — | — |

**Procedimiento:**

| Fase | Acciones clave | Responsable | Tiempo objetivo |
|---|---|---|---|
| **1. Preparación** | Visibilidad: Suricata 1000003-1000005, Wazuh 100122 y el access log en el host. Superficie mínima (2.2). Inventario de activos (1.3). Provisionador `remediate` listo. Plantilla de bitácora. Respaldo del volumen de la BD. Canal de comunicación fuera de banda. | Todo el equipo | Antes del incidente |
| **2. Detección y análisis** | Confirmar la alerta 100122: IP de origen, URI, hora y firma. Correlacionar con el access log: un **código 200 con una respuesta más grande de lo normal** indica éxito (SEV-1). Buscar actividad posterior desde esa IP (100110, 100112). Clasificar y notificar. | Analista N1 | Detección ≤ 5 min; triaje ≤ 15 min |
| **3. Contención** | Bloquear la IP de origen (`iptables -I INPUT 1 … DROP`). Parche virtual inmediato: nivel *impossible* forzado en nginx. En SEV-1 con ejecución de código: detener el contenedor con la aprobación de la gerencia. **Preservar la evidencia** (registros, `eve.json`, subidas) con hashes SHA-256 antes de cambiar nada más. | IR lead y administrador | ≤ 30 min (SEV-1) |
| **4. Erradicación** | Corregir la causa raíz (consultas preparadas, validación de entradas). Si se leyó la tabla `users`, **resetear todas las contraseñas** (MD5 sin sal) y la clave de la BD. Buscar persistencia (subidas, FIM de las últimas 24 h, procesos y contenedores). Actualizar el host y la imagen. Agregar detección para variantes no cubiertas. | Administrador | ≤ 4 h |
| **5. Recuperación** | Restaurar la BD desde un respaldo íntegro si hubo alteración. Levantar la aplicación con los controles. **Repetir el ataque de forma controlada:** no debe devolver datos y la alerta debe seguir apareciendo. Vigilancia reforzada durante 72 h. Cierre por el IR lead y reapertura aprobada por la gerencia. | IR lead | ≤ 8 h |
| **6. Lecciones aprendidas** | Reunión en un plazo de 5 días hábiles: tiempos reales frente a objetivos, contexto de las alertas, causa raíz y controles que faltaron (por ejemplo, un WAF con OWASP CRS). | Todo el equipo | ≤ 5 días hábiles |

**Lecciones ya incorporadas:**

- **Un IDS detecta el intento, no el éxito.** El triaje debe revisar la respuesta HTTP para distinguir SEV-1 de SEV-2.
- **Se agregó la prohibición de ejecutar PHP en las subidas (C3)**, porque una SQLi exitosa suele seguirse de una web shell.

**Notificación:** si hubiera datos personales reales, la Ley 8968 de Costa Rica y su reglamento obligan a informar a los titulares y a la PRODHAB en el plazo que fija el reglamento (✏️ verificar: 5 días hábiles). En el laboratorio no aplica.

El procedimiento detallado, con comandos y plantilla de bitácora, está en `docs/2.7-plan-respuesta-incidentes.md`.
