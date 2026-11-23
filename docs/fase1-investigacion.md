# Fase 1. Investigación

**Escenario:** tienda en línea ficticia TiendaCR. Un servidor web con una aplicación vulnerable (DVWA en contenedor), un servidor SIEM y una máquina atacante.
**Entorno:** laboratorio local en VirtualBox. Como proveedor de referencia para los conceptos de nube se usa **AWS (Amazon EC2)**.

---

## 1.1 Comparativa de herramientas de seguridad en la nube

Se compararon **seis herramientas**:

- **dos de proveedores cloud:** AWS GuardDuty y Microsoft Defender for Cloud;
- **cuatro de código abierto:** Wazuh, Suricata, CrowdSec y Falco.

Los requisitos de recursos de Wazuh y Suricata se **midieron en nuestro laboratorio** el 17/11/2026, con 1 agente y unas 53 500 reglas de Suricata cargadas. Los demás datos se contrastaron con documentación oficial de proveedores y proyectos. Los costos dependen de funciones, volumen y región; la respuesta automática necesita configuración (Amazon Web Services, s.f.-b; Microsoft, s.f.-a, s.f.-b; Wazuh Inc., s.f.-a, s.f.-b; Open Information Security Foundation, s.f.-a; CrowdSec, s.f.-a; The Falco Project, s.f.).

| Criterio | **AWS GuardDuty** (proveedor) | **Microsoft Defender for Cloud** (proveedor) | **Wazuh** (abierto) | **Suricata** (abierto) | **CrowdSec** (abierto) | **Falco** (abierto) |
|---|---|---|---|---|---|---|
| **Qué detecta o protege** | Amenazas en la **cuenta y la red** de AWS: credenciales comprometidas, instancias que se comunican con IP maliciosas, minería, reconocimiento. Planes opcionales para S3, EKS, malware y ejecución (*runtime*). | **Configuración** (postura, CSPM) e **host** (Defender for Servers: EDR, vulnerabilidades, FIM en el plan 2). Multinube. | **Host** (registros, FIM, SCA, rootcheck, vulnerabilidades) más **SIEM** central. También **identidades**, por los registros de autenticación. | **Red**: ataques en el tráfico (HTTP, DNS, TLS, SSH…), escaneos, *exploits*, malware en tránsito. | **Comportamiento por IP** en los registros: fuerza bruta, escaneos, *scrapers*, explotación web. | **Ejecución en host y contenedores**: llamadas al sistema anómalas (shell en un contenedor, escritura en `/etc`, escalamiento). |
| **Cómo detecta** | Inteligencia de amenazas, **aprendizaje automático y anomalías** sobre CloudTrail, VPC Flow Logs y DNS. | Reglas de política (recomendaciones), análisis de comportamiento e inteligencia de Microsoft. | **Reglas y decodificadores** (XML) con correlación (frecuencia y tiempo), comparación de *hashes* (FIM) y bases de CVE. | **Firmas** (ET Open/Pro y reglas propias), análisis de protocolos y Lua. | **Escenarios** (*leaky bucket*) sobre registros analizados, más una lista de bloqueo **comunitaria**. | **Reglas** (YAML) sobre eventos del kernel vía eBPF. |
| **Modelo de despliegue y recursos** | **SaaS sin agente** para las fuentes de telemetría tradicionales; los planes de *runtime* pueden usar agente. | **SaaS** con integración por agente: servidores de Azure, otras nubes y equipos locales compatibles pueden incorporarse mediante Azure Arc o Defender for Endpoint. | Servidor central (indexer, manager y dashboard) más **agentes**. Guía oficial: 4 vCPU y 8 GB para 1-25 agentes. **Medido:** el indexer (Java) usa unos 1,7 GB de RSS; la VM SIEM usa 2,7 GB de 8 GB; el agente usa menos de 60 MB. | **Sensor** en la interfaz (AF_PACKET) o en línea como IPS. Los recursos dependen del tráfico y de las reglas. **Medido:** unos 540 MB de RSS. | Agente ligero (Go) por host, más *bouncers*. Consola central opcional (SaaS). | DaemonSet en Kubernetes o servicio en el host. Requiere eBPF o un módulo del kernel. |
| **Costo y licencia** | Propietario. **Costo variable** según fuente de datos, región, volumen y plan; prueba gratuita de 30 días para funciones elegibles. | Propietario. CSPM básico gratuito. **Defender for Servers** cobra por servidor y hora (planes 1 y 2). | **GPLv2** (manager y agente) y Apache 2.0 (indexer basado en OpenSearch). Gratuito. Soporte y Wazuh Cloud de pago. | **GPLv2** (OISF). Gratuito. ET Open es gratuito; ET Pro es de pago. | Motor **MIT**. Gratuito. Consola con plan gratuito y planes de pago. | **Apache 2.0**, proyecto CNCF *graduated*. Gratuito. |
| **Respuesta automática** | **No bloquea por sí solo.** Los hallazgos van a EventBridge y de ahí a Lambda o SSM, que actúan (por ejemplo, modificar un grupo de seguridad o una NACL). | *Workflow automation* (Logic Apps). Defender for Endpoint puede **aislar** el equipo. | **Active response**: scripts en el agente (`firewall-drop`, `disable-account`, personalizados) disparados por reglas, con *timeout*. | Solo en **modo IPS** (en línea): `drop` y `reject`. En modo IDS solo alerta. | Es su fuerte: los **bouncers** bloquean en firewall, nginx, Cloudflare y otros. | Indirecta, con Falcosidekick o Falco Talon (matar un pod, etiquetar, notificar). |
| **Integración** | Security Hub, Detective, EventBridge y SIEM externos. **Wazuh puede ingerir sus hallazgos.** | Microsoft Sentinel, Defender XDR, conectores para AWS y GCP. | Suricata, VirusTotal, GuardDuty, CloudTrail, Azure, GCP, Slack, PagerDuty, API REST. Mapeo MITRE ATT&CK. | Salida **EVE JSON** que lee cualquier SIEM (Wazuh, Elastic, Splunk). | API, *bouncers*, Prometheus, SIEM. | Falcosidekick (más de 50 destinos), Prometheus y SIEM. |
| **Limitaciones** | Enfoque AWS; no es un IDS HTTP en línea para el tráfico de TiendaCR. Costo por consumo. | Requiere integrar los servidores en Azure. Admite equipos locales compatibles mediante Azure Arc; los planes avanzados tienen cargos y requisitos específicos. | Requiere **afinar** reglas para evitar ruido. El indexer consume mucha memoria. No ve el contenido de la red por sí solo. | **No ve el tráfico cifrado** (TLS) sin terminarlo. Falsos positivos. En la nube necesita *traffic mirroring* o instalarse en el host. | Solo detecta lo que aparece en registros. No ofrece FIM ni vulnerabilidades. La lista comunitaria implica compartir señales. | Enfocado en contenedores y kernel. Sin inspección de red ni de aplicación. Las reglas por defecto son ruidosas. |

### Justificación de las herramientas elegidas

Se eligió **Wazuh + Suricata** como defensa en profundidad reproducible (Dotson, 2019; Guijarro Olivares et al., 2019):

1. **Cubren las dos capas que exige el proyecto.**
   - Suricata ve el **contenido del tráfico**, como el *payload* de una SQLi en la URI o un escaneo, cosa que GuardDuty no puede ver con metadatos de flujo.
   - Wazuh ve el **host**: autenticación, integridad de archivos y vulnerabilidades del sistema.
   - Una web shell subida se detecta en las dos capas: Suricata con el sid 1000006 y el FIM de Wazuh con la regla 100110.
2. **Wazuh funciona como SIEM central** e integra las alertas de Suricata desde `eve.json`. Así hay un solo panel, como pide el enunciado (Wazuh Inc., s.f.-a).
3. **Respuesta automática incluida** (*active response*) con scripts activados por reglas, como `firewall-drop` para bloqueos temporales (Wazuh Inc., s.f.-b).
4. **Software libre y despliegue local.** GuardDuty protege recursos AWS. Defender for Cloud puede incorporar servidores locales compatibles mediante Azure Arc, pero exige integración con su plataforma y puede generar costos. Para este laboratorio aislado se priorizaron herramientas reproducibles y sin licencias comerciales (Microsoft, s.f.-a; Microsoft, s.f.-b).
5. **Reproducibilidad.** Ambas son de código abierto, con configuración en archivos que se versionan en el repositorio.

**Descartadas o complementarias:**

- **CrowdSec:** es muy buena para el bloqueo, pero se solapa con la *active response* de Wazuh y no aporta FIM ni detección de vulnerabilidades.
- **Falco:** sería valiosa para detectar una shell **dentro** del contenedor, pero los ataques del proyecto son de red y web. Se propone como mejora.
- **En un despliegue real en AWS** se puede **sumar GuardDuty** para detectar amenazas a nivel de cuenta y servicios que no son visibles para Wazuh o Suricata. Su costo dependerá de la región, el volumen de eventos y los planes activados (Amazon Web Services, s.f.-b).

---

## 1.2 Modelo de responsabilidad compartida

**Proveedor de referencia:** AWS, servicio Amazon EC2, que es infraestructura como servicio (IaaS).

AWS distingue la seguridad **"de"** la nube, a cargo del proveedor, de la seguridad **"en"** la nube, que corresponde al cliente. En IaaS, el cliente administra el sistema operativo y las capas superiores (Amazon Web Services, s.f.-a; Dotson, 2019).

| Capa | Responsable en EC2 | Qué implica | Equivalente en nuestro laboratorio |
|---|---|---|---|
| Centros de datos, seguridad física, energía | **AWS** | Acceso físico, vigilancia, destrucción de discos. | La laptop del equipo (la protegemos nosotros) |
| Hardware, red global, hipervisor (Nitro) | **AWS** | Aislamiento entre clientes, parches del hipervisor. | VirtualBox en el anfitrión |
| Servicios administrados del proveedor (API, IAM como servicio, CloudTrail) | **AWS** opera el servicio; **el cliente** lo configura | AWS garantiza que IAM funcione; el cliente decide quién tiene permisos. | — |
| **Grupos de seguridad y NACL** | **Compartida**: AWS provee y aplica el mecanismo; **el cliente define las reglas** | Una regla `0.0.0.0/0` al puerto 22 es responsabilidad del cliente. | **UFW** con denegación por defecto (2.2) |
| **Sistema operativo invitado** (parches, usuarios, SSH) | **Cliente** | Actualizaciones, endurecimiento, llaves SSH, sin root. | Ubuntu 24.04: `00-hardening.conf`, `apt upgrade` (C5) |
| **Aplicación y contenedores** | **Cliente** | Código seguro, imágenes actualizadas, configuración. | DVWA, Docker, nginx (C1-C4) |
| **Datos** (clasificación, cifrado, respaldos) | **Cliente** (AWS ofrece herramientas como KMS y EBS cifrado) | Decidir qué se cifra y quién tiene las llaves. | Volumen `dvwa-db`; claves generadas en la VM |
| **Identidades y accesos** (usuarios IAM, MFA, llaves) | **Cliente** | Menor privilegio, MFA, rotación de llaves. | Llaves SSH, `AllowUsers`, credenciales fuera del repositorio |
| **Monitoreo y respuesta** | **Cliente** (AWS ofrece CloudTrail y GuardDuty, pero alguien debe activarlos y revisarlos) | Registrar, alertar, responder. | Wazuh + Suricata + active response |

**Consecuencias para TiendaCR:**

- **Todas** las vulnerabilidades explotadas en la fase 2 caen del lado del **cliente**: SQLi, fuerza bruta, subida de archivos, paquetes sin parchear y puertos expuestos. Ninguna se resolvería "por estar en la nube".
- Un error frecuente es suponer que el proveedor parchea el sistema operativo de una instancia EC2 o que el grupo de seguridad viene cerrado por defecto para el tráfico de la aplicación.
- **En el laboratorio local el equipo asume las dos columnas**: también somos responsables de la "seguridad física" (la laptop) y del hipervisor.

---

## 1.3 Análisis de riesgos del escenario

### Método

Se aplicó **NIST SP 800-30 Rev. 1** de forma simplificada y semicuantitativa (Joint Task Force Transformation Initiative, 2012):

1. Caracterización del sistema e **inventario de activos**.
2. Identificación de **amenazas y vulnerabilidades** por activo.
3. Estimación de la **probabilidad** (P) y del **impacto** (I) en una escala de 1 a 5.
4. **Nivel de riesgo = P × I.**
5. Puntaje **CVSS v3.1** para vulnerabilidades concretas.
6. **Tratamiento** del riesgo y **reevaluación** del riesgo residual después de aplicar los controles (punto 2.8).

**Escalas:**

| Valor | Probabilidad (P) | Impacto (I) |
|---|---|---|
| 1 Muy baja | Requiere condiciones excepcionales; no se conoce explotación. | Sin efecto apreciable en el negocio. |
| 2 Baja | Requiere acceso o conocimiento especial. | Afecta un componente no crítico; recuperación en minutos. |
| 3 Media | Hay técnicas conocidas, pero requiere esfuerzo. | Interrupción parcial o exposición de datos no sensibles. |
| 4 Alta | Hay herramientas automatizadas públicas; la exposición es directa. | Interrupción de ventas o exposición de datos de clientes. |
| 5 Muy alta | Explotable de forma trivial o ya observada. | Compromiso total, fuga masiva de datos personales o sanción legal. |

**Nivel de riesgo:** 1-4 **Bajo** · 5-9 **Medio** · 10-16 **Alto** · 20-25 **Crítico**. Los puntajes reflejan el escenario sin mitigaciones; R09 supone una probabilidad baja de falla del SIEM, mientras que R12 asigna impacto directo bajo al reconocimiento por sí solo, sin ignorar su potencial como fase previa de otros ataques.

### 1. Inventario de activos y su valor

C = confidencialidad, I = integridad, D = disponibilidad, en una escala de 1 a 5. El valor del activo es el **máximo** de las tres dimensiones.

| ID | Activo | Tipo | Ubicación | C | I | D | Valor |
|---|---|---|---|---|---|---|---|
| A1 | Aplicación web TiendaCR (DVWA) | Software | `tiendacr-web`, contenedor | 4 | 5 | 5 | **5** |
| A2 | Base de datos de clientes y usuarios (MariaDB) | Información | `tiendacr-web`, contenedor sin publicar | 5 | 5 | 4 | **5** |
| A3 | Servidor objetivo (Ubuntu, Docker, nginx) | Infraestructura | 192.168.56.10 | 4 | 5 | 5 | **5** |
| A4 | Credenciales administrativas (llaves SSH, cuentas de la app, claves de la BD y de Wazuh) | Información | VM y laptop | 5 | 5 | 3 | **5** |
| A5 | Servidor SIEM y registros de seguridad (Wazuh) | Infraestructura e información | 192.168.56.20 | 4 | 5 | 4 | **5** |
| A6 | Sensores (Suricata y agente Wazuh) | Software | `tiendacr-web` | 3 | 4 | 4 | **4** |
| A7 | Red y control de tráfico (UFW / grupo de seguridad) | Infraestructura | Ambos servidores | 3 | 5 | 4 | **5** |
| A8 | Repositorio de configuración (GitHub) | Información | Nube (GitHub) | 4 | 4 | 2 | **4** |
| A9 | Reputación y continuidad del negocio | Intangible | — | — | — | 5 | **5** |

### 2. Amenazas y vulnerabilidades por activo

| Activo | Amenaza (fuente → evento) | Vulnerabilidad | Riesgo |
|---|---|---|---|
| A1, A2 | Atacante externo → inyección SQL | Consultas SQL concatenadas sin parametrizar (nivel `low`) | R01 |
| A1, A4 | Atacante externo → fuerza bruta de contraseñas | Login sin límite de intentos, sin bloqueo y sin CSRF | R02 |
| A3, A4 | Atacante externo → fuerza bruta o acceso SSH | SSH con contraseña o root (configuración por defecto de muchas imágenes) | R03 |
| A1, A3 | Atacante externo → subida de web shell y ejecución remota | Subida sin validar tipo ni contenido; el directorio permite ejecución | R04 |
| A1, A3 | Atacante externo → path traversal o LFI | Parámetro de archivo sin lista blanca | R05 |
| A1, A9 | Atacante externo → XSS para robar la sesión de un cliente | Salida sin codificar; sin CSP | R06 |
| A2, A5, A7 | Atacante externo → acceso directo a servicios internos | Puertos de BD, indexer o panel expuestos; Docker que se salta el firewall | R07 |
| A3, A6 | Atacante → explotación de CVE conocidas | Kernel y paquetes desactualizados (total de hallazgos pendiente de verificar) | R08 |
| A5 | Atacante o falla → pérdida de visibilidad del SOC | SIEM accesible desde la red atacante; punto único de falla | R09 |
| A1, A9 | Error del propio SOC → bloqueo de clientes legítimos | Respuesta automática por umbral (falsos positivos, NAT compartido) | R10 |
| A4, A8 | Error humano → credenciales publicadas | Archivos `.env` o de claves versionados por error | R11 |
| A3, A7 | Atacante externo → reconocimiento | Servicios visibles en la red | R12 |

### 3. Matriz de riesgos (inherente)

Riesgo inherente = sin controles. El riesgo residual se calcula en el punto 2.8.

| ID | Riesgo | Activos | P | I | **Nivel** |
|---|---|---|---|---|---|
| R01 | Inyección SQL extrae datos de clientes | A1, A2 | 5 | 5 | **25 Crítico** |
| R02 | Fuerza bruta al login web | A1, A4 | 5 | 4 | **20 Crítico** |
| R03 | Fuerza bruta o acceso SSH no autorizado | A3, A4 | 4 | 5 | **20 Crítico** |
| R04 | Subida de web shell y ejecución remota | A1, A3 | 4 | 5 | **20 Crítico** |
| R05 | Path traversal o LFI lee archivos del sistema | A1, A3 | 4 | 4 | **16 Alto** |
| R06 | XSS roba la sesión de un cliente | A1, A9 | 4 | 3 | **12 Alto** |
| R07 | Servicios internos expuestos (BD, indexer, panel) | A2, A5, A7 | 4 | 5 | **20 Crítico** |
| R08 | Paquetes con vulnerabilidades conocidas | A3, A6 | 3 | 4 | **12 Alto** |
| R09 | Pérdida de visibilidad (SIEM caído o comprometido) | A5 | 2 | 4 | **8 Medio** |
| R10 | La respuesta automática bloquea clientes legítimos | A1, A9 | 3 | 3 | **9 Medio** |
| R11 | Credenciales publicadas en el repositorio | A4, A8 | 3 | 4 | **12 Alto** |
| R12 | Reconocimiento de la infraestructura | A3, A7 | 5 | 1 | **5 Medio** |

**Mapa de calor (inherente):**

| P \ I | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **5** | R12 | | | R02 | R01 |
| **4** | | | R06 | R05 | R03, R04, R07 |
| **3** | | | R10 | R08, R11 | |
| **2** | | | | R09 | |
| **1** | | | | | |

### 4. Puntaje CVSS v3.1 de vulnerabilidades reales del proyecto

Los puntajes de las vulnerabilidades de la aplicación se calcularon con la fórmula de la especificación CVSS v3.1 (FIRST, 2019) para el contexto de TiendaCR. El de CVE-2025-53537 es el que reporta la detección de vulnerabilidades de Wazuh en nuestro servidor.

| # | Vulnerabilidad | Identificador | Vector CVSS v3.1 | Base | Severidad |
|---|---|---|---|---|---|
| V1 | Inyección SQL en el parámetro `id` (módulo SQLi de DVWA, nivel `low`) | **OWASP A03:2021 Injection**, CWE-89 | `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N` | **8.1** | Alta |
| V2 | Subida de archivos sin restricción, que permite una web shell | **OWASP A04:2021 Insecure Design**, CWE-434 | `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H` | **8.8** | Alta |
| V3 | Login sin límite de intentos (fuerza bruta) | **OWASP A07:2021 Identification and Authentication Failures**, CWE-307 | `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N` | **7.1** | Alta |
| V4 | Path traversal / LFI en el parámetro `page` | **OWASP A01:2021 Broken Access Control**, CWE-22 | `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` | **6.5** | Media |
| V5 | Fallo en `libhtp2` 0.5.46 (el analizador HTTP que usa **Suricata**): tráfico manipulado puede afectar su disponibilidad | **CVE-2025-53537** | `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` | **7.5** | Alta |

**Justificación de las métricas:**

- **AV:N:** todas son explotables por la red.
- **AC:L:** no requieren condiciones especiales.
- **PR:L** (V1 a V4): los módulos de DVWA exigen una sesión iniciada; como DVWA trae credenciales por defecto, ese privilegio es fácil de obtener. V5 no requiere autenticación (**PR:N**).
- **UI:N:** no hace falta que la víctima haga nada.
- **Impacto de V1:** lectura de toda la tabla de usuarios (C:H) y posibilidad de modificarla (I:H).
- **Impacto de V2:** ejecución de código como `www-data` (C:H, I:H, A:H).
- **Impacto de V3:** obtener la contraseña da acceso completo a la cuenta (C:H) con modificación limitada (I:L).
- **Impacto de V5:** solo afecta la disponibilidad del IDS (A:H).

**Hallazgos de la detección de vulnerabilidades de Wazuh** (agente `tiendacr-web`, 17/11/2026):

- El borrador indica **6.904 hallazgos**, pero las categorías anotadas (238 críticas, 2.241 altas, 2.517 medias y 250 bajas) suman **5.246**. Falta conciliar el total con un solo corte temporal del panel Wazuh antes de reportar cifras definitivas.
- Casi todas corresponden al **kernel** `linux-image-6.8.0-86` que trae la imagen base, con puntajes de hasta 10.0.
- Fuera del kernel solo aparecen `libhtp2` (V5) y `suricata-update`.
- **Lección:** el IDS también es superficie de ataque. En este laboratorio, `apt upgrade` no dejó actualizado el kernel `6.8.0-86`: queda pendiente instalar una versión HWE compatible, reiniciar y reevaluar las CVE.

### 5. Plan de tratamiento

| ID | Nivel inherente | Opción | Control propuesto | Responsable | Se implementa en |
|---|---|---|---|---|---|
| R01 | 25 | **Mitigar** | Consultas preparadas (nivel *impossible* forzado); detección con Suricata 1000003/4 y Wazuh 100122 | Integrante 1 | 2.5, 2.8 (C1) |
| R02 | 20 | **Mitigar** | Límite de velocidad (429), bloqueo de cuenta y CSRF; regla 100101 con `firewall-drop` | Integrante 2 | 2.5, 2.6, 2.8 (C1, C2) |
| R03 | 20 | **Mitigar** | SSH solo con llaves, sin root, `AllowUsers`, solo desde IP del equipo; regla 5763 con `firewall-drop` | Integrante 1 | 2.2, 2.6 |
| R04 | 20 | **Mitigar** | Validación de subidas (C1); 403 a PHP en subidas (C3); FIM 100110; Suricata 1000006 | Integrante 2 | 2.3, 2.5, 2.8 (C3) |
| R05 | 16 | **Mitigar** | Lista blanca de archivos (C1); Suricata 1000005 | Integrante 1 | 2.5, 2.8 |
| R06 | 12 | **Mitigar** | Codificación de salida (C1); cabeceras CSP (C4) | Integrante 2 | 2.8 (C4) |
| R07 | 20 | **Evitar** y mitigar | **Evitar:** la aplicación vulnerable nunca se publica en internet (red solo-anfitrión). **Mitigar:** denegación por defecto, BD sin publicar, Docker solo en `127.0.0.1` | Integrante 1 | 2.1, 2.2 |
| R08 | 12 | **Mitigar parcialmente** | Parches disponibles y revisión de imágenes; actualización efectiva del kernel y reinicio aún pendientes; seguimiento en *Vulnerability Detection* | Integrante 2 | 2.3, 2.8 (C5) |
| R09 | 8 | **Aceptar** (laboratorio) / **Transferir** (producción) | SIEM en una VM separada con firewall propio. En producción: servicio gestionado (Wazuh Cloud) con un acuerdo de disponibilidad | Integrante 1 | 2.2 |
| R10 | 9 | **Aceptar** (monitoreado) | Bloqueo temporal de 600 s, lista blanca, solo reglas de alta certeza | Integrante 2 | 2.6 |
| R11 | 12 | **Mitigar** | `.gitignore`, claves generadas dentro de las VM, revisión antes de cada commit | Ambos | Repositorio |
| R12 | 5 | **Aceptar** | Superficie mínima; detección con Suricata 1000001 y Wazuh 100120 (solo alerta, sin bloqueo, para evitar suplantación de origen) | Integrante 1 | 2.5 |

En producción, una **transferencia** adicional sería una póliza de ciberseguro para el impacto financiero de una fuga de datos (R01). La reevaluación con el **riesgo residual** está en `docs/2.8-remediacion-y-reevaluacion.md`.

---

Las referencias de esta fase están en `informe/secciones/92-referencias.md`.
