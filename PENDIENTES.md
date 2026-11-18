# Pendientes y lista de revisión

Estado al 17/11/2026. **Entrega: 18 de noviembre.** Marquen `[x]` a medida que avancen; cada uno haga sus propios commits, porque el enunciado exige que se vean los aportes de los dos.

## 1. Bloqueante: ataques controlados (2.4 y 2.8)

- [ ] Levantar el laboratorio: `vagrant up siem && vagrant up target && vagrant up attacker`.
- [ ] Confirmar que el objetivo está en estado **vulnerable**: `vagrant provision target --provision-with vulnerable`.
- [ ] Ejecutar desde Kali (`vagrant ssh attacker`) los 4 ataques, siguiendo `docs/2.4-ataques-y-detecciones.md`.
  - [ ] Anotar la hora de inicio de cada ataque (`date "+%F %T"`).
  - [ ] Correr `python3 scripts/alertas-ataque.py 192.168.56.30 "<hora>" 3` y guardar la salida.
  - [ ] Tomar las capturas del panel y de los registros y guardarlas en `evidencias/`.
- [ ] Aplicar la remediación (`--provision-with remediate`) y repetir los ataques 2 y 3.
- [ ] Llenar `informe/secciones/24-ataques.md` y la tabla de antes y después de `informe/secciones/28-remediacion.md`.

## 2. Revisión de contenido (marcas COMPLETAR en el PDF)

- [ ] **Portada:** universidad, nombres, carnés y nombre del PDF, en el bloque `CONFIG` de `informe/build.py`.
- [ ] **Resumen ejecutivo** (`informe/secciones/00-resumen-ejecutivo.md`): cifras de los ataques.
- [ ] **2.6:** tiempo real hasta el bloqueo de Kali.
- [ ] **2.7:** nombres en los roles y plazo de la Ley 8968 (verificar los 5 días hábiles en el reglamento).
- [ ] **Conclusiones:** ajustar con los resultados reales.
- [ ] **Declaración de IA:** que refleje con exactitud cómo se usó.
- [ ] **Anexos:** URL del repositorio y capturas. El PDF tiene 19 de 20 páginas, así que las capturas deben ir pequeñas.

## 3. Verificación de la fase 1 (`docs/fase1-investigacion.md`)

- [ ] Referencia de **Guijarro et al. (2019)**: confirmar autores, año y editorial contra el programa del curso.
- [ ] Revisar las afirmaciones de la comparativa (costos y licencias) contra la documentación oficial.
- [ ] Agregar **citas en el texto** (por ejemplo, Dotson, 2019) en los párrafos; hoy solo están en la lista de referencias.
- [ ] Revisar las valoraciones de probabilidad e impacto de la matriz de riesgos (R01-R12).

## 4. Entrega

- [ ] Generar el PDF final: `.venv/bin/python informe/build.py`. Debe tener 20 páginas o menos y **0 marcas COMPLETAR**.
- [ ] Revisar la ortografía y la redacción: se descuenta 1 punto por error, hasta 10.
- [ ] Revisar que no haya credenciales en el repositorio ni en las capturas, y difuminar las IP públicas si aparecen.
- [ ] Compartir el repositorio con el profesor.
- [ ] Ensayar la demo de 10 minutos: el ataque 2 en vivo, la alerta 100101 en el panel y Kali bloqueada. Los dos deben poder explicar cualquier parte.
- [ ] Llenar la coevaluación individual.
- [ ] Al terminar: `vagrant destroy -f`.

## Mapa del repositorio

| Qué revisar | Dónde |
|---|---|
| Infraestructura | `Vagrantfile`, `provision/` |
| Configuración y reglas | `config/` |
| Documentación detallada por sección | `docs/` |
| Informe (fuente de las secciones y del PDF) | `informe/secciones/`, `informe/build.py` |
| Evidencias | `evidencias/` |
