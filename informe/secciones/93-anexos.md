# Anexos

## Anexo A. Repositorio

**URL:** https://github.com/fio202/mini-soc-tiendacr. Contiene el `Vagrantfile` y `provision/` (las tres VM), `config/` (UFW, nginx, reglas propias de Suricata y Wazuh, respuesta activa y FIM), `scripts/alertas-ataque.py` (tiempo hasta la alerta), `docs/` (detalle de cada apartado) y `evidencias/` (salidas y capturas).

## Anexo B. Evidencias

Capturas del laboratorio, con las contraseñas fuera de cuadro. La salida completa de cada ataque (`alertas-ataque.py`) está en `evidencias/ataqueN.txt`.

<div class="evidencias">
<figure><img src="evidencias/agente-activo.png" alt="B1"><figcaption><b>Figura B1.</b> Agente <code>tiendacr-web</code> activo en el panel</figcaption></figure>
<figure><img src="evidencias/ufw-target.png" alt="B2"><figcaption><b>Figura B2.</b> <code>ufw status verbose</code> del servidor objetivo</figcaption></figure>
<figure><img src="evidencias/ataque1-panel.png" alt="B3"><figcaption><b>Figura B3.</b> Ataque 1: alertas de escaneo (1000001, 100120)</figcaption></figure>
<figure><img src="evidencias/ataque2-panel.png" alt="B4"><figcaption><b>Figura B4.</b> Ataque 2: alerta 100101 y respuesta <code>firewall-drop</code></figcaption></figure>
<figure><img src="evidencias/ataque2-iptables.png" alt="B5"><figcaption><b>Figura B5.</b> Ataque 2: regla DROP en la posición 1 de INPUT</figcaption></figure>
<figure><img src="evidencias/ataque3-panel.png" alt="B6"><figcaption><b>Figura B6.</b> Ataque 3: alerta 100122 de inyección SQL</figcaption></figure>
<figure><img src="evidencias/ataque4-panel.png" alt="B7"><figcaption><b>Figura B7.</b> Ataque 4: alerta FIM 100110 con el hash SHA-256</figcaption></figure>
<figure><img src="evidencias/ataque2-despues.png" alt="B8"><figcaption><b>Figura B8.</b> Después de remediar: respuestas 429 en la fuerza bruta</figcaption></figure>
<figure><img src="evidencias/ataque3-despues.png" alt="B9"><figcaption><b>Figura B9.</b> Después de remediar: la inyección SQL no devuelve filas</figcaption></figure>
<figure><img src="evidencias/vulnerabilidades.png" alt="B10"><figcaption><b>Figura B10.</b> Detección de vulnerabilidades de Wazuh (agente <code>tiendacr-web</code>)</figcaption></figure>
</div>
