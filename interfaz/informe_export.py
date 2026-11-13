"""Nota técnica exportable: vista para imprimir y PDF.

Las dos salidas pintan el mismo documento que arma `interfaz/notas.py`, así que la
pantalla, la hoja impresa, el PDF y la nota en Markdown dicen lo mismo.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from interfaz.documento import a_html, a_pdf
from interfaz.notas import ARCHIVO_NOTA, documento

RAIZ = Path(__file__).resolve().parents[1]
ESTATICOS = Path(__file__).resolve().parent / "static"

# La especificación pide notas de dos a tres páginas.
PAGINAS_MINIMAS = 2
PAGINAS_MAXIMAS = 3


def fragmento_nota(demo_id: int, informe: dict | None) -> str:
    """El <article> de la nota, para incrustarlo en la pestaña Informe."""
    return a_html(documento(demo_id, informe))


def html_imprimible(
    demo_id: int,
    informe: dict | None,
    auto_imprimir: bool = False,
    corrida: str | None = None,
    autonomo: bool = False,
) -> str:
    """Página completa de la nota. Con `autonomo`, sirve como archivo suelto fuera del servidor."""
    script = "<script>window.addEventListener('load', () => { window.print(); });</script>" if auto_imprimir else ""
    if autonomo:
        estilos = f"<style>{(ESTATICOS / 'nota.css').read_text(encoding='utf-8')}</style>"
        acciones = ""
    else:
        estilos = '<link rel="stylesheet" href="/static/nota.css">'
        consulta = f"?corrida={quote(corrida)}" if corrida else ""
        acciones = f"""<nav class="barra-acciones" aria-label="Acciones de la nota">
    <button type="button" onclick="window.print()">Imprimir o guardar como PDF</button>
    <a href="/api/demos/{demo_id}/informe.pdf{consulta}">Descargar PDF</a>
    <a href="/demo/{demo_id}">Volver al demo</a>
  </nav>"""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nota técnica · Demo {demo_id} · Nodo IA Caribe</title>
  {estilos}
</head>
<body class="hoja-nota">
  {acciones}
  <main>
  {fragmento_nota(demo_id, informe)}
  </main>
  {script}
</body>
</html>"""


def pdf_con_paginas(demo_id: int, informe: dict | None) -> tuple[bytes, int]:
    return a_pdf(documento(demo_id, informe))


def pdf_bytes(demo_id: int, informe: dict | None) -> bytes:
    return pdf_con_paginas(demo_id, informe)[0]


def nombre_pdf(demo_id: int) -> str:
    return f"Nodo-IA-Caribe_{ARCHIVO_NOTA[demo_id]}.pdf"


def guardar_pdf(demo_id: int, informe: dict | None) -> Path:
    destino = RAIZ / "resultados" / f"demo{demo_id}" / "informe.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(pdf_bytes(demo_id, informe))
    return destino
