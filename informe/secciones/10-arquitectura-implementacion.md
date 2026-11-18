# 2.1 Arquitectura y despliegue

<figure>
<img src="docs/arquitectura.png" alt="Arquitectura del mini SOC TiendaCR">
<figcaption>Figura 1. Arquitectura del mini SOC TiendaCR (elaboración propia).</figcaption>
</figure>

## Componentes

| VM | IP | Recursos | Sistema | Contenido |
|---|---|---|---|---|
| `tiendacr-web` (objetivo) | 192.168.56.10 | 2 vCPU, 4 GB | Ubuntu Server 24.04 LTS | DVWA y MariaDB en Docker Compose; nginx como proxy inverso; Suricata 7.0.3; agente Wazuh 4.14 |
| `tiendacr-siem` | 192.168.56.20 | 4 vCPU, 8 GB | Ubuntu Server 24.04 LTS | Wazuh 4.14 *all-in-one* (indexer, manager y dashboard) |
| `tiendacr-kali` (atacante) | 192.168.56.30 | 2 vCPU, 4 GB | Kali Linux 2026.2 | Herramientas de pruebas de penetración |
| Laptop (anfitrión) | 192.168.56.1 | — | Fedora + VirtualBox 7.2 + Vagrant 2.4 | Administración y panel del SOC |

La red es **solo-anfitrión** (192.168.56.0/24). La aplicación vulnerable nunca queda expuesta a internet.

## Despliegue reproducible

Todo el entorno se define como código en el repositorio y se levanta con tres comandos:

```bash
vagrant up siem      # Wazuh all-in-one + firewall del SIEM
vagrant up target    # DVWA, nginx, Suricata, agente Wazuh + firewall del objetivo
vagrant up attacker  # Kali Linux
```

| Script | Función |
|---|---|
| `provision/common.sh` | Endurecimiento de SSH y UFW con denegación por defecto (ambos servidores) |
| `provision/siem.sh` | Instalación de Wazuh y reglas de firewall del SIEM |
| `provision/target.sh` | Contenedores, nginx, Suricata (reglas ET Open más las propias) y agente |
| `provision/siem-rules.sh`, `target-rules.sh` | Despliegue de reglas propias y respuesta activa (con validación previa) |
| `provision/remediation.sh` | Alterna entre el estado vulnerable y el remediado (2.8) |

Las credenciales (claves de Wazuh y de la base de datos) se generan **dentro de las VM** y nunca se versionan.

## Problemas encontrados durante el despliegue

| Problema | Causa | Solución |
|---|---|---|
| Fallo al descargar las imágenes de Docker | DNS intermitente a través del NAT de VirtualBox | Resolver DNS del anfitrión (`natdnshostresolver1`) y reintentos en la descarga |
| La base de datos de DVWA no se creaba de forma automática | El formulario responde con una redirección (302); el mensaje de éxito aparece después | Seguir la redirección y reintentar hasta ver "Setup successful" |
| Error de Suricata al validar la configuración | En Suricata, `-q` no significa "silencioso" sino "cola NFQ" | Se quitó el parámetro |
| Docker se salta UFW al publicar puertos | Docker inserta reglas propias de iptables | DVWA se publica solo en `127.0.0.1`; nginx es el único punto de entrada |
| Una regla de Wazuh nunca se activaba | OS_Regex no admite clases de caracteres (`[345]`) | Alternativas con `|`, verificadas con `wazuh-logtest` |
