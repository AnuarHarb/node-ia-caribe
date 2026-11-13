"""Documento de la nota técnica: un solo modelo y tres salidas (Markdown, HTML y PDF).

El contenido se arma una vez en `interfaz/notas.py`. Aquí solo se pinta, para que el PDF,
la vista para imprimir y la nota en Markdown digan exactamente lo mismo.

Un texto es una cadena o una lista de tramos. Un tramo es una cadena (texto corrido) o
una tupla `(clase, texto)` con clase `b` (negrita), `c` (código o ruta) o `a` (enlace).
Los datos medidos entran siempre como cadenas, así ningún asterisco de una transcripción
se interpreta como formato.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from fpdf import FPDF
from fpdf.fonts import FontFace

FUENTES_FCA = Path(__file__).resolve().parent / "static" / "fca" / "FCA_Sistema-de-diseno" / "fuentes"
FUENTES_RESPALDO = (
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    Path("/Library/Fonts/Arial Unicode.ttf"),
    Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
)

# Colores del sistema de diseño FCA (tokens.css).
MARINO = (5, 10, 48)
TINTA = (11, 18, 32)
TENUE = (82, 96, 119)
AZUL = (0, 107, 173)
LINEA = (217, 228, 238)
NIEBLA = (239, 248, 255)

COLORES_ESTADO = {
    "ok": {"fondo": (230, 246, 238), "barra": (0, 140, 85)},
    "parcial": {"fondo": (255, 243, 226), "barra": (214, 120, 30)},
    "falla": {"fondo": (253, 234, 234), "barra": (190, 40, 40)},
    "pendiente": {"fondo": (238, 242, 247), "barra": TENUE},
}
ETIQUETA_ESTADO = {
    "ok": "Criterio cumplido",
    "parcial": "Evidencia parcial",
    "falla": "Criterio no cumplido",
    "pendiente": "Sin medición",
}


# --- Constructores -----------------------------------------------------------------


def b(texto: object) -> tuple[str, str]:
    return ("b", str(texto))


def cod(texto: object) -> tuple[str, str]:
    return ("c", str(texto))


def url(texto: object) -> tuple[str, str]:
    return ("a", str(texto))


def p(*partes: object) -> dict:
    return {"tipo": "p", "texto": list(partes)}


def lista(items: list, ordenada: bool = False) -> dict:
    return {"tipo": "lista", "items": list(items), "ordenada": ordenada}


def pasos(items: list) -> dict:
    return lista(items, ordenada=True)


def tabla(
    cabecera: list | None,
    filas: list[list],
    anchos: list[float] | None = None,
    titulo: str | None = None,
    alinear: list[str] | None = None,
) -> dict:
    return {
        "tipo": "tabla",
        "cabecera": list(cabecera) if cabecera else None,
        "filas": [list(fila) for fila in filas],
        "anchos": anchos,
        "titulo": titulo,
        "alinear": alinear,
    }


def aviso(*partes: object, clase: str = "parcial") -> dict:
    return {"tipo": "aviso", "texto": list(partes), "clase": clase}


def h3(texto: str) -> dict:
    return {"tipo": "h3", "texto": texto}


def seccion(titulo: str, *bloques: dict | None) -> dict:
    return {"titulo": titulo, "bloques": [bloque for bloque in bloques if bloque]}


# --- Utilidades comunes ------------------------------------------------------------


def _tramos(texto: object) -> list[tuple[str, str]]:
    if texto is None:
        return []
    if isinstance(texto, tuple) and len(texto) == 2 and texto[0] in ("b", "c", "a"):
        return [(texto[0], str(texto[1]))]
    if isinstance(texto, (list, tuple)):
        salida: list[tuple[str, str]] = []
        for parte in texto:
            salida.extend(_tramos(parte))
        return salida
    return [("", str(texto))]


def texto_plano(texto: object) -> str:
    return "".join(tramo for _, tramo in _tramos(texto))


def textos_del_documento(doc: dict) -> list[str]:
    """Todo el texto visible, para comprobar que la tipografía tiene cada carácter."""
    salida = [doc.get("titulo", ""), doc.get("antetitulo", ""), doc.get("pie", "")]
    salida.append(texto_plano((doc.get("estado") or {}).get("texto")))
    for campo, valor in doc.get("ficha") or []:
        salida += [texto_plano(campo), texto_plano(valor)]
    for sec in doc.get("secciones") or []:
        salida.append(sec["titulo"])
        for bloque in sec["bloques"]:
            if bloque["tipo"] in ("p", "aviso", "h3"):
                salida.append(texto_plano(bloque["texto"]))
            elif bloque["tipo"] == "lista":
                salida += [texto_plano(item) for item in bloque["items"]]
            elif bloque["tipo"] == "tabla":
                salida.append(bloque.get("titulo") or "")
                salida += [texto_plano(celda) for celda in bloque.get("cabecera") or []]
                for fila in bloque["filas"]:
                    salida += [texto_plano(celda) for celda in fila]
    return salida


# --- Markdown ----------------------------------------------------------------------


def _md(texto: object, en_tabla: bool = False) -> str:
    partes = []
    for clase, tramo in _tramos(texto):
        tramo = tramo.replace("\n", " ")
        if en_tabla:
            tramo = tramo.replace("|", "\\|")
        if clase == "b":
            partes.append(f"**{tramo.strip()}**")
        elif clase == "c":
            partes.append(f"`{tramo}`")
        elif clase == "a":
            partes.append(f"<{tramo}>")
        else:
            partes.append(tramo)
    return "".join(partes)


def a_markdown(doc: dict) -> str:
    estado = doc.get("estado") or {}
    lineas = [
        f"# {doc['titulo']}",
        "",
        doc.get("antetitulo", ""),
        "",
        f"**{ETIQUETA_ESTADO.get(estado.get('clase'), 'Estado')}.** {_md(estado.get('texto'))}",
        "",
        "| Campo | Contenido |",
        "| --- | --- |",
    ]
    for campo, valor in doc.get("ficha") or []:
        lineas.append(f"| {_md(campo, True)} | {_md(valor, True)} |")
    lineas.append("")
    for sec in doc.get("secciones") or []:
        lineas += [f"## {sec['titulo']}", ""]
        for bloque in sec["bloques"]:
            tipo = bloque["tipo"]
            if tipo == "p":
                lineas += [_md(bloque["texto"]), ""]
            elif tipo == "h3":
                lineas += [f"### {_md(bloque['texto'])}", ""]
            elif tipo == "aviso":
                lineas += [f"> {_md(bloque['texto'])}", ""]
            elif tipo == "lista":
                for numero, item in enumerate(bloque["items"], 1):
                    marca = f"{numero}." if bloque["ordenada"] else "-"
                    lineas.append(f"{marca} {_md(item)}")
                lineas.append("")
            elif tipo == "tabla":
                if bloque.get("titulo"):
                    lineas += [f"**{bloque['titulo']}**", ""]
                cabecera = bloque.get("cabecera") or ["Campo", "Contenido"]
                lineas.append("| " + " | ".join(_md(c, True) for c in cabecera) + " |")
                lineas.append("| " + " | ".join("---" for _ in cabecera) + " |")
                for fila in bloque["filas"]:
                    lineas.append("| " + " | ".join(_md(c, True) for c in fila) + " |")
                lineas.append("")
    if doc.get("pie"):
        lineas += ["---", "", doc["pie"], ""]
    return "\n".join(lineas)


# --- HTML --------------------------------------------------------------------------


def _h(texto: object) -> str:
    partes = []
    for clase, tramo in _tramos(texto):
        seguro = html.escape(tramo, quote=True)
        if clase == "b":
            partes.append(f"<strong>{seguro}</strong>")
        elif clase == "c":
            partes.append(f"<code>{seguro}</code>")
        elif clase == "a":
            partes.append(f'<a href="{seguro}">{seguro}</a>')
        else:
            partes.append(seguro)
    return "".join(partes)


def a_html(doc: dict) -> str:
    """Fragmento HTML semántico de la nota (un <article>), sin <html> ni estilos."""
    estado = doc.get("estado") or {}
    clase = estado.get("clase", "pendiente")
    ficha = "".join(f"<dt>{_h(campo)}</dt><dd>{_h(valor)}</dd>" for campo, valor in doc.get("ficha") or [])
    partes = [
        '<article class="nota">',
        "<header>",
        f'<p class="antetitulo">{_h(doc.get("antetitulo", ""))}</p>',
        f"<h1>{_h(doc['titulo'])}</h1>",
        f'<p class="estado estado-{html.escape(clase)}" role="status">'
        f"<strong>{_h(ETIQUETA_ESTADO.get(clase, 'Estado'))}.</strong> {_h(estado.get('texto'))}</p>",
        f'<dl class="ficha">{ficha}</dl>',
        "</header>",
    ]
    for numero, sec in enumerate(doc.get("secciones") or [], 1):
        ident = f"nota-seccion-{numero}"
        partes.append(f'<section aria-labelledby="{ident}"><h2 id="{ident}">{_h(sec["titulo"])}</h2>')
        for bloque in sec["bloques"]:
            tipo = bloque["tipo"]
            if tipo == "p":
                partes.append(f"<p>{_h(bloque['texto'])}</p>")
            elif tipo == "h3":
                partes.append(f"<h3>{_h(bloque['texto'])}</h3>")
            elif tipo == "aviso":
                partes.append(
                    f'<aside class="aviso aviso-{html.escape(bloque.get("clase", "parcial"))}" role="note">'
                    f"<p>{_h(bloque['texto'])}</p></aside>"
                )
            elif tipo == "lista":
                etiqueta = "ol" if bloque["ordenada"] else "ul"
                items = "".join(f"<li>{_h(item)}</li>" for item in bloque["items"])
                partes.append(f"<{etiqueta}>{items}</{etiqueta}>")
            elif tipo == "tabla":
                alinear = bloque.get("alinear") or []
                titulo = f"<caption>{_h(bloque['titulo'])}</caption>" if bloque.get("titulo") else ""
                cabecera = ""
                if bloque.get("cabecera"):
                    celdas = "".join(f'<th scope="col">{_h(c)}</th>' for c in bloque["cabecera"])
                    cabecera = f"<thead><tr>{celdas}</tr></thead>"
                cuerpo = ""
                for fila in bloque["filas"]:
                    celdas = ""
                    for indice, celda in enumerate(fila):
                        derecha = ' class="num"' if indice < len(alinear) and alinear[indice] == "R" else ""
                        if indice == 0 and not bloque.get("cabecera"):
                            celdas += f'<th scope="row">{_h(celda)}</th>'
                        else:
                            celdas += f"<td{derecha}>{_h(celda)}</td>"
                    cuerpo += f"<tr>{celdas}</tr>"
                partes.append(f"<table>{titulo}{cabecera}<tbody>{cuerpo}</tbody></table>")
        partes.append("</section>")
    if doc.get("pie"):
        partes.append(f"<footer><p>{_h(doc['pie'])}</p></footer>")
    partes.append("</article>")
    return "\n".join(partes)


# --- PDF ---------------------------------------------------------------------------


class _Pdf(FPDF):
    def __init__(self, pie: str) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.add_font("Poppins", "", str(FUENTES_FCA / "Poppins-Regular.ttf"))
        self.add_font("Poppins", "B", str(FUENTES_FCA / "Poppins-SemiBold.ttf"))
        # Whisper a veces escribe en otros alfabetos; Poppins no los tiene.
        self.respaldo = next((ruta for ruta in FUENTES_RESPALDO if ruta.is_file()), None)
        if self.respaldo:
            self.add_font("Respaldo", "", str(self.respaldo))
            self.set_fallback_fonts(["Respaldo"], exact_match=False)
        self._pie = pie
        self.set_margins(16, 15, 16)
        self.set_auto_page_break(auto=True, margin=17)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Poppins", "", 7.5)
        self.set_text_color(*TENUE)
        self.cell(0, 4, f"{self._pie} · página {self.page_no()} de {{nb}}", align="C")


def _lineas(pdf: _Pdf, texto: object, tam: float, ancho: float) -> list[list[tuple[str, str]]]:
    """Parte el texto en líneas que caben en `ancho`, sin cortar palabras al cambiar de estilo."""
    lineas: list[list[tuple[str, str]]] = [[]]
    usado = 0.0
    for clase, tramo in _tramos(texto):
        pdf.set_font("Poppins", "B" if clase == "b" else "", tam)
        for trozo in re.findall(r"\S+|\s+", tramo):
            if trozo.isspace():
                if usado == 0:
                    continue
                lineas[-1].append((clase, " "))
                usado += pdf.get_string_width(" ")
                continue
            largo = pdf.get_string_width(trozo)
            if usado > 0 and usado + largo > ancho:
                while lineas[-1] and lineas[-1][-1][1] == " ":
                    lineas[-1].pop()
                lineas.append([])
                usado = 0.0
            while largo > ancho and len(trozo) > 1:
                corte = len(trozo)
                while corte > 1 and pdf.get_string_width(trozo[:corte]) > ancho:
                    corte -= 1
                lineas[-1].append((clase, trozo[:corte]))
                lineas.append([])
                trozo = trozo[corte:]
                largo = pdf.get_string_width(trozo)
            lineas[-1].append((clase, trozo))
            usado += largo
    while lineas and not lineas[-1]:
        lineas.pop()
    return lineas


def _pintar_lineas(
    pdf: _Pdf,
    lineas: list[list[tuple[str, str]]],
    tam: float,
    alto: float,
    x0: float,
    color: tuple = TINTA,
    saltar_pagina: bool = True,
) -> None:
    margen_celda = pdf.c_margin
    pdf.c_margin = 0
    try:
        for linea in lineas:
            if saltar_pagina and pdf.will_page_break(alto):
                pdf.add_page()
            pdf.set_x(x0)
            for clase, trozo in linea:
                pdf.set_font("Poppins", "B" if clase == "b" else "", tam)
                pdf.set_text_color(*(AZUL if clase == "a" else color))
                pdf.cell(
                    pdf.get_string_width(trozo),
                    alto,
                    trozo,
                    link=trozo if clase == "a" else "",
                    new_x="RIGHT",
                    new_y="TOP",
                )
            pdf.ln(alto)
    finally:
        pdf.c_margin = margen_celda


def _escribir(
    pdf: _Pdf,
    texto: object,
    tam: float,
    alto: float,
    color: tuple = TINTA,
    sangria: float = 0.0,
) -> None:
    x0 = pdf.l_margin + sangria
    _pintar_lineas(pdf, _lineas(pdf, texto, tam, pdf.epw - sangria), tam, alto, x0, color)


def _caja(pdf: _Pdf, texto: object, clase: str, tam: float) -> None:
    colores = COLORES_ESTADO.get(clase, COLORES_ESTADO["pendiente"])
    alto = tam * 0.47
    relleno_x, relleno_y, barra = 4.5, 2.0, 1.4
    lineas = _lineas(pdf, texto, tam, pdf.epw - relleno_x - 3)
    altura = len(lineas) * alto + 2 * relleno_y
    if pdf.will_page_break(altura):
        pdf.add_page()
    y0 = pdf.get_y()
    pdf.set_fill_color(*colores["fondo"])
    pdf.rect(pdf.l_margin, y0, pdf.epw, altura, style="F")
    pdf.set_fill_color(*colores["barra"])
    pdf.rect(pdf.l_margin, y0, barra, altura, style="F")
    pdf.set_y(y0 + relleno_y)
    _pintar_lineas(pdf, lineas, tam, alto, pdf.l_margin + relleno_x, saltar_pagina=False)
    pdf.set_y(y0 + altura)
    pdf.ln(2.2)


def _celda(celda: object) -> tuple[str, bool]:
    tramos = _tramos(celda)
    negrita = bool(tramos) and all(clase == "b" for clase, _ in tramos)
    return "".join(tramo for _, tramo in tramos), negrita


def _alto_minimo_tabla(bloque: dict, tam: float = 7.9) -> float:
    """Espacio que la tabla necesita en la página donde empieza.

    Una tabla corta no se parte entre dos páginas: si no cabe entera, empieza en la siguiente.
    """
    filas = bloque["filas"]
    if len(filas) > 8:
        return 20.0
    return max(20.0, (len(filas) + 1) * (tam * 0.47 + 2.4) + 8)


def _tabla_pdf(pdf: _Pdf, bloque: dict, tam: float = 7.9) -> None:
    cabecera = bloque.get("cabecera")
    filas = bloque["filas"]
    if not filas and not cabecera:
        return
    columnas = len(cabecera) if cabecera else len(filas[0])
    pesos = bloque.get("anchos") or [1] * columnas
    anchos = tuple(pdf.epw * peso / sum(pesos) for peso in pesos)
    alinear = bloque.get("alinear") or ["L"] * columnas
    if pdf.will_page_break(_alto_minimo_tabla(bloque, tam)):
        pdf.add_page()
    if bloque.get("titulo"):
        pdf.set_font("Poppins", "B", 8.6)
        pdf.set_text_color(*MARINO)
        pdf.multi_cell(pdf.epw, 4.4, bloque["titulo"], align="L", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.6)
    pdf.set_font("Poppins", "", tam)
    pdf.set_text_color(*TINTA)
    pdf.set_draw_color(*LINEA)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_line_width(0.2)
    with pdf.table(
        col_widths=anchos,
        width=pdf.epw,
        align="LEFT",
        text_align="LEFT",
        v_align="TOP",
        borders_layout="HORIZONTAL_LINES",
        line_height=tam * 0.47,
        padding=(1.0, 1.2, 1.0, 1.2),
        first_row_as_headings=bool(cabecera),
        headings_style=FontFace(emphasis="BOLD", color=MARINO, fill_color=NIEBLA),
    ) as marco:
        if cabecera:
            fila_pdf = marco.row()
            for indice, celda in enumerate(cabecera):
                fila_pdf.cell(texto_plano(celda), align=alinear[indice] if indice < len(alinear) else "L")
        for fila in filas:
            fila_pdf = marco.row()
            for indice, celda in enumerate(fila):
                texto, negrita = _celda(celda)
                fila_pdf.cell(
                    texto,
                    align=alinear[indice] if indice < len(alinear) else "L",
                    style=FontFace(emphasis="BOLD") if negrita else None,
                )
    pdf.ln(2.6)


def caracteres_sin_glifo(doc: dict) -> list[str]:
    """Caracteres del documento que la tipografía del PDF no puede dibujar."""
    pdf = _Pdf("")
    disponibles = set(pdf.fonts["poppins"].cmap) & set(pdf.fonts["poppinsB"].cmap)
    if pdf.respaldo:
        disponibles |= set(pdf.fonts["respaldo"].cmap)
    usados = {caracter for texto in textos_del_documento(doc) for caracter in texto if not caracter.isspace()}
    return sorted(caracter for caracter in usados if ord(caracter) not in disponibles)


def a_pdf(doc: dict) -> tuple[bytes, int]:
    """Devuelve el PDF y su número de páginas."""
    pdf = _Pdf(doc.get("pie_pagina") or "Nodo IA Caribe")
    pdf.add_page()
    margen = pdf.l_margin

    pdf.set_font("Poppins", "", 7.8)
    pdf.set_text_color(*AZUL)
    pdf.multi_cell(pdf.epw, 4, (doc.get("antetitulo") or "").upper(), align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("Poppins", "B", 16.5)
    pdf.set_text_color(*MARINO)
    pdf.multi_cell(pdf.epw, 7.6, doc["titulo"], align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2.2)

    estado = doc.get("estado") or {}
    clase = estado.get("clase", "pendiente")
    _caja(pdf, [b(ETIQUETA_ESTADO.get(clase, "Estado") + "."), " ", estado.get("texto")], clase, 9.2)

    if doc.get("ficha"):
        _tabla_pdf(
            pdf,
            {
                "cabecera": None,
                "filas": [[b(texto_plano(campo)), valor] for campo, valor in doc["ficha"]],
                "anchos": [1, 3.1],
            },
            tam=8.2,
        )

    for sec in doc.get("secciones") or []:
        # El título de una sección no se queda solo al pie de la página: va con lo que le sigue.
        primero = sec["bloques"][0] if sec["bloques"] else None
        alto_siguiente = _alto_minimo_tabla(primero) if primero and primero["tipo"] == "tabla" else 15.0
        if pdf.will_page_break(9 + alto_siguiente):
            pdf.add_page()
        pdf.ln(1.2)
        pdf.set_font("Poppins", "B", 11.5)
        pdf.set_text_color(*MARINO)
        pdf.multi_cell(pdf.epw, 6, sec["titulo"], align="L", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        for bloque in sec["bloques"]:
            tipo = bloque["tipo"]
            if tipo == "p":
                _escribir(pdf, bloque["texto"], 9.2, 4.5)
                pdf.ln(1.6)
            elif tipo == "h3":
                if pdf.will_page_break(18):
                    pdf.add_page()
                pdf.set_font("Poppins", "B", 9.6)
                pdf.set_text_color(*AZUL)
                pdf.multi_cell(pdf.epw, 5, texto_plano(bloque["texto"]), align="L", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(0.8)
            elif tipo == "aviso":
                _caja(pdf, bloque["texto"], bloque.get("clase", "parcial"), 8.6)
            elif tipo == "lista":
                for numero, item in enumerate(bloque["items"], 1):
                    if pdf.will_page_break(9):
                        pdf.add_page()
                    pdf.set_font("Poppins", "", 9.2)
                    pdf.set_text_color(*TENUE)
                    pdf.set_x(margen + 1)
                    pdf.cell(6, 4.5, f"{numero}." if bloque["ordenada"] else "•", new_x="RIGHT", new_y="TOP")
                    _escribir(pdf, item, 9.2, 4.5, sangria=7)
                    pdf.set_x(margen)
                    pdf.ln(0.7)
                pdf.ln(1.2)
            elif tipo == "tabla":
                _tabla_pdf(pdf, bloque)

    if doc.get("pie"):
        pdf.ln(1)
        pdf.set_font("Poppins", "", 7.6)
        pdf.set_text_color(*TENUE)
        pdf.multi_cell(pdf.epw, 3.8, doc["pie"], align="L", new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output()), pdf.page_no()
