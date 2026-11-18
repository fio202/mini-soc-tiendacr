# Pendientes y reparto de trabajo

Estado al 17/11/2026. **Entrega: 18 de noviembre.** Marquen `[x]` a medida que avancen.

Cada uno sube su trabajo **con commits desde su propia cuenta**: el enunciado exige que se vean los aportes de los dos. Para no pisarse, hagan `git pull` antes de empezar y trabaje cada uno en sus propios archivos (ver la tabla del final).

---

## Compañero (HASA2005): informe y documentación (no necesita las VM)

### 0. Preparación (5 min)

- [ ] Aceptar la invitación: https://github.com/fio202/mini-soc-tiendacr/invitations
- [ ] Clonar el repositorio y preparar el generador del PDF:
  ```bash
  git clone https://github.com/fio202/mini-soc-tiendacr.git && cd mini-soc-tiendacr
  python3 -m venv .venv && .venv/bin/pip install markdown-it-py mdit-py-plugins weasyprint
  ```

### 1. Revisar la fase 1 (`docs/fase1-investigacion.md`)

- [ ] Confirmar la referencia de **Guijarro et al. (2019)** contra el programa del curso: autores, año y editorial. Está en `informe/secciones/92-referencias.md`.
- [ ] **Agregar citas en el texto** donde corresponda, por ejemplo (Dotson, 2019), (Wazuh Inc., s.f.) o (Joint Task Force Transformation Initiative, 2012). Hoy solo están en la lista final.
- [ ] Revisar en las páginas oficiales los datos de la comparativa: costos, licencias y respuesta automática.
- [ ] Revisar que las valoraciones de probabilidad e impacto de los riesgos R01 a R12 sean razonables.

### 2. Completar las partes del informe que no dependen de los ataques

- [ ] **Portada:** bloque `CONFIG` de `informe/build.py` (universidad, nombres con carné y nombre del PDF `P1_Apellido1_Apellido2.pdf`).
- [ ] **Roles** del plan de respuesta a incidentes, con los nombres: `informe/secciones/27-plan-ir.md`.
- [ ] **Plazo de la Ley 8968** (5 días hábiles), verificado en el reglamento: mismo archivo.
- [ ] **Declaración de uso de IA**, ajustada a lo que realmente hicieron: `informe/secciones/91-declaracion-ia.md`.
- [ ] **URL del repositorio** en el anexo A: `informe/secciones/93-anexos.md`.
- [ ] **Kernel** en el control C5 (`informe/secciones/28-remediacion.md`): aclarar que el kernel `6.8.0-86` no se actualizó con `apt upgrade` (requiere el kernel HWE y un reinicio) y que queda como riesgo residual del laboratorio.

### 3. Ortografía y redacción

- [ ] Revisar todo el informe: se descuenta 1 punto por error, hasta 10.
- [ ] Generar el PDF y revisarlo completo: `.venv/bin/python informe/build.py`.

### 4. Preparación para la defensa (el profesor puede preguntarle cualquier cosa)

- [ ] Entender el diagrama `docs/arquitectura.png`.
- [ ] Entender las tablas de reglas de los apartados 2.2 (firewall) y 2.5 (Suricata y Wazuh).
- [ ] Saber explicar cómo funciona la respuesta automática (2.6).
- [ ] Saber explicar por qué la alerta de SQLi **sigue apareciendo** después de remediar (2.8).

---

## Fiorella: ataques y evidencia (necesita las VM, que están en su laptop)

- [ ] Encender el laboratorio: `vagrant up siem target attacker`.
- [ ] Confirmar el estado **vulnerable**: `vagrant provision target --provision-with vulnerable`.
- [ ] Ejecutar desde Kali (`vagrant ssh attacker`) los 4 ataques, siguiendo `docs/2.4-ataques-y-detecciones.md`.
  - [ ] Anotar la hora de inicio de cada ataque (`date "+%F %T"`).
  - [ ] Correr `python3 scripts/alertas-ataque.py 192.168.56.30 "<hora>" 3` y guardar la salida.
  - [ ] Tomar las capturas del panel y de los registros y guardarlas en `evidencias/`.
- [ ] Aplicar la remediación (`--provision-with remediate`) y repetir los ataques 2 y 3.
- [ ] Llenar `informe/secciones/24-ataques.md` y la tabla de antes y después de `informe/secciones/28-remediacion.md`, más las cifras del resumen ejecutivo, del 2.6 y de las conclusiones.
- [ ] Al terminar: `vagrant halt`. Después de la entrega: `vagrant destroy -f`.

---

## Entre los dos, al final

- [ ] Ensayar juntos la demo de 10 minutos: el ataque 2 en vivo, la alerta 100101 en el panel y Kali bloqueada.
- [ ] Generar el PDF final, con **0 marcas COMPLETAR** y **20 páginas o menos**. Las capturas deben ir pequeñas: hoy el PDF tiene 19 páginas.
- [ ] Revisar que no haya credenciales en el repositorio ni en las capturas, y difuminar las IP públicas si aparecen.
- [ ] Compartir el repositorio con el profesor.
- [ ] Cada uno llena su coevaluación individual.

---

## Quién edita qué (para evitar conflictos en git)

| Compañero | Fiorella |
|---|---|
| `docs/fase1-investigacion.md` | `informe/secciones/24-ataques.md` |
| `informe/secciones/27-plan-ir.md` | `informe/secciones/28-remediacion.md`: solo la tabla de antes y después |
| `informe/secciones/91-declaracion-ia.md` | `informe/secciones/00-resumen-ejecutivo.md` |
| `informe/secciones/92-referencias.md` | `informe/secciones/25-reglas-respuesta.md`: solo el tiempo real del 2.6 |
| `informe/secciones/93-anexos.md`: anexo A | `informe/secciones/93-anexos.md`: anexo B (capturas) |
| `informe/build.py`: solo el bloque `CONFIG` | `informe/secciones/90-conclusiones.md` |
| `informe/secciones/28-remediacion.md`: solo la frase del kernel (C5) | `evidencias/` |

## Mapa del repositorio

| Qué | Dónde |
|---|---|
| Infraestructura | `Vagrantfile`, `provision/` |
| Configuración y reglas | `config/` |
| Documentación detallada por sección | `docs/` |
| Informe (fuente de las secciones y del PDF) | `informe/secciones/`, `informe/build.py` |
| Evidencias | `evidencias/` |
