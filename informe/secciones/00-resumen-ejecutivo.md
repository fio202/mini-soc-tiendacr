# Resumen ejecutivo

TiendaCR, una tienda en línea ficticia, no contaba con capacidad de detección ni de respuesta ante ataques a su servidor web. El equipo diseñó, desplegó y operó un **mini centro de operaciones de seguridad (SOC)** en un laboratorio local de VirtualBox. Consta de tres máquinas:

- un **servidor objetivo** con la aplicación vulnerable DVWA en contenedores;
- un **servidor SIEM** con Wazuh 4.14;
- una **máquina atacante** con Kali Linux.

Las tres se aprovisionan de forma reproducible con Vagrant.

**Investigación (fase 1):**

- Se compararon seis herramientas de seguridad: dos de proveedores cloud y cuatro de código abierto.
- Se eligió **Wazuh** (monitoreo de host y SIEM) junto con **Suricata** (IDS de red), porque cubren las capas de host y de red, ofrecen respuesta automática y no tienen costo.
- El análisis de riesgos con **NIST SP 800-30** identificó **12 riesgos**: 5 críticos, 4 altos y 3 medios.
- Se calcularon los puntajes **CVSS v3.1** de cinco vulnerabilidades reales, incluida la **CVE-2025-53537**, presente en el propio IDS.

**Implementación (fase 2):**

- **Control de acceso:** denegación por defecto en ambos servidores, acceso solo desde las IP del equipo y SSH solo con llaves.
- **Reglas propias:** 6 reglas de detección en Suricata y 9 en Wazuh, todas con su técnica MITRE ATT&CK.
- **Respuesta automática:** bloquea la IP atacante en el firewall. En la prueba controlada actuó en **1,07 s**.

- De los cuatro ataques controlados ejecutados, **se detectaron los cuatro**, cada uno con su regla propia y su técnica MITRE ATT&CK.
- El tiempo medio hasta la primera alerta fue de **15 s** (de 4,1 s en la SQLi a 21,1 s en el escaneo).
- La respuesta automática bloqueó al atacante **19,2 s** después del inicio de la fuerza bruta (la ejecución del bloqueo, desde la alerta, tardó ~1 s).

**Resultado:**

- Después de la remediación (nivel de seguridad *impossible*, límite de velocidad en el login, prohibición de ejecutar PHP en las subidas, cabeceras de seguridad y actualizaciones), la repetición de los ataques 2 y 3 **no obtuvo contraseña ni datos**: la fuerza bruta recibió 429 y la inyección SQL devolvió 0 filas.
- El riesgo residual baja a **0 críticos y 1 alto** (R08, por el kernel sin actualizar): quedan 8 medios y 3 bajos.

**Recomendaciones principales para producción:**

- WAF con OWASP CRS.
- MFA en el inicio de sesión.
- Respaldos cifrados.
- Activar AWS GuardDuty si la tienda se migra a la nube.
