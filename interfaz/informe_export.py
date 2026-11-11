"""Informe exportable: HTML para imprimir y PDF para archivar."""

from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF

from interfaz.catalogo import DEMOS

RAIZ = Path(__file__).resolve().parents[1]
FUENTES_FCA = Path(__file__).resolve().parent / "static" / "fca" / "FCA_Sistema-de-diseno" / "fuentes"

CAMPOS_OMITIR_DEMO1 = {
    "tabla",
    "modelos",
    "wer_corpus",
    "wer_por_persona",
    "tiempos_promedio",
    "resumen_ejecutivo",
    "definicion_wer",
    "video_corrida",
    "observaciones_llm",
    "nota_referencias",
    "implicacion_alucinaciones",
}

CAMPOS_OMITIR = {
    "tabla",
    "filas",
    "eventos",
    "variedades",
    "detalle",
    "equipo",
    "bloqueo",
    "demo",
    "comparacion",
    "rendimiento",
    "paquete_ciego",
    "protocolo_checklist",
    "resumen_ejecutivo",
    "criterio_protocolo",
}


def _e(texto: object) -> str:
    return html.escape(str(texto), quote=True)


def _formatear_fecha(valor: str | None) -> str:
    if not valor:
        return "—"
    try:
        d = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        return d.strftime("%d %b %Y, %H:%M %z")
    except ValueError:
        return str(valor)


def _texto_equipo(equipo: dict | None) -> str:
    if not equipo:
        return "—"
    partes = [
        equipo.get("procesador"),
        f"{equipo.get('memoria_gb')} GB" if equipo.get("memoria_gb") else None,
        equipo.get("sistema"),
        f"Python {equipo.get('python')}" if equipo.get("python") else None,
    ]
    return ", ".join(p for p in partes if p)


def _estado_linea(informe: dict, meta: dict) -> str:
    if informe.get("criterio_cumplido") is True:
        return "Criterio cumplido (método y calificación)."
    if informe.get("criterio_metodo_armado"):
        pendiente = informe.get("pendiente_calificacion") or "calificación humana"
        return f"Paquete ciego listo. Pendiente: {pendiente}."
    if informe.get("criterio_cumplido") is False:
        return "Criterio no cumplido."
    if informe.get("parcial"):
        return "Medición parcial (revisar protocolo)."
    if informe.get("pendiente") or informe.get("pendiente_calificacion"):
        return "Evidencia incompleta: " + str(
            informe.get("pendiente") or informe.get("pendiente_calificacion") or "pendiente"
        )
    return "Informe de laboratorio TRL 3."


def _filas_metadatos(informe: dict) -> list[tuple[str, str]]:
    filas = []
    omitir = CAMPOS_OMITIR | (CAMPOS_OMITIR_DEMO1 if informe.get("demo") == 1 else set())
    for clave, valor in informe.items():
        if clave in omitir or valor is None or isinstance(valor, (dict, list)):
            continue
        etiqueta = clave.replace("_", " ").capitalize()
        if isinstance(valor, bool):
            texto = "Sí" if valor else "No"
        else:
            texto = str(valor)
        filas.append((etiqueta, texto))
    return filas


def _tabla_pruebas(informe: dict) -> str:
    filas = informe.get("filas")
    if not filas or not isinstance(filas, list) or not filas[0].get("prueba"):
        return ""
    cuerpo = ""
    for fila in filas:
        cuerpo += (
            f"<tr><td><code>{_e(fila.get('prueba', ''))}</code></td>"
            f"<td>{_e(fila.get('esperado', ''))}</td>"
            f"<td>{_e(fila.get('obtenido', ''))}</td></tr>"
        )
    return f"""<section>
      <h2>Pruebas automatizadas</h2>
      <table>
        <thead><tr><th>Prueba</th><th>Esperado</th><th>Obtenido</th></tr></thead>
        <tbody>{cuerpo}</tbody>
      </table>
    </section>"""


def _seccion_demo1(informe: dict) -> str:
    if informe.get("demo") != 1 and not informe.get("wer_corpus"):
        return ""
    resumen = informe.get("resumen_ejecutivo")
    bloque_resumen = f"<p class=\"resumen-informe\">{_e(resumen)}</p>" if resumen else ""
    m = informe.get("modelos") or {}
    modelos = f"""<section>
      <h2>Modelos usados</h2>
      <table class="meta"><tbody>
        <tr><th>Reconocimiento (Whisper)</th><td>{_e(m.get('whisper', '—'))}</td></tr>
        <tr><th>Lenguaje (Ollama)</th><td>{_e(m.get('ollama', '—'))}</td></tr>
        <tr><th>Síntesis (Piper)</th><td>{_e(m.get('piper_asistente', '—'))}</td></tr>
      </tbody></table>
    </section>"""
    wc = informe.get("wer_corpus") or {}
    filas_wer = ""
    for p in informe.get("wer_por_persona") or []:
        filas_wer += (
            f"<tr><td>{_e(p.get('persona', ''))}</td><td>{_e(p.get('frases', ''))}</td>"
            f"<td>{_e(p.get('wer_porcentaje', ''))} %</td></tr>"
        )
    tabla_hablantes = (
        f"<table><thead><tr><th>Hablante</th><th>Frases</th><th>WER</th></tr></thead><tbody>{filas_wer}</tbody></table>"
        if filas_wer
        else ""
    )
    wer = f"""<section>
      <h2>Error por palabra (WER)</h2>
      <p>Corpus completo: <strong>{_e(wc.get('wer_porcentaje', '—'))} %</strong> WER
      ({_e(wc.get('palabras_referencia', ''))} palabras de referencia).</p>
      {tabla_hablantes}
    </section>"""
    tp = informe.get("tiempos_promedio") or {}
    tiempos = ""
    if tp:
        tiempos = f"""<section>
      <h2>Tiempos promedio por etapa</h2>
      <table class="meta"><tbody>
        <tr><th>Escuchar (ASR)</th><td>{_e(tp.get('asr_promedio_s', '—'))} s</td></tr>
        <tr><th>Entender y responder (LLM)</th><td>{_e(tp.get('llm_promedio_s', '—'))} s</td></tr>
        <tr><th>Hablar (TTS)</th><td>{_e(tp.get('tts_promedio_s', '—'))} s</td></tr>
        <tr><th>Total punta a punta</th><td>{_e(tp.get('total_promedio_s', '—'))} s</td></tr>
      </tbody></table>
    </section>"""
    video = ""
    if informe.get("video_corrida"):
        video = f'<p><a href="{_e(informe["video_corrida"])}">Video de la corrida (evidencia punta a punta)</a></p>'
    refs = ""
    if informe.get("nota_referencias"):
        refs = f'<p class="body-sm">{_e(informe["nota_referencias"])}</p>'
    aluc = ""
    if informe.get("observaciones_llm"):
        items = "".join(
            f"<li><strong>{_e(h.get('id', ''))}</strong> — {_e(h.get('observacion', ''))}</li>" for h in informe["observaciones_llm"]
        )
        pie = informe.get("implicacion_alucinaciones", "")
        aluc = f"""<section>
      <h2>Respuestas del asistente (alucinaciones observadas)</h2>
      <ul>{items}</ul>
      <p>{_e(pie)}</p>
    </section>"""
    return bloque_resumen + refs + modelos + wer + tiempos + aluc + video


def _tabla_voz(informe: dict) -> str:
    tabla = informe.get("tabla")
    if not tabla:
        return ""
    cuerpo = ""
    for fila in tabla:
        audio = ""
        if fila.get("audio_entrada_url"):
            audio = f'<a href="{_e(fila["audio_entrada_url"])}">Entrada</a>'
        cuerpo += (
            f"<tr><td>{_e(fila.get('persona', ''))}</td>"
            f"<td>{_e(fila.get('transcripcion_correcta', ''))}</td>"
            f"<td>{_e(fila.get('transcripcion_sistema', ''))}</td>"
            f"<td>{_e(fila.get('wer_porcentaje', '—'))}</td>"
            f"<td>{_e(fila.get('respuesta_asistente', '') or '—')}</td>"
            f"<td>{_e(fila.get('asr_s', '—'))} / {_e(fila.get('llm_s', '—'))} / {_e(fila.get('tts_s', '—'))}</td>"
            f"<td>{audio or '—'}</td></tr>"
        )
    return f"""<section>
      <h2>Flujo punta a punta por frase</h2>
      <table>
        <thead><tr><th>Persona</th><th>Referencia</th><th>Transcripción ASR</th><th>WER %</th><th>Respuesta asistente</th><th>ASR / LLM / TTS (s)</th><th>Audio</th></tr></thead>
        <tbody>{cuerpo}</tbody>
      </table>
    </section>"""


def _tabla_wer(informe: dict) -> str:
    vars_ = informe.get("variedades")
    if not vars_:
        return ""
    cuerpo = ""
    for v in vars_:
        cuerpo += f"<tr><td>{_e(v.get('variedad', ''))}</td><td>{_e(v.get('frases', ''))}</td><td>{_e(v.get('wer_porcentaje', ''))} %</td></tr>"
    return f"""<section>
      <h2>WER por variedad</h2>
      <table>
        <thead><tr><th>Variedad</th><th>Frases</th><th>WER</th></tr></thead>
        <tbody>{cuerpo}</tbody>
      </table>
    </section>"""


def _tabla_eventos(informe: dict) -> str:
    eventos = informe.get("eventos")
    if not eventos:
        return ""
    cuerpo = ""
    for i, ev in enumerate(eventos, 1):
        cuerpo += (
            f"<tr><td>{i}</td><td>{_e(ev.get('entidad', ''))}</td><td>{_e(ev.get('accion', ''))}</td>"
            f"<td><code>{_e(ev.get('ruta', ''))}</code></td><td>{_e(ev.get('resultado', ''))}</td>"
            f"<td>{_e(ev.get('motivo', ''))}</td></tr>"
        )
    return f"""<section>
      <h2>Registro de auditoría (corrida visible)</h2>
      <table>
        <thead><tr><th>#</th><th>Entidad</th><th>Acción</th><th>Ruta</th><th>Resultado</th><th>Motivo</th></tr></thead>
        <tbody>{cuerpo}</tbody>
      </table>
    </section>"""


def _seccion_demo3(informe: dict) -> str:
    if informe.get("demo") != 3 and not informe.get("comparacion"):
        return ""
    resumen = informe.get("resumen_ejecutivo")
    bloque_resumen = f"<p class=\"resumen-informe\">{_e(resumen)}</p>" if resumen else ""
    c = informe.get("comparacion") or {}
    rl = (informe.get("rendimiento") or {}).get("local") or {}
    rr = (informe.get("rendimiento") or {}).get("referencia") or {}
    comp = f"""<section>
      <h2>Comparación local vs referencia</h2>
      <table>
        <thead><tr><th></th><th>Local ({_e(c.get('modelo_local', ''))})</th><th>Referencia ({_e(c.get('proveedor_referencia', ''))} · {_e(c.get('modelo_referencia', ''))})</th></tr></thead>
        <tbody>
          <tr><th>Respuestas completas</th><td>{_e(c.get('respuestas_local', ''))} / {_e(c.get('tareas_total', 40))}</td><td>{_e(c.get('respuestas_referencia', ''))} / {_e(c.get('tareas_total', 40))}</td></tr>
          <tr><th>Promedio en caliente (s)</th><td>{_e(rl.get('promedio_caliente_s', '—'))}</td><td>{_e(rr.get('promedio_caliente_s', '—'))}</td></tr>
          <tr><th>Promedio todas las tareas (s)</th><td>{_e(rl.get('promedio_todas_s', '—'))}</td><td>{_e(rr.get('promedio_todas_s', '—'))}</td></tr>
          <tr><th>Primera tarea / máximo caliente (s)</th><td>{_e(rl.get('primera_s', '—'))} / {_e(rl.get('maximo_caliente_s', '—'))}</td><td>— / {_e(rr.get('maximo_caliente_s', '—'))}</td></tr>
          <tr><th>Costo API (USD)</th><td>{_e(informe.get('costo_local_nota', '0 USD por consulta. No incluye energía ni equipo.'))}</td><td>—</td></tr>
        </tbody>
      </table>
      <p class="body-sm"><strong>Fecha de la corrida (40+40):</strong> {_formatear_fecha(str(informe.get('fecha_corrida') or informe.get('fecha') or ''))} ·
      <strong>Calificación ciega:</strong> {_formatear_fecha(str(informe.get('fecha_calificacion') or ''))}</p>
    </section>"""
    p = informe.get("paquete_ciego") or {}
    cal = p.get("calificacion") or {}
    ciego = f"""<section>
      <h2>Paquete ciego</h2>
      <p><strong>Estado:</strong> {'Generado' if p.get('listo') else 'No generado'}. {_e(p.get('aviso', ''))}</p>
      <table class="meta">
        <tbody>
          <tr><th>Identificador (hash)</th><td><code>{_e(p.get('hash', '—'))}</code></td></tr>
          <tr><th>Tareas en el paquete</th><td>{_e(p.get('tareas_en_paquete', ''))}</td></tr>
          <tr><th>Archivo para calificadores</th><td><code>{_e(p.get('archivo', ''))}</code></td></tr>
          <tr><th>Clave (solo laboratorio)</th><td><code>{_e(p.get('clave_archivo', ''))}</code></td></tr>
          <tr><th>Evaluadores</th><td>{_e(', '.join(cal.get('calificadores') or []) or '—')}</td></tr>
          <tr><th>Calificación humana</th><td>{_e(cal.get('descripcion', 'Pendiente'))}</td></tr>
          <tr><th>Kappa Cohen promedio</th><td>{_e(cal.get('kappa_cohen_promedio', '—'))}</td></tr>
        </tbody>
      </table>
      {f'<p class="body-sm">{_e(informe.get("limitacion_calificadores"))}</p>' if informe.get('limitacion_calificadores') else ''}
    </section>"""
    filas_chk = ""
    for fila in informe.get("protocolo_checklist") or []:
        ok = "Sí" if fila.get("cumple") else "No"
        filas_chk += f"<tr><td>{_e(fila.get('item', ''))}</td><td>{_e(fila.get('medido', ''))}</td><td>{ok}</td></tr>"
    checklist = f"""<section>
      <h2>Checklist del protocolo</h2>
      <table>
        <thead><tr><th>Paso</th><th>Medido</th><th>Cumple</th></tr></thead>
        <tbody>{filas_chk}</tbody>
      </table>
    </section>"""
    return bloque_resumen + comp + ciego + checklist


def _bloque_metadatos(informe: dict) -> str:
    items = _filas_metadatos(informe)
    if not items:
        return ""
    filas = "".join(f"<tr><th>{_e(k)}</th><td>{_e(v)}</td></tr>" for k, v in items)
    return f"""<section>
      <h2>Indicadores medidos</h2>
      <table class="meta">
        <tbody>{filas}</tbody>
      </table>
    </section>"""


def cuerpo_informe(demo_id: int, informe: dict, meta: dict) -> str:
    titulo = meta.get("titulo") or informe.get("titulo") or f"Demo {demo_id}"
    fecha = _formatear_fecha(informe.get("fecha"))
    equipo = _texto_equipo(informe.get("equipo"))
    estado = _estado_linea(informe, meta)
    return f"""<header class="doc-header">
    <p class="kicker">Nodo IA Caribe · evidencia de laboratorio TRL 3</p>
    <h1>Demo {demo_id}. {_e(titulo)}</h1>
    <p class="meta-line">Fecha: {_e(fecha)}<br>
    Equipo: {_e(equipo)}<br>
  Responsable: {_e(meta.get('responsable', ''))}</p>
    <p class="estado"><strong>{_e(estado)}</strong></p>
    <p class="criterio-protocolo"><strong>Criterio del protocolo:</strong> {_e(meta.get('criterio', ''))}</p>
  </header>
  <main>
    {_seccion_demo1(informe) if demo_id == 1 else ""}
    {_seccion_demo3(informe) if demo_id == 3 else ""}
    {_bloque_metadatos(informe)}
    {_tabla_pruebas(informe)}
    {_tabla_voz(informe)}
    {_tabla_wer(informe)}
    {_tabla_eventos(informe)}
  </main>
  <footer class="doc-footer">
    <p>Generado desde <code>resultados/demo{demo_id}/informe.json</code>. Sin cifras inventadas.</p>
  </footer>"""


ESTILOS_IMPRESION = """
    body { font-family: Palatino, "Iowan Old Style", Georgia, serif; max-width: 52rem; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; color: #1c1c1c; line-height: 1.45; font-size: 11pt; }
    .kicker { font-family: system-ui, sans-serif; font-size: 0.75rem; letter-spacing: 0.06em; text-transform: uppercase; color: #3d5c62; margin: 0 0 0.5rem; }
    h1 { font-size: 1.65rem; margin: 0 0 0.75rem; line-height: 1.2; }
    h2 { font-size: 1.1rem; margin: 1.5rem 0 0.5rem; color: #1d4e57; }
    table { border-collapse: collapse; width: 100%; margin: 0.5rem 0 1rem; font-size: 10pt; }
    th, td { border-bottom: 1px solid #ccc; text-align: left; vertical-align: top; padding: 0.35rem 0.45rem; }
    th { color: #3d5c62; font-weight: 600; }
    code { font-family: ui-monospace, monospace; font-size: 0.88em; }
    .estado { font-weight: 700; margin: 1rem 0; padding: 0.5rem 0.75rem; background: #eef4f6; border-left: 3px solid #1d4e57; }
    .criterio-protocolo { font-size: 0.95rem; }
    .meta-line { margin: 0 0 0.5rem; }
    .doc-footer { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #ccc; font-size: 0.85rem; color: #555; }
    .barra-acciones { font-family: system-ui, sans-serif; display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.5rem; padding: 0.75rem; background: #e7eef2; border: 1px solid #b8c5cc; }
    .barra-acciones a, .barra-acciones button { font: inherit; cursor: pointer; padding: 0.45rem 0.85rem; border: 1px solid #1d4e57; background: #1d4e57; color: #f8fbfc; text-decoration: none; }
    .barra-acciones a.sec, .barra-acciones button.sec { background: #f8fbfc; color: #14221c; }
    @media print {
      .barra-acciones { display: none !important; }
      body { padding: 0; max-width: none; }
      a[href]::after { content: none; }
    }
    @page { margin: 18mm 16mm; }
"""


def html_imprimible(demo_id: int, informe: dict, auto_imprimir: bool = False) -> str:
    meta = DEMOS[demo_id]
    script = ""
    if auto_imprimir:
        script = "<script>window.addEventListener('load', () => { window.print(); });</script>"
    acciones = f"""<div class="barra-acciones no-print">
      <button type="button" onclick="window.print()">Guardar como PDF</button>
      <a class="sec" href="/api/demos/{demo_id}/informe.pdf">Descargar PDF</a>
      <a class="sec" href="/demo/{demo_id}">Volver al demo</a>
    </div>"""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Informe · Demo {demo_id} · Nodo IA Caribe</title>
  <style>{ESTILOS_IMPRESION}</style>
</head>
<body>
  {acciones}
  {cuerpo_informe(demo_id, informe, meta)}
  {script}
</body>
</html>"""


class _InformePdf(FPDF):
    def __init__(self) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        regular = FUENTES_FCA / "Poppins-Regular.ttf"
        semibold = FUENTES_FCA / "Poppins-SemiBold.ttf"
        self.add_font("Poppins", "", str(regular))
        self.add_font("Poppins", "B", str(semibold))


def pdf_bytes(demo_id: int, informe: dict) -> bytes:
    meta = DEMOS[demo_id]
    fragmento = cuerpo_informe(demo_id, informe, meta)
    html_pdf = fragmento.replace('class="doc-header"', "").replace('class="kicker"', "")
    estilos = """<style>
    body, p, td, th, li { font-family: Poppins; font-size: 11pt; color: #1c1c1c; line-height: 1.45; }
    h1 { font-family: Poppins; font-size: 18pt; font-weight: bold; color: #14221c; }
    h2 { font-family: Poppins; font-size: 13pt; font-weight: bold; color: #1d4e57; }
    code { font-family: Courier; font-size: 10pt; }
    .estado { font-weight: bold; }
    </style>"""
    pdf = _InformePdf()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(18, 18, 18)
    pdf.add_page()
    pdf.set_font("Poppins", size=11)
    pdf.write_html(estilos + html_pdf)
    return bytes(pdf.output())


def guardar_pdf(demo_id: int, informe: dict) -> Path:
    destino = RAIZ / "resultados" / f"demo{demo_id}" / "informe.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(pdf_bytes(demo_id, informe))
    return destino
