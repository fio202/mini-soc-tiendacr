#!/usr/bin/env python3
"""
Genera el informe técnico en PDF a partir de docs/ e informe/secciones/.

Requisitos (una sola vez):
    python3 -m venv .venv && .venv/bin/pip install markdown-it-py mdit-py-plugins weasyprint
Uso (desde la raíz del repositorio):
    .venv/bin/python informe/build.py
Salida:
    informe/informe.html  y  informe/<NOMBRE_PDF>
"""
import html
import re
from pathlib import Path

from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from weasyprint import HTML

# ----------------------------------------------------------------- DATOS DE PORTADA
CONFIG = {
    "institucion": "Universidad Técnica Nacional (UTN) - Sede Regional de San Carlos",
    "curso": "ITI-922 Seguridad de TI II",
    "profesor": "Prof. Marcos Castro",
    "titulo": "Proyecto 2: Mini SOC TiendaCR",
    "subtitulo": "Laboratorio local con Wazuh, Suricata, monitoreo y respuesta a incidentes",
    "integrantes": ["Fiorella Zamora Campos", "Harold Saborío Arce"],
    "fecha": "18 de noviembre de 2026",
    "pdf": "P1_Zamora_Saborio.pdf",
}

RAIZ = Path(__file__).resolve().parent.parent
SEC = "informe/secciones/"

# (archivo, niveles a bajar en los encabezados, salto de página antes)
PARTES = [
    (SEC + "00-resumen-ejecutivo.md", 0, True),
    ("docs/fase1-investigacion.md", 0, True),
    ("#FASE2", 0, True),
    # Versiones condensadas para el informe; el detalle (comandos, procedimientos) vive en docs/
    (SEC + "10-arquitectura-implementacion.md", 1, False),
    (SEC + "22-control-acceso.md", 1, False),
    (SEC + "23-monitoreo.md", 1, False),
    (SEC + "24-ataques.md", 1, False),
    (SEC + "25-reglas-respuesta.md", 1, False),
    (SEC + "27-plan-ir.md", 1, False),
    (SEC + "28-remediacion.md", 1, False),
    (SEC + "90-conclusiones.md", 0, True),
    (SEC + "91-declaracion-ia.md", 0, False),
    (SEC + "92-referencias.md", 0, False),
    (SEC + "93-anexos.md", 0, True),
]

TODO = '<span class="todo">COMPLETAR</span>'


def bajar_encabezados(texto: str, n: int) -> str:
    """Baja n niveles los encabezados ATX, sin tocar bloques de código."""
    if n == 0:
        return texto
    salida, en_codigo = [], False
    for linea in texto.splitlines():
        if linea.lstrip().startswith("```"):
            en_codigo = not en_codigo
        if not en_codigo and re.match(r"^#{1,5} ", linea):
            linea = "#" * n + linea
        salida.append(linea)
    return "\n".join(salida)


def preparar(ruta: str, nivel: int) -> str:
    if ruta == "#FASE2":
        return "# Fase 2. Implementación, ataque, detección y respuesta\n"
    texto = (RAIZ / ruta).read_text(encoding="utf-8")
    # Líneas solo útiles en el repositorio
    texto = "\n".join(l for l in texto.splitlines() if "informe/secciones/92-referencias.md" not in l)
    texto = texto.replace("✏️", "COMPLETAR_MARK")
    # Separadores horizontales de los .md: en el informe sobran
    texto = re.sub(r"(?m)^---\s*$", "", texto)
    return bajar_encabezados(texto, nivel)


def slug(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s).lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return re.sub(r"[\s_]+", "-", s).strip("-") or "sec"


def construir() -> None:
    md = MarkdownIt("commonmark", {"html": True, "typographer": False}).enable(["table", "strikethrough"])
    md.use(anchors_plugin, min_level=1, max_level=3, slug_func=slug)

    bloques = []
    for ruta, nivel, salto in PARTES:
        if salto:
            bloques.append('<div class="salto"></div>')
        bloques.append(preparar(ruta, nivel))
    cuerpo = md.render("\n\n".join(bloques))
    cuerpo = cuerpo.replace("COMPLETAR_MARK", TODO)

    # Índice (H1 y H2)
    entradas = []
    for nivel, ident, texto in re.findall(r'<h([12]) id="([^"]+)">(.*?)</h\1>', cuerpo):
        limpio = re.sub(r"<[^>]+>", "", texto)
        entradas.append(f'<li class="toc{nivel}"><a href="#{ident}">{limpio}</a></li>')
    indice = '<section class="indice"><h1 class="sin-indice">Índice</h1><ul>' + "".join(entradas) + "</ul></section>"

    c = CONFIG
    portada = f"""
<section class="portada">
  <p class="inst">{html.escape(c['institucion'])}</p>
  <p class="curso">{html.escape(c['curso'])} · {html.escape(c['profesor'])}</p>
  <div class="bloque-titulo">
    <h1 class="sin-indice">{html.escape(c['titulo'])}</h1>
    <p class="sub">{html.escape(c['subtitulo'])}</p>
  </div>
  <img src="docs/arquitectura.png" alt="">
  <div class="autores">
    <p><b>Integrantes</b></p>
    {''.join(f'<p>{html.escape(i)}</p>' for i in c['integrantes'])}
    <p class="fecha">{html.escape(c['fecha'])}</p>
  </div>
</section>"""
    portada = portada.replace("COMPLETAR", TODO)

    css = (Path(__file__).parent / "estilo.css").read_text(encoding="utf-8")
    doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>{html.escape(c['titulo'])}</title><style>{css}</style></head>
<body>{portada}{indice}<main>{cuerpo}</main></body></html>"""

    salida_html = RAIZ / "informe/informe.html"
    salida_html.write_text(doc, encoding="utf-8")
    pdf = RAIZ / "informe" / c["pdf"]
    documento = HTML(string=doc, base_url=str(RAIZ)).render()
    documento.write_pdf(pdf)
    pendientes = doc.count('class="todo"')
    print(f"PDF: {pdf.relative_to(RAIZ)}  |  páginas: {len(documento.pages)}  |  marcas COMPLETAR: {pendientes}")


if __name__ == "__main__":
    construir()
