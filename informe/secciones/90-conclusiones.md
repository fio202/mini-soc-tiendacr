# Conclusiones

<span class="todo">COMPLETAR: revisar y ajustar con los resultados reales de los ataques.</span>

1. **La defensa en profundidad funcionó como se esperaba.**
   - Las detecciones de red (Suricata) y de host (Wazuh) se complementan.
   - Una subida de web shell la detectan las dos capas: Suricata con el sid 1000006 y el FIM con la regla 100110.
   - Un escaneo solo lo ve la red, y un cambio en `authorized_keys` solo lo ve el host.
2. **El control de acceso redujo la superficie antes de monitorear.**
   - Con denegación por defecto, el atacante solo vio los puertos 22 y 80 (<span class="todo">COMPLETAR con el resultado del escaneo</span>).
   - Con SSH solo con llaves, la fuerza bruta contra SSH deja de ser viable.
3. **Detectar no es lo mismo que prevenir.** Después de la remediación, el IDS siguió alertando los intentos de SQLi. El éxito de la remediación se mide por el impacto (sin datos extraídos), no por la ausencia de alertas.
4. **La respuesta automática es eficaz, pero tiene un costo.** Bloqueó al atacante en <span class="todo">COMPLETAR</span> s. Por el riesgo de bloquear clientes legítimos se limitó a reglas de alta certeza, con bloqueo temporal y lista blanca.
5. **Las herramientas de seguridad también son superficie de ataque.** Wazuh detectó la CVE-2025-53537 en la librería HTTP de Suricata y 6904 CVE en el kernel de la imagen base. Mantener parchado el propio SOC es parte del trabajo.
6. **Infraestructura como código.** Definir el SOC en Vagrant y en scripts permitió reconstruirlo, alternar entre el estado vulnerable y el remediado, y documentar cada control de forma verificable.

**Trabajo futuro:**

- WAF con ModSecurity y OWASP CRS.
- Suricata en modo IPS.
- Falco para detectar actividad dentro de los contenedores.
- MFA en el inicio de sesión.
- Respaldos cifrados.
- En la nube: AWS GuardDuty, integrado con Wazuh.
