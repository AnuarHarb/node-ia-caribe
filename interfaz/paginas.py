"""Plantillas HTML de la interfaz."""

from __future__ import annotations

import html
import json

from interfaz.catalogo import DEMOS
from interfaz.informes import estado_hipotesis_portada, resumen_tarjeta
from interfaz.red import enlace_telefono
from voz.frases import FRASES

REPO_GITHUB = "https://github.com/AnuarHarb/node-ia-caribe"


def e(texto: object) -> str:
    return html.escape(str(texto))


def _marca_estado_demo(estado: str, etiqueta: str) -> str:
    iconos = {
        "ok": (
            '<svg class="demo-estado-glyph" width="22" height="22" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>'
        ),
        "falla": (
            '<svg class="demo-estado-glyph" width="22" height="22" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>'
        ),
        "parcial": (
            '<svg class="demo-estado-glyph" width="22" height="22" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2.5" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
            '<path d="M8 12h8"/></svg>'
        ),
        "pendiente": (
            '<svg class="demo-estado-glyph" width="22" height="22" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
            '<path d="M12 7v5l3 2"/></svg>'
        ),
    }
    icono = iconos.get(estado, iconos["pendiente"])
    clase = e(estado)
    return (
        f'<span class="demo-tarjeta-estado demo-tarjeta-estado--{clase}" role="status">'
        f'{icono}<span class="demo-tarjeta-estado-texto">{e(etiqueta)}</span></span>'
    )


def _fca_kicker(texto: str) -> str:
    return (
        f'<p class="fca-kicker"><span class="fca-bars" aria-hidden="true">'
        f"<i></i><i></i><i></i></span>{e(texto)}</p>"
    )


def _head_css() -> str:
    return """<link rel="stylesheet" href="/static/fca/fca-fonts.css">
  <link rel="stylesheet" href="/static/fca/FCA_Sistema-de-diseno/tokens.css">
  <link rel="stylesheet" href="/static/fca/FCA_Sistema-de-diseno/componentes/fca-componentes.css">
  <link rel="stylesheet" href="/static/app.css">"""


DEMO_ICONOS: dict[int, str] = {
    1: (
        '<svg class="demo-tarjeta-svg" width="40" height="40" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>'
        '<path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>'
    ),
    2: (
        '<svg class="demo-tarjeta-svg" width="40" height="40" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>'
        '<path d="m4.9 4.9 14.2 14.2"/></svg>'
    ),
    3: (
        '<svg class="demo-tarjeta-svg" width="40" height="40" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false"><path d="m16 3 4 4-4 4"/><path d="M20 7H4"/>'
        '<path d="m8 21-4-4 4-4"/><path d="M4 17h16"/></svg>'
    ),
    4: (
        '<svg class="demo-tarjeta-svg" width="40" height="40" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false"><path d="M3 3v18h18"/><path d="M7 16V9"/><path d="M11 16V5"/>'
        '<path d="M15 16v-3"/><path d="M19 16V7"/></svg>'
    ),
    5: (
        '<svg class="demo-tarjeta-svg" width="40" height="40" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>'
        '<path d="M9 12l2 2 4-4"/></svg>'
    ),
}


def _cabecera(titulo: str, intro: str, breadcrumb: str | None = None, demo_id: int | None = None, *, portada: bool = False) -> str:
    migas = ""
    if breadcrumb:
        migas = f'<nav class="breadcrumb" aria-label="Ubicación"><a href="/">Inicio</a> · {breadcrumb}</nav>'
    body_attr = f' data-demo="{demo_id}"' if demo_id is not None else ""
    meta_demo = ""
    if demo_id is not None:
        meta_demo = f"""<p class="demo-meta">
      <span class="fca-pill">TRL 3</span>
      <span class="fca-pill fca-pill--soft">Demo {demo_id}</span>
      <span class="fca-pill fca-pill--soft">Evidencia local</span>
    </p>"""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(titulo if titulo != "Nodo IA Caribe" else "Laboratorio TRL 3")} · Nodo IA Caribe</title>
  {_head_css()}
</head>
<body class="fca-root{" portada" if portada else ""}"{body_attr}>
  <header class="site-header">
    <a class="brand-lockup" href="/">
      <img src="/static/fca/FCA_Sistema-de-diseno/logos/fca-lockup-color.png" width="200" height="40" alt="Fundación Código Abierto">
    </a>
    <div class="header-circuit" aria-hidden="true"></div>
    {migas}
    {_fca_kicker("Nodo IA Caribe · laboratorio TRL 3")}
    <h1 class="page-title">{e(titulo)}</h1>
    <p class="intro-lead body-sm">{e(intro)}</p>
    {meta_demo}
  </header>
  <main>
"""


def _pie(extra_script: str = "", *, demo: bool = False) -> str:
    scripts_demo = ""
    if demo:
        scripts_demo = '<script src="/static/corrida-video.js"></script>\n  '
    return f"""  </main>
  <footer class="site-footer">
    <div class="footer-bars" aria-hidden="true"><span class="fca-bars"><i></i><i></i><i></i><i></i><i></i></span></div>
    <p class="body-sm">Nodo IA Caribe · <a href="https://codigoabierto.tech" rel="noopener">Fundación Código Abierto</a>.
      Informes en <code>resultados/</code> · <a href="/nota-tecnica">Nota técnica</a> ·
      <a href="{e(REPO_GITHUB)}" rel="noopener">Repositorio</a> ·
      <a href="{e(REPO_GITHUB + "/blob/main/LICENSE")}" rel="noopener">Licencia</a>.
      Videos de corrida (demos 2–5): <code>resultados/demoN/historial/</code>.</p>
  </footer>
  {scripts_demo}<script src="/static/escenario.js"></script>
  <script src="/static/app.js"></script>
  {extra_script}
</body>
</html>
"""


def inicio() -> str:
    tarjetas = []
    for demo_id in range(1, 6):
        meta = DEMOS[demo_id]
        hipotesis = estado_hipotesis_portada(demo_id)
        metrica = hipotesis.get("detalle") or resumen_tarjeta(demo_id)
        icono = DEMO_ICONOS.get(demo_id, "")
        marca = _marca_estado_demo(hipotesis["estado"], hipotesis["etiqueta"])
        tarjetas.append(
            f"""<li class="demo-carrusel-item">
          <a class="fca-card demo-tarjeta demo-tarjeta--{e(hipotesis["estado"])}" href="/demo/{demo_id}">
            {marca}
            <span class="demo-tarjeta-numero" aria-hidden="true">{demo_id:02d}</span>
            <span class="demo-tarjeta-icono">{icono}</span>
            <span class="demo-tarjeta-cuerpo">
              <span class="demo-tarjeta-encabezado">
                <span class="fca-pill fca-pill--soft">Demo {demo_id}</span>
                <span class="demo-tarjeta-titulo">{e(meta["titulo"])}</span>
              </span>
              <span class="demo-tarjeta-resumen body-sm">{e(meta["tesis"])}</span>
              <span class="demo-tarjeta-metrica">{e(metrica)}</span>
            </span>
          </a>
        </li>"""
        )
    cuerpo = _cabecera(
        "Nodo IA Caribe",
        "Pruebas de laboratorio del punto de partida (TRL 3). Cada demo se corre en este equipo, se mide y deja un informe.",
        portada=True,
    )
    cuerpo += """<p class="portada-nota">Orden 1 → 5. Desliza o usa las flechas. <strong>Verde ✓</strong> hipótesis cumplida, <strong>rojo ✗</strong> no cumplida, <strong>amarillo</strong> por ejecutar o en progreso. El pie de cada tarjeta resume la última medición.</p>"""
    cuerpo += """<p class="portada-entrega body-sm"><a href="/nota-tecnica">Nota técnica</a> (video 2–3 min, enlace al repositorio y evidencias). Al correr un demo desde la interfaz se guarda un <strong>video corto</strong> junto al informe en el historial.</p>"""
    cuerpo += f"""<section class="demo-carrusel-seccion" aria-labelledby="demos-portada-titulo">
      <div class="demo-carrusel-cabecera">
        <h2 id="demos-portada-titulo" class="demo-carrusel-titulo">Demos del laboratorio</h2>
        <div class="demo-carrusel-controles">
          <button type="button" class="fca-btn fca-btn--secondary demo-carrusel-btn" data-dir="-1" aria-label="Ver demos anteriores">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>
          </button>
          <button type="button" class="fca-btn fca-btn--secondary demo-carrusel-btn" data-dir="1" aria-label="Ver demos siguientes">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>
          </button>
        </div>
      </div>
      <div class="demo-carrusel" id="demo-carrusel" tabindex="0" role="region" aria-label="Carrusel de demos">
        <ul class="demo-carrusel-pista">
          {"".join(tarjetas)}
        </ul>
      </div>
    </section>"""
    return cuerpo + _pie()


def demo(demo_id: int) -> str:
    meta = DEMOS[demo_id]
    cuerpo = _cabecera(
        f"Demo {demo_id}. {meta['titulo']}",
        meta["tesis"],
        f"{demo_id} · {meta['titulo']}",
        demo_id=demo_id,
    )

    hero_botones = ""
    if demo_id == 1:
        hero_botones = '<p class="hero-ayuda">Graba en costeño en el bloque de abajo. Cada medición guardada entra al historial.</p>'
    else:
        hero_botones = (
            f"""<button type="button" class="fca-btn hero-correr" data-demo-correr="{demo_id}">"""
            """Correr experimento</button>"""
        )
        if demo_id == 3:
            hero_botones += (
                '<p id="demo3-aviso-api" class="hero-ayuda demo3-aviso-api" role="status">'
                "Sin API key de referencia comercial: solo se ejecutará la mitad local (40 respuestas en Ollama).</p>"
            )

    explicacion = e(meta.get("explicacion_simple", meta["tesis"]))
    criterio_corto = e(meta.get("criterio_corto", meta["criterio"]))
    que_pasa = f"""<article class="demo-explicacion fca-card" aria-labelledby="demo-que-pasa-titulo">
      <div class="demo-explicacion-cabecera">
        <h2 id="demo-que-pasa-titulo" class="demo-explicacion-titulo">¿Qué va a pasar aquí?</h2>
        <button type="button" class="fca-btn fca-btn--secondary demo-btn-voz" id="leer-explicacion" aria-describedby="demo-que-pasa-titulo">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>
          <span class="demo-btn-voz-texto">Escuchar explicación</span>
        </button>
      </div>
      <p class="demo-explicacion-texto" id="demo-explicacion-texto">{explicacion}</p>
      <p class="demo-explicacion-criterio"><strong>Criterio de éxito:</strong> {criterio_corto}</p>
      <p class="demo-explicacion-voz-estado" id="leer-explicacion-estado" role="status" hidden></p>
      <audio id="audio-explicacion" preload="none" class="sr-only-audio"></audio>
    </article>
    """

    tabs = f"""{que_pasa}<nav class="demo-tabs" aria-label="Secciones del demo">
      <button type="button" class="demo-tab activa" role="tab" id="tab-btn-experimento" aria-selected="true" aria-controls="tab-experimento" data-tab="experimento">Experimento</button>
      <button type="button" class="demo-tab" role="tab" id="tab-btn-resultados" aria-selected="false" aria-controls="tab-resultados" data-tab="resultados">Resultados</button>
    </nav>
    <section id="tab-experimento" class="tab-panel activa" role="tabpanel" aria-labelledby="tab-btn-experimento">
      <div class="corrida-hero panel fca-card">
        <p class="estado-corrida" id="estado-corrida" data-estado="reposo">
          <span class="estado-punto" aria-hidden="true"></span>
          <span class="estado-texto">En reposo · listo para correr</span>
        </p>
        <div class="hero-acciones">{hero_botones}</div>
      </div>
      <div id="escenario" class="escenario vacio escenario-hero" data-escenario="{demo_id}" hidden>
        <p class="escenario-pie" aria-live="polite"></p>
      </div>
      <article id="resultado-rapido" class="resultado-rapido panel fca-card" hidden aria-live="polite">
        <h2>Última corrida</h2>
        <div id="informe-rapido"></div>
        <p><button type="button" class="fca-btn fca-btn--secondary" data-ir-tab="resultados">Ver en historial</button></p>
      </article>
      __EXTRA_EXPERIMENTO__
      <details class="bitacora-details panel">
        <summary>Bitácora técnica de la sesión</summary>
        <ul id="avance" aria-live="polite" aria-label="Avance de la corrida"></ul>
      </details>
    </section>
    <section id="tab-resultados" class="tab-panel" role="tabpanel" aria-labelledby="tab-btn-resultados" hidden>
      {('<section id="demo3-resultados-ciego" class="panel fca-card demo3-paso-ciego" hidden aria-labelledby="demo3-res-ciego-titulo">'
      '<h2 id="demo3-res-ciego-titulo">Calificación ciega pendiente</h2>'
      '<p class="body-sm">El paquete ciego ya está en el laboratorio. Dos personas deben puntuar las respuestas A y B antes de calcular quién respondió mejor.</p>'
      '<p id="demo3-res-ciego-resumen" class="demo3-ciego-resumen" role="status"></p>'
      '<p class="hero-acciones"><a id="btn-calificar-ciego-resultados" class="fca-btn" href="/calificar?paquete=actual">Calificar paquete ciego</a></p>'
      '</section>') if demo_id == 3 else ''}
      <div class="resultados-layout">
        <aside class="panel fca-card historial-aside">
          <h2>Historial</h2>
          <ul id="historial-lista" class="historial-lista"></ul>
          <p id="historial-vacio" class="pendiente">Todavía no hay corridas guardadas.</p>
        </aside>
        <article id="historial-detalle" class="panel fca-card panel-informe historial-detalle">
          <nav class="informe-exportar" aria-label="Exportar informe" id="historial-exportar" hidden>
            <a class="enlace-json" id="hist-link-imprimir" href="#" target="_blank" rel="noopener">Vista PDF</a>
            <a class="enlace-json" id="hist-link-pdf" href="#">Descargar PDF</a>
          </nav>
          <p class="pendiente">Elige una corrida de la lista para ver el detalle.</p>
        </article>
      </div>
    </section>
    <details class="protocolo-details panel fca-card">
      <summary>Protocolo y criterio</summary>
      <p>{e(meta["montaje"])}</p>
      <dl class="protocolo-dl">
        <dt>Criterio de éxito</dt>
        <dd>{e(meta["criterio"])}</dd>
        <dt>Responsable</dt>
        <dd>{e(meta["responsable"])}</dd>
      </dl>
    </details>"""

    extra = ""
    if demo_id == 1:
        extra = _bloque_voz()
    if demo_id == 2:
        enlace = enlace_telefono()
        valor_ip = e(enlace["ip"] or enlace.get("ip_detectada") or "")
        aviso_ip = (
            ""
            if enlace["ip"]
            else '<p class="aviso" id="aviso-ip">No detecté la IP en la red. Escríbela abajo (Ajustes → Red en el Mac, o la IP que muestra el router).</p>'
        )
        extra = f"""<section class="panel fca-card" aria-labelledby="telefono-titulo">
      <h2 id="telefono-titulo">Consulta desde el teléfono</h2>
      <p>Con el router <strong>sin internet</strong>, cada teléfono en la misma Wi‑Fi escanea el QR o abre el enlace. Si cambias de red o de computador, ajusta la IP: el QR y el enlace se actualizan aquí (solo en este navegador; no hace falta tocar el código).</p>
      <form id="form-ip-telefono" class="ip-form">
        <label for="ip-manual">IPv4 de este Mac en la red del router
          <input id="ip-manual" name="ip" type="text" inputmode="decimal" autocomplete="off" spellcheck="false" placeholder="192.168.0.24" value="{valor_ip}">
        </label>
        <div class="ip-acciones">
          <button type="submit" class="fca-btn">Actualizar QR y enlace</button>
          <button type="button" class="fca-btn fca-btn--secondary" id="ip-detectar">Usar IP detectada</button>
        </div>
        <p id="ip-estado" class="aviso" role="status" hidden></p>
      </form>
      <div class="qr-telefono">
        <img id="qr-telefono" src="/api/demo2/qr.svg" width="220" height="220" alt="Código QR para abrir la consulta por voz en el teléfono">
        <div class="qr-texto">
          <p class="enlace-destacado"><a id="url-telefono-abrir" href="{e(enlace["url"])}">{e(enlace["texto"])}</a></p>
          <p><code id="url-telefono">{e(enlace["texto"])}</code></p>
          <p class="acciones-enlace">
            <button type="button" class="fca-btn fca-btn--secondary" id="copiar-url-telefono">Copiar enlace</button>
          </p>
          {aviso_ip}
          <p>En el computador, la sala en <a href="/voz/sala">/voz/sala</a>.</p>
        </div>
      </div>
    </section>"""
    if demo_id == 3:
        extra = """<section class="panel fca-card" aria-labelledby="referencia-titulo">
      <h2 id="referencia-titulo">Referencia comercial (segunda mitad)</h2>
      <p>Un solo botón <strong>Correr experimento</strong> arriba hace la corrida local y, si hay clave, la referencia comercial en el mismo flujo. La API key se usa solo en esa corrida, <strong>no se guarda en disco</strong> ni en el informe. También valen <code>ANTHROPIC_API_KEY</code> / <code>OPENAI_API_KEY</code> en el entorno del servidor.</p>
      <form id="form-referencia-demo3" class="ref-form">
        <label for="ref-proveedor">Proveedor
          <select id="ref-proveedor" name="proveedor">
            <option value="anthropic" selected>Anthropic</option>
            <option value="openai">OpenAI</option>
          </select>
        </label>
        <label for="ref-modelo">Modelo
          <input id="ref-modelo" name="modelo" type="text" value="claude-haiku-4-5" autocomplete="off" spellcheck="false">
        </label>
        <label for="ref-api-key">API key (opcional en el primer intento)
          <input id="ref-api-key" name="api_key" type="password" autocomplete="off" spellcheck="false" placeholder="sk-ant-… o sk-…">
        </label>
        <label class="ref-recordar">
          <input id="ref-recordar" type="checkbox">
          Recordar la clave solo en esta pestaña del navegador
        </label>
        <p id="ref-estado" class="aviso" role="status" hidden></p>
      </form>
      <p>Cuando existan las 40 respuestas locales y las 40 de referencia, se genera el paquete ciego en <code>resultados/demo3/ciego.json</code>.</p>
    </section>
    <section id="demo3-paso-ciego" class="panel fca-card demo3-paso-ciego" hidden aria-labelledby="demo3-ciego-titulo">
      <h2 id="demo3-ciego-titulo">Siguiente paso: calificación ciega</h2>
      <p class="body-sm">Dos personas distintas leen cada tarea con <strong>respuesta A</strong> y <strong>respuesta B</strong> sin saber cuál salió del modelo local y cuál de la referencia comercial. Así se cierra la comparación (aún no hay ganador hasta calificar).</p>
      <p id="demo3-ciego-resumen" class="demo3-ciego-resumen" role="status"></p>
      <p class="hero-acciones">
        <a id="btn-calificar-ciego" class="fca-btn" href="/calificar?paquete=actual">Calificar paquete ciego</a>
      </p>
    </section>"""

    cuerpo += tabs.replace("__EXTRA_EXPERIMENTO__", extra)
    return cuerpo + _pie(_script_voz_si(demo_id), demo=True)


def _bloque_voz() -> str:
    frases_json = json.dumps(FRASES, ensure_ascii=False)
    return f"""<section class="panel fca-card voz-grid" aria-labelledby="voz-titulo">
      <h2 id="voz-titulo">Sesión de voz (demo 1)</h2>
      <p>Consentimiento escrito antes de grabar. El audio no se publica.</p>
      <label>Nombre de quien habla
        <input id="persona" name="persona" type="text" autocomplete="name" required>
      </label>
      <label>
        <input id="consentimiento" type="checkbox">
        Hay consentimiento de donación de voz
      </label>
      <p id="frase-guion"></p>
      <section id="escenario-voz" class="escenario escenario-1 vacio" aria-label="Flujo de voz en vivo">
        <ol class="flujo-voz">
          <li data-paso="grabar">Grabar</li>
          <li data-paso="transcribir">Transcribir</li>
          <li data-paso="responder">Responder</li>
        </ol>
        <p class="escenario-pie" aria-live="polite">Listo para grabar.</p>
      </section>
      <div class="fila-boton">
        <button type="button" id="grabar" class="fca-btn">Grabar</button>
        <button type="button" id="detener" disabled>Detener y enviar</button>
      </div>
      <p id="estado-voz" role="status"></p>
      <p><strong>Transcripción del sistema:</strong> <span id="transcripcion">—</span></p>
      <p><strong>Respuesta:</strong> <span id="respuesta-voz"></span></p>
      <audio id="audio-respuesta" controls></audio>
      <label>Transcripción correcta
        <textarea id="correcta" rows="3"></textarea>
      </label>
      <fieldset>
        <legend>¿La transcripción del sistema quedó bien?</legend>
        <label><input type="radio" name="ok" value="si"> Sí</label>
        <label><input type="radio" name="ok" value="no"> No</label>
      </fieldset>
      <button type="button" id="guardar-fila" class="fca-btn">Guardar medición</button>
    </section>
    <script>
    const FRASES = {frases_json};
    let indice = 0;
    let grabacion = null;
    let trozos = [];
    let ultimo = null;
    const fraseEl = document.getElementById("frase-guion");
    function mostrarFrase() {{ fraseEl.textContent = FRASES[indice]; }}
    mostrarFrase();
    document.getElementById("grabar").onclick = async () => {{
      if (!document.getElementById("consentimiento").checked || !document.getElementById("persona").value.trim()) {{
        document.getElementById("estado-voz").textContent = "Falta nombre o consentimiento.";
        return;
      }}
      trozos = [];
      const flujo = await navigator.mediaDevices.getUserMedia({{ audio: true }});
      grabacion = new MediaRecorder(flujo);
      grabacion.ondataavailable = (ev) => {{ if (ev.data.size) trozos.push(ev.data); }};
      grabacion.onstop = enviarAudio;
      grabacion.start();
      document.getElementById("grabar").disabled = true;
      document.getElementById("detener").disabled = false;
      document.getElementById("estado-voz").textContent = "Grabando.";
      if (typeof setEstadoCorrida === "function") setEstadoCorrida("corriendo", "Grabando voz…");
      if (typeof escenarioVozPaso === "function") escenarioVozPaso("grabar", "Grabando la frase en costeño.");
    }};
    document.getElementById("detener").onclick = () => {{
      if (grabacion && grabacion.state !== "inactive") grabacion.stop();
    }};
    async function enviarAudio() {{
      const blob = new Blob(trozos, {{ type: grabacion.mimeType }});
      grabacion.stream.getTracks().forEach((t) => t.stop());
      const b64 = await new Promise((res) => {{
        const r = new FileReader();
        r.onload = () => res(String(r.result).split(",")[1]);
        r.readAsDataURL(blob);
      }});
      document.getElementById("estado-voz").textContent = "Procesando en el equipo…";
      if (typeof escenarioVozPaso === "function") escenarioVozPaso("transcribir", "Whisper transcribe en este Mac…");
      const resp = await fetch("/api/voz/turno", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
          demo: 1,
          persona: document.getElementById("persona").value.trim(),
          guion: FRASES[indice],
          audio_b64: b64,
          mime: blob.type
        }})
      }});
      const data = await resp.json();
      document.getElementById("grabar").disabled = false;
      document.getElementById("detener").disabled = true;
      if (!resp.ok) {{
        document.getElementById("estado-voz").textContent = data.error || "Falló.";
        return;
      }}
      ultimo = data;
      document.getElementById("transcripcion").textContent = data.transcripcion || "(vacía)";
      document.getElementById("respuesta-voz").textContent = data.respuesta;
      document.getElementById("audio-respuesta").src = "data:audio/wav;base64," + data.audio_b64;
      if (typeof escenarioVozPaso === "function") escenarioVozPaso("responder", "Ollama responde y Piper sintetiza la voz.");
      document.getElementById("estado-voz").textContent = "Listo en " + data.segundos + " s.";
      indice = (indice + 1) % FRASES.length;
      mostrarFrase();
    }};
    document.getElementById("guardar-fila").onclick = async () => {{
      if (!ultimo) return;
      const ok = document.querySelector('input[name="ok"]:checked');
      if (!ok) return;
      await fetch("/api/voz/fila", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
          id: ultimo.id,
          persona: document.getElementById("persona").value.trim(),
          guion: ultimo.guion,
          transcripcion_correcta: document.getElementById("correcta").value.trim(),
          transcripcion_sistema: ultimo.transcripcion,
          correcta: ok.value,
          audio: ultimo.audio
        }})
      }});
      document.getElementById("estado-voz").textContent = "Fila guardada. Informe actualizado.";
      if (typeof mostrarUltimoResultado === "function") mostrarUltimoResultado(1);
      if (typeof setEstadoCorrida === "function") setEstadoCorrida("ok", "Medición guardada en el historial.");
    }};
    </script>"""


def _script_voz_si(demo_id: int) -> str:
    if demo_id == 1:
        return ""
    return ""


def _markdown_simple(texto: str) -> str:
    partes: list[str] = []
    for bloque in texto.split("\n\n"):
        bloque = bloque.strip()
        if not bloque:
            continue
        if bloque.startswith("# "):
            partes.append(f"<h1>{e(bloque[2:])}</h1>")
            continue
        if bloque.startswith("## "):
            partes.append(f"<h2>{e(bloque[3:])}</h2>")
            continue
        if bloque.startswith("### "):
            partes.append(f"<h3>{e(bloque[4:])}</h3>")
            continue
        if bloque.startswith("|"):
            filas = [
                "<tr>"
                + "".join(f"<td>{e(celda.strip())}</td>" for celda in fila.split("|")[1:-1])
                + "</tr>"
                for fila in bloque.splitlines()
                if fila.strip().startswith("|") and not set(fila.replace("|", "").strip()) <= {"-", " "}
            ]
            if filas:
                partes.append(
                    '<table class="nota-tabla"><tbody>' + "".join(filas) + "</tbody></table>"
                )
            continue
        if bloque.startswith("- "):
            items = "".join(f"<li>{e(linea[2:])}</li>" for linea in bloque.splitlines() if linea.startswith("- "))
            partes.append(f"<ul>{items}</ul>")
            continue
        partes.append(f"<p>{e(bloque)}</p>")
    return "\n".join(partes)


def nota_tecnica() -> str:
    import os
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[1]
    archivo = raiz / "notas" / "NOTA_TECNICA.md"
    texto = archivo.read_text(encoding="utf-8") if archivo.is_file() else "Falta notas/NOTA_TECNICA.md."
    repo = os.environ.get("NODO_REPO_URL", "").strip()
    if repo:
        texto = texto.replace("REPOSITORIO_PENDIENTE", repo)
    cuerpo = _cabecera(
        "Nota técnica del laboratorio",
        "Evidencia TRL 3 · Nodo IA Caribe. Incluye enlace al repositorio, al video de presentación y a las corridas medidas.",
        breadcrumb="Nota técnica",
    )
    cuerpo += f'<article class="nota-tecnica panel fca-card">{_markdown_simple(texto)}</article>'
    cuerpo += """<p class="body-sm"><a href="/">← Volver a la portada</a></p>"""
    return cuerpo + _pie()


def pagina_voz(modo: str) -> str:
    from voz.pagina import PAGINA

    return PAGINA.replace("FRASES_JSON", json.dumps(FRASES, ensure_ascii=False))


def pagina_calificar() -> str:
    path = __import__("pathlib").Path(__file__).resolve().parents[1] / "demo3_comparacion" / "calificar.html"
    return path.read_text(encoding="utf-8").replace(
        'href="/static/app.css"',
        'href="/static/app.css"',
    )
