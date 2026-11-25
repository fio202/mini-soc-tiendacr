# Coevaluación — Aportes del equipo

**Proyecto 2: Mini SOC TiendaCR** · ITI-922 Seguridad de TI II
Integrantes: Fiorella Zamora Campos y Harold Saborío Arce

> Este documento resume el aporte de cada integrante. La coevaluación oficial
> se entrega además en el formulario individual del curso; cada quien envía el suyo.

## Reparto del trabajo

| Área | Responsable principal |
|---|---|
| Infraestructura como código (Vagrant, provisión de las 3 VM) | Fiorella |
| Control de acceso (UFW, SSH con llaves, nginx, Docker en 127.0.0.1) | Fiorella |
| Monitoreo (Wazuh manager/indexer/dashboard, agente, FIM, Suricata) | Fiorella |
| Reglas propias (Suricata y Wazuh) y respuesta automática `firewall-drop` | Fiorella |
| Ejecución de los 4 ataques, evidencia y repetición tras remediar | Fiorella |
| Informe técnico, generador del PDF y repositorio | Fiorella |
| Fase 1: comparativa de herramientas y valoraciones de riesgo | Harold |
| Plan de respuesta a incidentes (roles y Ley 8968) | Harold |
| Referencias APA, citas en el texto y declaración de uso de IA | Harold |
| Portada y estilos del informe | Harold |
| Nota de riesgo residual del kernel (control C5) | Harold |

## Fiorella Zamora Campos

- Diseñó y construyó el laboratorio como código con Vagrant: las tres máquinas
  virtuales (SIEM, servidor objetivo y Kali), la red aislada y los scripts de
  aprovisionamiento.
- Configuró el control de acceso: UFW con denegación por defecto y reglas solo
  para las IP del equipo, SSH únicamente con llaves y sin root, y DVWA publicada
  solo en `127.0.0.1` detrás de nginx.
- Instaló y configuró el monitoreo: Wazuh 4.14 (manager, indexer y dashboard),
  el agente con FIM y detección de vulnerabilidades, y Suricata integrado al panel.
- Escribió las reglas propias de Suricata y de Wazuh y la respuesta automática
  `firewall-drop` (bloqueo temporal de 600 s).
- Ejecutó los cuatro ataques controlados desde Kali, recogió la evidencia y
  repitió los ataques 2 y 3 tras la remediación para la comparación antes/después.
- Armó el informe técnico (secciones, generador del PDF y tablas con los
  resultados reales) y el repositorio con el reparto de tareas.
- Usó Claude Code como asistente de configuración y documentación (declarado en
  el informe); revisó y probó todo lo generado.

## Harold Saborío Arce

- Revisó y afinó la Fase 1 de investigación: la comparativa de herramientas de
  seguridad (criterios, costos, licencias y capacidad de respuesta) y las
  valoraciones de probabilidad e impacto de la matriz de riesgos.
- Completó el plan de respuesta a incidentes (2.7): la asignación de roles con
  responsables y el plazo de la Ley 8968 de protección de datos.
- Ajustó las referencias en formato APA y agregó las citas en el texto.
- Redactó la declaración de uso de IA del informe.
- Configuró la portada y los estilos del documento en PDF.
- Redactó la nota del riesgo residual del kernel (control C5 de la remediación).
- Trabajó con su propia cuenta de GitHub mediante un *pull request*, de modo que
  los aportes de ambos quedan registrados en el historial del repositorio.

## Evidencia de los aportes en el repositorio

Los commits de ambos integrantes son visibles en el historial de
<https://github.com/fio202/mini-soc-tiendacr> (`git log`), como exige el enunciado.
