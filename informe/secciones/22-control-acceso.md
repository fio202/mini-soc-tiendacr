# 2.2 Control de acceso y de tráfico

En el laboratorio local, el grupo de seguridad se implementa con **UFW** en cada servidor. La política es `deny incoming` y `deny routed` por defecto. **Ninguna regla usa `0.0.0.0/0`**: todas fijan la IP de origen, la interfaz, el puerto y el protocolo. El detalle y los comandos de verificación están en `docs/2.2-control-de-acceso.md`.

| ID | Servidor | Acción | Origen → destino | Justificación | Riesgo que mitiga | Principio |
|---|---|---|---|---|---|---|
| D0 | Ambos | DENY | Cualquiera → cualquiera | Todo lo no permitido se descarta (BD, 9200, 55000, puertos de Docker) | R07 exposición de servicios | Denegación por defecto |
| R00 | Ambos | ALLOW | 10.0.2.2 (NAT VirtualBox) → 22/tcp | Canal de gestión de Vagrant, no alcanzable desde la red del laboratorio | Pérdida de administración | Menor privilegio |
| R01 | Objetivo | ALLOW | .1 y .30 → 22/tcp | SSH solo desde equipos del equipo | R03 acceso SSH no autorizado | Menor privilegio |
| R02 | Objetivo | ALLOW | .1 y .30 → .10:80/tcp | La aplicación vulnerable solo es accesible para el equipo | R01-R06 explotación por terceros | Menor privilegio |
| R01 | SIEM | ALLOW | .1 → 22/tcp | Kali **no** tiene acceso al SIEM | R09 compromiso del SIEM | Separación de funciones |
| R10/R11 | SIEM | ALLOW | .10 → 1514 y 1515/tcp | Eventos y registro **solo** del agente monitoreado | Inyección de eventos falsos | Menor privilegio |
| R12 | SIEM | ALLOW | .1 → 443/tcp | Panel solo para el analista | Acceso al panel por terceros | Menor privilegio |
| — | Objetivo | (sin regla) | DVWA publicado en `127.0.0.1:4280`; MariaDB sin publicar | Docker se salta UFW si publica en `0.0.0.0`; nginx es el único punto de entrada | R07 | Defensa en profundidad |

**SSH (ambos servidores):** archivo `00-hardening.conf`. Lleva el prefijo 00 porque sshd aplica el primer valor que lee.

- `PasswordAuthentication no`
- `KbdInteractiveAuthentication no`
- `PermitRootLogin no`
- `MaxAuthTries 3`
- `AllowUsers vagrant`

**Verificación:**

- `sshd -T` confirma los valores.
- Un intento de inicio de sesión con contraseña es rechazado con `Permission denied (publickey)`.
- Desde la laptop, los puertos 9200 del SIEM y 3306 del objetivo aparecen **bloqueados**.
- Desde Kali, el panel del SIEM (443) aparece **bloqueado**.
