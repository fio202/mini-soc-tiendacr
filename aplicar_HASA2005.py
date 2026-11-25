#!/usr/bin/env python3
"""Revisión focalizada del informe Mini SOC TiendaCR (HASA2005).

Uso desde la raíz de un clon actualizado del repositorio:
  python3 /ruta/aplicar_HASA2005.py --repo . --carne-harold NUMERO --carne-fiorella NUMERO

No modifica los apartados de ataques ni las capturas asignados a Fiorella.
Los cambios se hacen solo si se encuentran los fragmentos esperados; por seguridad
se cancela toda la operación cuando cambió alguno de ellos.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DECLARACION_IA = '''# Declaración de uso de inteligencia artificial

El equipo reconoce el uso de herramientas de inteligencia artificial como **asistentes de apoyo** durante la preparación del proyecto. El borrador del repositorio documenta el uso de **Claude Code (Anthropic)** para proponer código, configuraciones y textos. Adicionalmente, **ChatGPT (OpenAI)** se utilizó para apoyar la revisión editorial y el contraste de afirmaciones con documentación oficial.

| Actividad | Apoyo de la IA | Responsabilidad humana |
|---|---|---|
| Aprovisionamiento y configuración (Vagrant, Docker, nginx y Wazuh) | Propuestas de scripts y ayuda para interpretar errores de configuración. | Revisar código, ejecutar el despliegue y verificar su funcionamiento en el laboratorio. |
| Reglas de Suricata y Wazuh | Sugerencias para reglas y pruebas de detección y respuesta. | Comprobar sintaxis, umbrales, alertas y bloqueos con los registros reales. |
| Investigación, análisis de riesgos y referencias | Borradores, organización de tablas, revisión de redacción y búsqueda de fuentes. | Contrastar licencias, costos, citas y normativa con las publicaciones oficiales; decidir las valoraciones de riesgo. |
| Plan de respuesta a incidentes e informe | Apoyo para estructurar el procedimiento, revisar ortografía y presentar hallazgos. | Asignar roles y tiempos, documentar las decisiones y aprobar el informe. |
| Diagrama y evidencia experimental | Herramientas de apoyo para elaborar o revisar la documentación. | Corroborar la arquitectura real; ejecutar las pruebas en Kali y obtener capturas sin fabricar resultados. |

**Límites del uso:** la IA no se considera fuente de evidencia experimental. Los tiempos, bloqueos, alertas y resultados de los ataques deben provenir de las máquinas virtuales y de las capturas obtenidas por el equipo. Las correcciones documentales no sustituyen las pruebas. Cada integrante debe comprender y poder defender el trabajo presentado.
'''


def sustitucion(texto: str, original: str, nuevo: str, archivo: str) -> str:
    if nuevo in texto:
        return texto
    if original in texto:
        return texto.replace(original, nuevo, 1)
    raise RuntimeError(f"No se encontró el fragmento esperado en {archivo}: {original[:95]!r}. Hacer git pull y revisar manualmente.")


def actualizar_fase1(texto: str) -> str:
    archivo = 'docs/fase1-investigacion.md'
    # Se preserva la tabla comparativa original de 7 columnas: contiene información
    # de detección, despliegue, licencia, respuesta e integración que no debe perderse.
    if '| Criterio | **AWS GuardDuty**' not in texto:
        raise RuntimeError('No se encontró la tabla comparativa original de siete columnas.')
    texto = sustitucion(texto,
        '| **Modelo de despliegue y recursos** | **SaaS sin agente**: se activa por región y no consume recursos de las VM. El plan de *runtime* sí usa un agente. | **SaaS** más un agente (Defender for Endpoint o Azure Arc para máquinas fuera de Azure). |',
        '| **Modelo de despliegue y recursos** | **SaaS sin agente** para las fuentes de telemetría tradicionales; los planes de *runtime* pueden usar agente. | **SaaS** con integración por agente: servidores de Azure, otras nubes y equipos locales compatibles pueden incorporarse mediante Azure Arc o Defender for Endpoint. |', archivo)
    texto = sustitucion(texto,
        '| **Costo y licencia** | Propietario. **Pago por volumen** de eventos analizados. Prueba gratuita de 30 días. |',
        '| **Costo y licencia** | Propietario. **Costo variable** según fuente de datos, región, volumen y plan; prueba gratuita de 30 días para funciones elegibles. |', archivo)
    texto = sustitucion(texto,
        '| **Limitaciones** | Solo AWS. **No inspecciona el contenido** de los paquetes (solo metadatos de flujo), así que no ve una SQLi dentro de HTTP. Tiene costo variable. | Centrado en Azure. Costo por servidor. Las funciones avanzadas (FIM, JIT) solo están en el plan 2. |',
        '| **Limitaciones** | Enfoque AWS; no es un IDS HTTP en línea para el tráfico de TiendaCR. Costo por consumo. | Requiere integrar los servidores en Azure. Admite equipos locales compatibles mediante Azure Arc; los planes avanzados tienen cargos y requisitos específicos. |', archivo)

    texto = sustitucion(texto,
        'El resto de los datos provienen de la documentación oficial de cada proyecto o proveedor.',
        'Los demás datos se contrastaron con documentación oficial de proveedores y proyectos. Los costos dependen de funciones, volumen y región; la respuesta automática necesita configuración (Amazon Web Services, s.f.-b; Microsoft, s.f.-a, s.f.-b; Wazuh Inc., s.f.-a, s.f.-b; Open Information Security Foundation, s.f.-a; CrowdSec, s.f.-a; The Falco Project, s.f.).', archivo)
    texto = sustitucion(texto,
        'Se eligió **Wazuh + Suricata**:',
        'Se eligió **Wazuh + Suricata** como defensa en profundidad reproducible (Dotson, 2019; Guijarro Olivares et al., 2019):', archivo)
    texto = sustitucion(texto,
        '2. **Wazuh funciona como SIEM central** e integra Suricata de forma nativa leyendo `eve.json`. Así hay un solo panel, como pide el enunciado.',
        '2. **Wazuh funciona como SIEM central** e integra las alertas de Suricata desde `eve.json`. Así hay un solo panel, como pide el enunciado (Wazuh Inc., s.f.-a).', archivo)
    texto = sustitucion(texto,
        '3. **Respuesta automática incluida** (*active response*) sin servicios adicionales.',
        '3. **Respuesta automática incluida** (*active response*) con scripts activados por reglas, como `firewall-drop` para bloqueos temporales (Wazuh Inc., s.f.-b).', archivo)
    texto = sustitucion(texto,
        '4. **Costo cero y despliegue local.** GuardDuty y Defender for Cloud requieren una cuenta en la nube, tienen costo variable y **no pueden monitorear VM de VirtualBox**.',
        '4. **Software libre y despliegue local.** GuardDuty protege recursos AWS. Defender for Cloud puede incorporar servidores locales compatibles mediante Azure Arc, pero exige integración con su plataforma y puede generar costos. Para este laboratorio aislado se priorizaron herramientas reproducibles y sin licencias comerciales (Microsoft, s.f.-a; Microsoft, s.f.-b).', archivo)
    texto = sustitucion(texto,
        '- **En un despliegue real en AWS** se recomienda **sumar GuardDuty**: es barato, no requiere agente y detecta amenazas a nivel de cuenta (credenciales filtradas o llamadas a la API desde IP maliciosas) que ni Wazuh ni Suricata ven. Wazuh puede ingerir sus hallazgos.',
        '- **En un despliegue real en AWS** se puede **sumar GuardDuty** para detectar amenazas a nivel de cuenta y servicios que no son visibles para Wazuh o Suricata. Su costo dependerá de la región, el volumen de eventos y los planes activados (Amazon Web Services, s.f.-b).', archivo)
    texto = sustitucion(texto,
        'AWS lo resume así: AWS es responsable de la seguridad **"de"** la nube y el cliente de la seguridad **"en"** la nube. En IaaS el cliente asume **la mayor parte** de la responsabilidad, porque controla el sistema operativo hacia arriba.',
        'AWS distingue la seguridad **"de"** la nube, a cargo del proveedor, de la seguridad **"en"** la nube, que corresponde al cliente. En IaaS, el cliente administra el sistema operativo y las capas superiores (Amazon Web Services, s.f.-a; Dotson, 2019).', archivo)
    texto = sustitucion(texto,
        'Se aplicó **NIST SP 800-30 Rev. 1** de forma simplificada y semicuantitativa:',
        'Se aplicó **NIST SP 800-30 Rev. 1** de forma simplificada y semicuantitativa (Joint Task Force Transformation Initiative, 2012):', archivo)
    texto = sustitucion(texto,
        '**Nivel de riesgo:** 1-4 **Bajo** · 5-9 **Medio** · 10-16 **Alto** · 20-25 **Crítico**.',
        '**Nivel de riesgo:** 1-4 **Bajo** · 5-9 **Medio** · 10-16 **Alto** · 20-25 **Crítico**. Los puntajes reflejan el escenario sin mitigaciones; R09 supone una probabilidad baja de falla del SIEM, mientras que R12 asigna impacto directo bajo al reconocimiento por sí solo, sin ignorar su potencial como fase previa de otros ataques.', archivo)
    texto = sustitucion(texto,
        'Kernel y paquetes desactualizados (6904 CVE detectadas por Wazuh)',
        'Kernel y paquetes desactualizados (total de hallazgos pendiente de verificar)', archivo)
    texto = sustitucion(texto,
        '- **6904 CVE** en total: 238 críticas, 2241 altas, 2517 medias y 250 bajas.',
        '- El borrador indica **6.904 hallazgos**, pero las categorías anotadas (238 críticas, 2.241 altas, 2.517 medias y 250 bajas) suman **5.246**. Falta conciliar el total con un solo corte temporal del panel Wazuh antes de reportar cifras definitivas.', archivo)
    texto = sustitucion(texto,
        '| R08 | 12 | **Mitigar** | `apt upgrade` y reinicio con kernel nuevo; actualizar la imagen; seguimiento en *Vulnerability Detection* | Integrante 2 | 2.3, 2.8 (C5) |',
        '| R08 | 12 | **Mitigar parcialmente** | Parches disponibles y revisión de imágenes; actualización efectiva del kernel y reinicio aún pendientes; seguimiento en *Vulnerability Detection* | Integrante 2 | 2.3, 2.8 (C5) |', archivo)
    texto = sustitucion(texto,
        '- **Lección:** el componente de seguridad (el IDS) también es superficie de ataque y también hay que parchearlo. Además, el kernel vulnerable no se corrige solo con `apt upgrade`: hay que **reiniciar** con el kernel nuevo y retirar el antiguo.',
        '- **Lección:** el IDS también es superficie de ataque. En este laboratorio, `apt upgrade` no dejó actualizado el kernel `6.8.0-86`: queda pendiente instalar una versión HWE compatible, reiniciar y reevaluar las CVE.', archivo)
    return texto


def actualizar_plan(texto: str) -> str:
    f = 'informe/secciones/27-plan-ir.md'
    texto = sustitucion(texto,
        '| Analista SOC (N1) | Triaje de alertas, apertura del incidente, evidencia inicial | ✏️ Integrante 1 | ✏️ Integrante 2 |',
        '| Analista SOC (N1) | Triaje de alertas, apertura del incidente, evidencia inicial | Harold Saborío Arce | Fiorella Zamora |', f)
    texto = sustitucion(texto,
        '| Responsable de incidentes (IR lead) | Severidad, decisiones de contención, bitácora, cierre | ✏️ Integrante 2 | ✏️ Integrante 1 |',
        '| Responsable de incidentes (IR lead) | Severidad, decisiones de contención, bitácora, cierre | Fiorella Zamora | Harold Saborío Arce |', f)
    texto = sustitucion(texto,
        '| Administrador de sistemas | Contención y erradicación (firewall, contenedores, nginx) | ✏️ Integrante 1 | ✏️ Integrante 2 |',
        '| Administrador de sistemas | Contención y erradicación (firewall, contenedores, nginx) | Harold Saborío Arce | Fiorella Zamora |', f)
    texto = sustitucion(texto,
        '**Notificación:** si hubiera datos personales reales, la Ley 8968 de Costa Rica y su reglamento obligan a informar a los titulares y a la PRODHAB en el plazo que fija el reglamento (✏️ verificar: 5 días hábiles). En el laboratorio no aplica.',
        '**Notificación de datos personales:** los artículos 38 y 39 del Reglamento a la Ley 8968 (Decreto Ejecutivo N.º 37554-JP) establecen que, ante una vulnerabilidad que afecte datos personales, el responsable debe comunicarla a los titulares afectados **dentro de cinco días hábiles desde su ocurrencia**, iniciar la revisión exhaustiva en ese plazo e informar a los titulares y a la PRODHAB sobre la naturaleza del incidente, los datos comprometidos, las medidas inmediatas y los medios de información. Este escenario usa datos ficticios, por lo que no se configura una brecha real que notificar (Poder Ejecutivo de Costa Rica, 2012).', f)
    return texto


def actualizar_referencias(texto: str) -> str:
    f = 'informe/secciones/92-referencias.md'
    texto = sustitucion(texto,
        'Guijarro Olivares, J., Caparrós Ramírez, J. J., & Cubero Luque, L. (2019). *DevOps y seguridad cloud*. Editorial UOC.',
        'Guijarro Olivares, J., Caparrós Ramírez, J., & Cubero Luque, L. (2019). *DevOps y seguridad cloud*. Editorial UOC.', f)
    texto = sustitucion(texto,
        'Amazon Web Services. (s.f.-b). *What is Amazon GuardDuty?* Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html',
        'Amazon Web Services. (s.f.-b). *Amazon GuardDuty pricing*. https://aws.amazon.com/guardduty/pricing/\n\nAmazon Web Services. (s.f.-c). *What is Amazon GuardDuty?* Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html', f)
    texto = sustitucion(texto,
        'CrowdSec. (s.f.). *CrowdSec documentation*. https://docs.crowdsec.net/',
        'CrowdSec. (s.f.-a). *CrowdSec documentation*. https://docs.crowdsec.net/\n\nCrowdSec. (s.f.-b). *CrowdSec FAQ: license, resources, performance, data sharing*. https://docs.crowdsec.net/u/troubleshooting/general/', f)
    texto = sustitucion(texto,
        'Microsoft. (s.f.). *Microsoft Defender for Cloud documentation*. Microsoft Learn. https://learn.microsoft.com/azure/defender-for-cloud/',
        'Microsoft. (s.f.-a). *Select a Defender for Servers plan*. Microsoft Learn. https://learn.microsoft.com/en-us/azure/defender-for-cloud/plan-defender-for-servers-select-plan\n\nMicrosoft. (s.f.-b). *Microsoft Defender for Cloud pricing*. https://azure.microsoft.com/en-us/pricing/details/defender-for-cloud/\n\nMicrosoft. (s.f.-c). *Microsoft Defender for Cloud documentation*. Microsoft Learn. https://learn.microsoft.com/azure/defender-for-cloud/', f)
    texto = sustitucion(texto,
        'Open Information Security Foundation. (s.f.). *Suricata user guide*. https://docs.suricata.io/',
        'Open Information Security Foundation. (s.f.-a). *Suricata user guide*. https://docs.suricata.io/\n\nOpen Information Security Foundation. (s.f.-b). *What is Suricata?* https://docs.suricata.io/en/latest/what-is-suricata.html', f)
    texto = sustitucion(texto,
        'Wazuh Inc. (s.f.). *Wazuh documentation* (versión 4.14). https://documentation.wazuh.com/current/',
        'Wazuh Inc. (s.f.-a). *Wazuh documentation*. https://documentation.wazuh.com/current/\n\nWazuh Inc. (s.f.-b). *Active Response: How to configure*. https://documentation.wazuh.com/current/user-manual/capabilities/active-response/how-to-configure.html', f)
    if 'Poder Ejecutivo de Costa Rica. (2012).' not in texto:
        texto += '\nPoder Ejecutivo de Costa Rica. (2012). *Reglamento a la Ley de Protección de la Persona frente al Tratamiento de sus Datos Personales* (Decreto Ejecutivo N.º 37554-JP, arts. 38-39). https://formatos.inamu.go.cr/SIDOC/DOCS/decreto_37554jp.pdf\n'
    return texto


def actualizar_anexo(texto: str) -> str:
    return sustitucion(texto,
        '**URL:** <span class="todo">COMPLETAR (repositorio público en GitHub, compartido con el profesor)</span>',
        '**URL:** https://github.com/fio202/mini-soc-tiendacr', 'informe/secciones/93-anexos.md')


def actualizar_remediacion(texto: str) -> str:
    f = 'informe/secciones/28-remediacion.md'
    original = '| C5 | Paquetes con CVE | `apt upgrade` (más el reinicio con el kernel nuevo) y `docker compose pull` | ✏️ CVE en el panel después de remediar |'
    nuevo = '| C5 | Paquetes con CVE | `apt upgrade` y revisión de imágenes; instalar un kernel HWE compatible y reiniciar siguen pendientes. | ✏️ CVE en el panel después de remediar |'
    texto = sustitucion(texto, original, nuevo, f)
    texto = sustitucion(texto,
        '**Comparación antes / después** (misma herramienta y mismos parámetros):',
        '**Riesgo residual C5:** el kernel `6.8.0-86` **no quedó actualizado** con `apt upgrade` en la evidencia disponible. Es necesario instalar el kernel HWE compatible, reiniciar el servidor, verificar `uname -r` y volver a revisar las CVE con Wazuh. Hasta entonces, las vulnerabilidades asociadas al kernel permanecen como riesgo residual y **debe revisarse el puntaje R08** antes de afirmar que todos los riesgos altos desaparecieron.\n\n**Comparación antes / después** (misma herramienta y mismos parámetros):', f)
    return texto


def actualizar_build(texto: str, car_h: str | None, car_f: str | None, fecha: str | None) -> str:
    f = 'informe/build.py'
    cambios = {
        'institucion': 'Universidad Técnica Nacional (UTN) - Sede Regional de San Carlos',
        'profesor': 'Prof. Marcos Castro',
        'titulo': 'Proyecto 2: Mini SOC TiendaCR',
        'subtitulo': 'Laboratorio local con Wazuh, Suricata, monitoreo y respuesta a incidentes',
        'pdf': 'P1_Zamora_Saborio.pdf',
    }
    if car_h is not None and car_f is not None:
        cambios['integrantes'] = [f'Fiorella Zamora (carné {car_f})', f'Harold Saborío Arce (carné {car_h})']
    if fecha:
        cambios['fecha'] = fecha
    for llave, valor in cambios.items():
        patron = re.compile(r'(?m)^(\s*"' + re.escape(llave) + r'": ).*(,)(\s*(?:#.*)?)$')
        nuevo = json.dumps(valor, ensure_ascii=False)
        texto, n = patron.subn(lambda m: m.group(1) + nuevo + ',' + (m.group(3) if llave == 'pdf' else ''), texto, count=1)
        if n != 1:
            raise RuntimeError(f'No se pudo actualizar CONFIG.{llave} en {f}')
    return texto


def actualizar_estilo(texto: str) -> str:
    archivo = 'informe/estilo.css'
    for original, nuevo in [
        ('color: #1b1b1b;', 'color: #000000;'),
        ('color: #555;', 'color: #000000;'),
        ('color: #777;', 'color: #000000;'),
        ('color: #444;', 'color: #000000;'),
    ]:
        if original in texto:
            texto = texto.replace(original, nuevo)
    return texto


def principal() -> int:
    p = argparse.ArgumentParser(description='Aplica mejoras documentales asignadas a HASA2005, sin pisar evidencia de Fiorella.')
    p.add_argument('--repo', default='.', help='Raíz del clon de mini-soc-tiendacr (por defecto: .)')
    p.add_argument('--carne-harold', help='Carné universitario real de Harold (sin inventarlo)')
    p.add_argument('--carne-fiorella', help='Carné universitario real de Fiorella (sin inventarlo)')
    p.add_argument('--fecha', help='Fecha real de presentación, por ejemplo: 19 de noviembre de 2026')
    p.add_argument('--dry-run', action='store_true', help='Valida los cambios sin escribirlos')
    args = p.parse_args()
    if bool(args.carne_harold) != bool(args.carne_fiorella):
        p.error('Para terminar la portada hay que indicar ambos carnés o ninguno.')
    repo = Path(args.repo).expanduser().resolve()
    if not (repo / '.git').exists() or not (repo / 'informe/build.py').exists():
        p.error(f'{repo} no es la raíz de un clon Git del proyecto.')

    archivos = {
        'docs/fase1-investigacion.md': actualizar_fase1,
        'informe/secciones/27-plan-ir.md': actualizar_plan,
        'informe/secciones/91-declaracion-ia.md': lambda _: DECLARACION_IA,
        'informe/secciones/92-referencias.md': actualizar_referencias,
        'informe/secciones/93-anexos.md': actualizar_anexo,
        'informe/secciones/28-remediacion.md': actualizar_remediacion,
        'informe/build.py': lambda t: actualizar_build(t, args.carne_harold, args.carne_fiorella, args.fecha),
        'informe/estilo.css': actualizar_estilo,
    }
    pendientes = {}
    try:
        for ruta, funcion in archivos.items():
            path = repo / ruta
            contenido = path.read_text(encoding='utf-8')
            nuevo = funcion(contenido)
            pendientes[path] = (contenido, nuevo)
    except (RuntimeError, OSError, ValueError) as e:
        print('ERROR: no se aplicó ningún cambio:', e, file=sys.stderr)
        return 1

    modificados = [str(p.relative_to(repo)) for p, (anterior, nuevo) in pendientes.items() if anterior != nuevo]
    if not args.dry_run:
        for path, (anterior, nuevo) in pendientes.items():
            if anterior != nuevo:
                path.write_text(nuevo, encoding='utf-8')
    print('Modo:', 'verificación (sin cambios)' if args.dry_run else 'escritura')
    print('Archivos actualizados:', len(modificados))
    for ruta in modificados:
        print(' -', ruta)
    if not args.carne_harold:
        print('AVISO: quedan por poner los dos carnés en CONFIG.integrantes; ejecuta otra vez con --carne-harold y --carne-fiorella.')
    print('REVISAR con Fiorella: asignación de roles, declaración histórica de IA, cifras de Wazuh y pruebas 2.4/2.8.')
    print('Luego: git diff --check && git diff; .venv/bin/python informe/build.py; git add [solo tus archivos]')
    return 0


if __name__ == '__main__':
    raise SystemExit(principal())
