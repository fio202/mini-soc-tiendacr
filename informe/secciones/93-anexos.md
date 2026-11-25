# Anexos

## Anexo A. Repositorio

**URL:** https://github.com/fio202/mini-soc-tiendacr. Contiene el `Vagrantfile` y `provision/` (las tres VM), `config/` (UFW, nginx, reglas propias de Suricata y Wazuh, respuesta activa y FIM), `scripts/alertas-ataque.py` (tiempo hasta la alerta), `docs/` (detalle de cada apartado) y `evidencias/` (salidas y capturas).

## Anexo B. Evidencias

Capturas de la ejecución real de los cuatro ataques (25/11/2026), con la salida en la terminal de la laptop y la detección extraída del SIEM. Las contraseñas y la clave del panel se mantienen fuera de cuadro.

<div class="evidencias">
<figure><img src="evidencias/agente-activo.png" alt="Agente <code>tiendacr-web</code> en estado Active (<code>agent_control -l</code> en el SIEM)"><figcaption><b>Figura B1.</b> Agente <code>tiendacr-web</code> en estado Active (<code>agent_control -l</code> en el SIEM)</figcaption></figure>
<figure><img src="evidencias/ufw-target.png" alt="UFW del objetivo: denegación por defecto y acceso solo desde las IP del equipo"><figcaption><b>Figura B2.</b> UFW del objetivo: denegación por defecto y acceso solo desde las IP del equipo</figcaption></figure>
<figure><img src="evidencias/ataque1-panel.png" alt="Ataque 1: nmap ve solo 22 y 80; alerta 100120 a los 21,1 s"><figcaption><b>Figura B3.</b> Ataque 1: nmap ve solo 22 y 80; alerta 100120 a los 21,1 s</figcaption></figure>
<figure><img src="evidencias/ataque2-panel.png" alt="Ataque 2: alerta 100101 y respuesta <code>firewall-drop</code>"><figcaption><b>Figura B4.</b> Ataque 2: alerta 100101 y respuesta <code>firewall-drop</code></figcaption></figure>
<figure><img src="evidencias/ataque2-iptables.png" alt="Ataque 2: regla DROP de Kali en la posición 1 de INPUT"><figcaption><b>Figura B5.</b> Ataque 2: regla DROP de Kali en la posición 1 de INPUT</figcaption></figure>
<figure><img src="evidencias/ataque3-panel.png" alt="Ataque 3: extracción de usuarios con hashes MD5 y alerta 100122"><figcaption><b>Figura B6.</b> Ataque 3: extracción de usuarios con hashes MD5 y alerta 100122</figcaption></figure>
<figure><img src="evidencias/ataque4-panel.png" alt="Ataque 4: ejecución del PHP subido, alerta 100123 y FIM 100110 con SHA-256"><figcaption><b>Figura B7.</b> Ataque 4: ejecución del PHP subido, alerta 100123 y FIM 100110 con SHA-256</figcaption></figure>
<figure><img src="evidencias/ataque2-despues.png" alt="Tras remediar: la fuerza bruta recibe 429 desde la 7.ª petición"><figcaption><b>Figura B8.</b> Tras remediar: la fuerza bruta recibe 429 desde la 7.ª petición</figcaption></figure>
<figure><img src="evidencias/ataque3-despues.png" alt="Tras remediar: la inyección SQL devuelve 0 filas; la 100122 sigue alertando"><figcaption><b>Figura B9.</b> Tras remediar: la inyección SQL devuelve 0 filas; la 100122 sigue alertando</figcaption></figure>
<figure><img src="evidencias/vulnerabilidades.png" alt="Detección de vulnerabilidades de Wazuh: 7.541 hallazgos (7.517 del kernel)"><figcaption><b>Figura B10.</b> Detección de vulnerabilidades de Wazuh: 7.541 hallazgos (7.517 del kernel)</figcaption></figure>
</div>
