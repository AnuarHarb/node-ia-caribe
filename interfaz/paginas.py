"""Plantillas HTML de la interfaz."""

from __future__ import annotations

import html
import json
import re

from interfaz.catalogo import DEMOS
from interfaz.informes import estado_hipotesis_portada, resumen_tarjeta
from interfaz.red import enlace_telefono
from voz.frases import FRASES, FRASES_PALENQUERO

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
  <link rel="stylesheet" href="/static/app.css">
  <link rel="stylesheet" href="/static/nota.css">"""


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
        scripts_demo = (
            '<script src="/static/corrida-video.js"></script>\n  '
            '<script src="/static/grabar-pantalla.js"></script>\n  '
        )
    return f"""  </main>
  <footer class="site-footer">
    <div class="footer-bars" aria-hidden="true"><span class="fca-bars"><i></i><i></i><i></i><i></i><i></i></span></div>
    <p class="body-sm">Nodo IA Caribe · <a href="https://codigoabierto.tech" rel="noopener">Fundación Código Abierto</a>.
      Grabaciones y mediciones sensibles: solo local (<code>resultados/</code>, <code>grabaciones/</code>).
      <a href="/medicion-base">Medición base del equipo</a> en <code>ejemplo/resultados/</code> ·
      <a href="/nota-tecnica">Entrega</a> ·
      <a href="{e(REPO_GITHUB)}" rel="noopener">Repositorio</a> ·
      <a href="{e(REPO_GITHUB + "/blob/main/LICENSE")}" rel="noopener">Licencia</a>.</p>
  </footer>
  {scripts_demo}<script src="/static/escenario.js"></script>
  <script src="/static/app.js"></script>
  {extra_script}
</body>
</html>
"""


def _portada_complementos() -> str:
    from ejemplo.datos import AUTORIZACION_PALENQUERO

    return f"""<section class="portada-complementos" aria-label="Información complementaria">
      <p class="body-sm portada-complementos-linea">
        <a href="/nota-tecnica">Entrega del laboratorio</a>
        <span class="portada-complementos-sep" aria-hidden="true">·</span>
        <a href="/medicion-base">Medición base del equipo</a>
        <span class="portada-complementos-sep" aria-hidden="true">·</span>
        Lo que grabes queda solo en <code>resultados/</code> en este computador.
      </p>
      <p class="body-sm portada-complementos-linea">{e(AUTORIZACION_PALENQUERO)}</p>
    </section>"""


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
              <span class="demo-tarjeta-resumen body-sm">{e(meta["pregunta"])}</span>
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
    cuerpo += """<p class="portada-nota">Orden 1 → 5. Desliza o usa las flechas. <strong>Verde ✓</strong> hipótesis cumplida, <strong>rojo ✗</strong> no cumplida, <strong>amarillo</strong> por ejecutar o en progreso. El pie de cada tarjeta resume la última medición.</p>"""
    cuerpo += _portada_complementos()
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
        hero_botones = (
            '<p class="hero-ayuda">Este demo se mide frase por frase en <a href="#sesion-voz">Sesión de voz</a>: '
            "graba, revisa lo que entendió el sistema y guarda. Cada frase guardada entra sola al informe.</p>"
        )
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
      <p class="demo-explicacion-criterio"><strong>Pregunta que responde:</strong> {e(meta["pregunta"])}</p>
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
      <section class="panel fca-card grabacion-pantalla" id="grabacion-pantalla" aria-labelledby="video-entrega-titulo">
        <h2 id="video-entrega-titulo">Video para la entrega (2 a 3 minutos)</h2>
        <p>Graba lo que pide la convocatoria: esta pantalla, otras ventanas, teléfonos si los muestras a cámara, o la pantalla completa con QuickTime u OBS. Aquí el navegador guarda un <code>.webm</code> en este equipo.</p>
        <ol class="pasos-medicion">
          <li>Pulsa <strong>Empezar a grabar</strong>. Elige «Pestaña», «Ventana» o «Pantalla completa» y, si aparece, activa el audio.</li>
          <li>Haz la demostración (2 a 3 minutos, sin editar de más).</li>
          <li>Pulsa <strong>Detener y guardar</strong>. Descarga el archivo y súbelo como no listado.</li>
          <li>Pega el enlace en <code>entregables/enlaces.json</code> en el número de este demo.</li>
        </ol>
        <div class="grabacion-pantalla-acciones">
          <button type="button" id="btn-video-iniciar" class="fca-btn">Empezar a grabar</button>
          <button type="button" id="btn-video-detener" class="fca-btn fca-btn--secondary" disabled>Detener y guardar</button>
        </div>
        <p id="video-entrega-estado" class="grabacion-pantalla-estado" role="status">Sin grabación en curso.</p>
        <ul id="video-entrega-lista" class="video-entrega-lista"></ul>
        <p class="body-sm">La corrida automática (al pulsar <strong>Correr experimento</strong>) solo captura esta pestaña a baja calidad; este botón es el que conviene para entregar.</p>
      </section>
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
            <a class="enlace-json" id="hist-link-imprimir" href="#" target="_blank" rel="noopener">Ver la nota técnica</a>
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
    </section>
    <section class="panel fca-card" aria-labelledby="medicion2-titulo">
      <h2 id="medicion2-titulo">Lo que se mide en esta sesión</h2>
      <p>El criterio tiene tres partes y las tres quedan medidas: <strong>3 o más usuarios a la vez</strong>, <strong>respuesta de voz en menos de 10 s en promedio</strong> y <strong>sin internet</strong>. En cada consulta el servidor comprueba si el equipo alcanza internet y lo guarda.</p>
      <p id="red-estado" class="red-estado" role="status" data-red="desconocida">Comprobando la salida a internet…</p>
      <ol class="pasos-medicion">
        <li>Desconecta el router de internet frente a la cámara y espera a que arriba diga «sin salida a internet».</li>
        <li>Cada persona abre el enlace en su teléfono, escribe su nombre y hace 10 consultas por voz, todos al mismo tiempo.</li>
        <li>Anota abajo la lectura del medidor de consumo, si lo tienes.</li>
        <li>Pulsa <strong>Correr experimento</strong>: el informe se calcula con las consultas por voz de la sesión.</li>
      </ol>
      <form id="form-consumo" class="consumo-form">
        <fieldset>
          <legend>Consumo eléctrico (opcional, lectura del medidor)</legend>
          <label for="consumo-reposo">En reposo (W)
            <input id="consumo-reposo" name="reposo_w" type="number" inputmode="decimal" min="0" max="5000" step="0.1" autocomplete="off">
          </label>
          <label for="consumo-carga">Durante la carga (W)
            <input id="consumo-carga" name="carga_w" type="number" inputmode="decimal" min="0" max="5000" step="0.1" autocomplete="off">
          </label>
          <label for="consumo-instrumento">Medidor usado
            <input id="consumo-instrumento" name="instrumento" type="text" autocomplete="off" maxlength="120" placeholder="Marca y modelo del medidor de enchufe">
          </label>
          <button type="submit" class="fca-btn fca-btn--secondary">Guardar consumo</button>
        </fieldset>
        <p id="consumo-estado" class="aviso" role="status" hidden></p>
      </form>
    </section>"""
    if demo_id == 4:
        extra = _bloque_corpus_demo4()
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


def _bloque_corpus_demo4() -> str:
    return """<section class="panel fca-card" aria-labelledby="corpus-demo4-titulo">
      <h2 id="corpus-demo4-titulo">Armar el corpus (WER)</h2>
      <p>El demo 4 necesita pares <strong>audio + transcripción de referencia</strong> por variedad. Tienes dos caminos:</p>
      <ul>
        <li><strong>Español costeño:</strong> las mediciones del <a href="/demo/1">demo 1</a> (variedad costeño) cuentan solas; aquí puedes sumar frases extra.</li>
        <li><strong>Palenquero:</strong> en el <a href="/demo/1">demo 1</a> elige variedad <em>palenquero</em> y guarda cada medición, <strong>o</strong> sube el audio y la referencia en este formulario (aval lingüístico según protocolo).</li>
      </ul>
      <p id="corpus-resumen" class="corpus-resumen" role="status">Cargando estado del corpus…</p>
      <form id="form-corpus-demo4" class="corpus-form">
        <label for="corpus-variedad">Variedad
          <select id="corpus-variedad" name="variedad">
            <option value="palenquero" selected>Palenquero</option>
            <option value="costeno">Costeño (adicional al demo 1)</option>
          </select>
        </label>
        <label for="corpus-id">Id de la frase (ej. P01, 001)
          <input id="corpus-id" name="id" type="text" autocomplete="off" spellcheck="false" required placeholder="P01">
        </label>
        <label for="corpus-ref">Transcripción de referencia (lo que dijo el hablante)
          <textarea id="corpus-ref" name="referencia" rows="3" required></textarea>
        </label>
        <label for="corpus-audio">Audio
          <input id="corpus-audio" name="audio" type="file" accept="audio/*" capture required>
        </label>
        <button type="submit" class="fca-btn">Guardar en corpus</button>
        <p id="corpus-estado" class="aviso" role="status" hidden></p>
      </form>
      <details class="corpus-listado">
        <summary>Ver archivos en carpeta</summary>
        <div id="corpus-tablas" class="corpus-tablas"></div>
      </details>
    </section>"""


def _bloque_voz() -> str:
    frases_json = json.dumps(
        {"costeno": FRASES, "palenquero": FRASES_PALENQUERO}, ensure_ascii=False
    ).replace("</", "<\\/")
    return f"""<section class="panel fca-card sesion-voz" id="sesion-voz" aria-labelledby="voz-titulo" data-paso="quien">
      <h2 id="voz-titulo">Sesión de voz</h2>
      <ol class="sesion-pasos" aria-label="Pasos de cada frase">
        <li data-paso="quien">1. Quién habla</li>
        <li data-paso="grabar">2. Grabar la frase</li>
        <li data-paso="revisar">3. Revisar y guardar</li>
      </ol>

      <form id="voz-quien" class="voz-quien" data-panel="quien">
        <p>Cada persona dice las {len(FRASES)} frases de su variedad con su habla natural. El audio se queda en este equipo y no se publica.</p>
        <label for="persona">Nombre de quien habla
          <input id="persona" name="persona" type="text" autocomplete="name" required>
        </label>
        <fieldset class="voz-variedad">
          <legend>Variedad</legend>
          <label><input type="radio" name="variedad" value="costeno" checked> Español costeño (guion del protocolo)</label>
          <label><input type="radio" name="variedad" value="palenquero"> Palenquero ({len(FRASES_PALENQUERO)} frases publicadas, con su fuente)</label>
        </fieldset>
        <label class="voz-consentimiento">
          <input id="consentimiento" name="consentimiento" type="checkbox" required>
          Esta persona firmó el consentimiento de donación de voz
        </label>
        <button type="submit" class="fca-btn">Empezar</button>
        <p class="voz-error" role="alert" hidden></p>
      </form>

      <section class="voz-panel" data-panel="grabar" aria-labelledby="voz-frase-titulo" hidden>
        <header class="voz-cabecera">
          <p class="voz-quien-resumen"><strong id="voz-persona-nombre"></strong> · <span id="voz-variedad-nombre"></span>
            · <button type="button" class="enlace-boton" id="voz-cambiar">Cambiar</button></p>
          <p class="voz-progreso" id="voz-progreso" role="status"></p>
        </header>
        <h3 id="voz-frase-titulo" class="voz-frase-numero"></h3>
        <figure class="voz-frase-figura">
          <blockquote class="voz-frase" id="voz-frase"></blockquote>
          <figcaption class="voz-frase-fuente body-sm" id="voz-frase-fuente" hidden></figcaption>
        </figure>
        <details class="voz-palenquero" hidden>
          <summary>Usar otra frase acordada con el hablante</summary>
          <label for="guion-palenquero">Frase en palenquero (será la transcripción correcta)
            <textarea id="guion-palenquero" rows="2" placeholder="Texto acordado con la Fundación Chano y Chalole o el hablante"></textarea>
          </label>
        </details>
        <div class="voz-microfono">
          <button type="button" class="boton-mic" id="boton-mic" aria-pressed="false" aria-describedby="voz-mic-ayuda">
            <span class="boton-mic-icono" aria-hidden="true"></span>
            <span class="boton-mic-texto">Grabar</span>
          </button>
          <p class="voz-mic-estado" aria-live="polite">
            <span class="voz-cronometro" id="voz-cronometro">0:00</span>
            <meter id="voz-nivel" min="0" max="1" low="0.15" high="0.85" optimum="0.5" value="0" aria-label="Nivel del micrófono"></meter>
          </p>
          <p id="voz-mic-ayuda" class="body-sm">Pulsa Grabar y lee la frase en voz alta. Se detiene sola cuando terminas; si coincide con la frase, se guarda sola. También puedes pulsar Terminar o la barra espaciadora.</p>
        </div>
        <section class="voz-procesando" id="escenario-voz" aria-label="Procesando la frase" hidden>
          <ol class="flujo-voz">
            <li data-paso="grabar">Escuchar</li>
            <li data-paso="transcribir">Transcribir</li>
            <li data-paso="responder">Responder en voz</li>
          </ol>
          <p class="escenario-pie" aria-live="polite"></p>
        </section>
        <p class="voz-error" role="alert" hidden></p>
        <details class="voz-guion-completo">
          <summary>Ver todas las frases</summary>
          <ol id="voz-lista-frases" class="voz-lista-frases"></ol>
        </details>
      </section>

      <section class="voz-panel" data-panel="revisar" aria-labelledby="voz-revisar-titulo" hidden>
        <h3 id="voz-revisar-titulo">Lo que entendió no coincide con la frase</h3>
        <p class="body-sm">Escucha lo que entendió y decide si es un error del sistema. Una tilde, una «s» que se come el costeño o una palabra que la persona leyó distinto pueden no serlo.</p>
        <dl class="voz-comparacion">
          <dt>Lo que entendió el sistema <span class="body-sm">(te lo lee en voz alta)</span></dt>
          <dd><p id="voz-sistema" class="voz-sistema"></p>
            <audio id="audio-eco" controls preload="auto"></audio></dd>
          <dt>Respuesta del asistente</dt>
          <dd><details class="voz-respuesta">
            <summary>Escuchar lo que respondió</summary>
            <p id="voz-respuesta"></p>
            <audio id="audio-respuesta" controls preload="none"></audio>
          </details></dd>
          <dt>Tiempo</dt>
          <dd id="voz-tiempos"></dd>
        </dl>
        <label for="correcta">Lo que de verdad se dijo <span class="body-sm">(viene del guion; corrígelo si la persona dijo otra cosa)</span>
          <textarea id="correcta" rows="2"></textarea>
        </label>
        <p id="voz-sugerencia" class="voz-sugerencia" role="status"></p>
        <fieldset class="voz-veredicto">
          <legend>¿Cómo quedó la transcripción?</legend>
          <button type="button" class="fca-btn" data-correcta="no">Mal transcrita · Guardar</button>
          <button type="button" class="fca-btn fca-btn--secondary" data-correcta="si">Bien transcrita · Guardar</button>
        </fieldset>
        <p><button type="button" class="enlace-boton" id="voz-repetir">Descartar y grabar de nuevo</button></p>
        <p class="voz-error" role="alert" hidden></p>
      </section>

      <p class="voz-guardado" id="voz-guardado" role="status" hidden></p>
    </section>
    <script type="application/json" id="frases-demo1">{frases_json}</script>
    <script src="/static/demo1-voz.js"></script>"""


def _script_voz_si(demo_id: int) -> str:
    if demo_id == 1:
        return ""
    return ""


def _en_linea(texto: str) -> str:
    """Negrita, código y enlaces de una línea de Markdown, ya escapada."""
    salida = e(texto)
    salida = re.sub(r"`([^`]+)`", r"<code>\1</code>", salida)
    salida = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", salida)
    return re.sub(r"(?<![\"'>=])(https?://[^\s<]+[^\s<.,;)])", r'<a href="\1">\1</a>', salida)


def _markdown_simple(texto: str) -> str:
    partes: list[str] = []
    for bloque in re.split(r"\n{2,}", texto):
        bloque = bloque.strip()
        if not bloque:
            continue
        if bloque.startswith("```"):
            codigo = "\n".join(linea for linea in bloque.splitlines() if not linea.startswith("```"))
            partes.append(f"<pre><code>{e(codigo)}</code></pre>")
            continue
        if bloque.startswith("# "):
            # El título de la página ya es el h1; el del documento baja un nivel.
            partes.append(f"<h2>{_en_linea(bloque[2:])}</h2>")
            continue
        if bloque.startswith("## "):
            partes.append(f"<h2>{_en_linea(bloque[3:])}</h2>")
            continue
        if bloque.startswith("### "):
            partes.append(f"<h3>{_en_linea(bloque[4:])}</h3>")
            continue
        if bloque.startswith("|"):
            filas = [
                [celda.strip() for celda in fila.split("|")[1:-1]]
                for fila in bloque.splitlines()
                if fila.strip().startswith("|") and not set(fila.replace("|", "").strip()) <= {"-", " ", ":"}
            ]
            if filas:
                cabecera = "".join(f'<th scope="col">{_en_linea(celda)}</th>' for celda in filas[0])
                cuerpo = "".join(
                    "<tr>" + "".join(f"<td>{_en_linea(celda)}</td>" for celda in fila) + "</tr>" for fila in filas[1:]
                )
                partes.append(
                    f'<table class="nota-tabla"><thead><tr>{cabecera}</tr></thead><tbody>{cuerpo}</tbody></table>'
                )
            continue
        if bloque.startswith("- "):
            items = "".join(f"<li>{_en_linea(linea[2:])}</li>" for linea in bloque.splitlines() if linea.startswith("- "))
            partes.append(f"<ul>{items}</ul>")
            continue
        if re.match(r"\d+\. ", bloque):
            items = "".join(
                f"<li>{_en_linea(re.sub(r'^\d+\. ', '', linea))}</li>"
                for linea in bloque.splitlines()
                if re.match(r"\d+\. ", linea)
            )
            partes.append(f"<ol>{items}</ol>")
            continue
        partes.append(f"<p>{_en_linea(' '.join(bloque.splitlines()))}</p>")
    return "\n".join(partes)


def _estado_de_la_entrega() -> str:
    """Tabla viva: cómo va cada nota frente a lo que pide la especificación."""
    from interfaz.entregar import revisar

    revision = revisar()
    filas = []
    for fila in revision["notas"]:
        n = fila["demo"]
        if fila["video"]:
            video = f'<a href="{e(fila["video"])}" rel="noopener">Ver video</a>'
        elif fila["video_opcional"]:
            video = "Opcional"
        else:
            video = "Falta el enlace"
        filas.append(
            f"""<tr>
          <th scope="row"><a href="/demo/{n}">Demo {n}. {e(fila["titulo"])}</a></th>
          <td><span class="estado-badge {e(fila["estado"])}">{e(fila["etiqueta"])}</span></td>
          <td class="num">{fila["paginas"]}</td>
          <td>{video}</td>
          <td><a href="/demo/{n}/informe/imprimir">Ver</a> · <a href="/api/demos/{n}/informe.pdf">PDF</a></td>
        </tr>"""
        )
    resultados = "".join(
        f"<dt>Demo {fila['demo']}. {e(fila['titulo'])}</dt><dd>{e(fila['resumen'])}</dd>" for fila in revision["notas"]
    )
    if revision["pendientes"]:
        items = "".join(f"<li>{e(texto)}</li>" for texto in revision["pendientes"])
        falta = f'<h3 id="falta-titulo">Falta antes de radicar</h3><ul aria-labelledby="falta-titulo">{items}</ul>'
    else:
        falta = "<p><strong>Nada pendiente:</strong> las cinco notas cumplen el criterio y tienen su video.</p>"
    return f"""<section class="panel fca-card entrega" aria-labelledby="entrega-titulo">
      <h2 id="entrega-titulo">Cómo va la entrega</h2>
      <p>Se calcula ahora con los informes medidos. Para escribir los cinco PDF y el ZIP: <code>.venv/bin/python -m interfaz.entregar</code>.</p>
      <div class="tabla-desplazable">
        <table class="datos entrega-tabla">
          <caption>Estado de cada nota técnica</caption>
          <thead><tr>
            <th scope="col">Demo</th><th scope="col">Estado</th>
            <th scope="col">Páginas</th><th scope="col">Video</th><th scope="col">Nota</th>
          </tr></thead>
          <tbody>{"".join(filas)}</tbody>
        </table>
      </div>
      <h3>Resultado de cada demo</h3>
      <dl class="entrega-resultados">{resultados}</dl>
      {falta}
    </section>"""


def nota_tecnica() -> str:
    from pathlib import Path

    archivo = Path(__file__).resolve().parents[1] / "notas" / "NOTA_TECNICA.md"
    texto = archivo.read_text(encoding="utf-8") if archivo.is_file() else "Falta notas/NOTA_TECNICA.md."
    # El primer título del archivo repite el de la página.
    texto = re.sub(r"\A# [^\n]*\n+", "", texto)
    cuerpo = _cabecera(
        "Entrega del laboratorio",
        "Evidencia TRL 3 · Nodo IA Caribe. Estado de las cinco notas técnicas, sus videos y lo que falta para radicar.",
        breadcrumb="Entrega",
    )
    cuerpo += _estado_de_la_entrega()
    cuerpo += f'<article class="nota-tecnica panel fca-card">{_markdown_simple(texto)}</article>'
    cuerpo += """<p class="body-sm"><a href="/">← Volver a la portada</a></p>"""
    return cuerpo + _pie()


def medicion_base() -> str:
    """Medición base del repositorio: notas, datos e historial de referencia."""
    from pathlib import Path

    from ejemplo.datos import AUTORIZACION_PALENQUERO

    indice = Path(__file__).resolve().parents[1] / "ejemplo" / "indice.json"
    cuerpo = _cabecera(
        "Medición base",
        "Referencia del equipo con la muestra completa del protocolo (notas, datos e historial en ejemplo/resultados/).",
        breadcrumb="Medición base",
    )
    if not indice.is_file():
        cuerpo += """<section class="panel fca-card entrega" aria-labelledby="medicion-base-titulo">
      <h2 id="medicion-base-titulo">Todavía no se ha generado</h2>
      <p>Para escribir la medición base: <code>.venv/bin/python -m ejemplo.generar</code>.</p>
    </section>"""
        return cuerpo + _pie()
    notas = json.loads(indice.read_text(encoding="utf-8"))
    filas = []
    for nota in notas:
        archivo = e(nota["archivo"])
        origen = "Datos sintéticos" if nota["sintetico"] else "Semillas de referencia"
        filas.append(
            f"""<tr>
          <th scope="row">Demo {nota["demo"]}. {e(nota["titulo"])}</th>
          <td><span class="estado-badge {e(nota["estado"])}">{e(nota["etiqueta"])}</span></td>
          <td>{origen}</td>
          <td class="num">{nota["paginas"]}</td>
          <td class="ejemplo-nota-enlaces">
            <a href="/medicion-base/notas/{archivo}.html">Ver en pantalla</a>
            <span class="ejemplo-nota-sep" aria-hidden="true">·</span>
            <a href="/medicion-base/notas/{archivo}.pdf">Ver PDF</a>
            <span class="ejemplo-nota-sep" aria-hidden="true">·</span>
            <a href="/medicion-base/notas/{archivo}.pdf?descargar=1">Descargar PDF</a>
          </td>
        </tr>"""
        )
    respuestas = "".join(
        f"<dt>Demo {nota['demo']}. {e(nota['pregunta'])}</dt><dd>{e(nota['respuesta'])}</dd>" for nota in notas
    )
    cuerpo += f"""<section class="panel fca-card entrega" aria-labelledby="medicion-base-titulo">
      <h2 id="medicion-base-titulo">Las cinco notas con la muestra completa</h2>
      <p class="body-sm">Referencia pública del protocolo completo. La evidencia de radicación está en <a href="/nota-tecnica">Entrega</a> y en tu <code>resultados/</code> local.</p>
      <div class="ejemplo-descargas">
        <a class="fca-btn fca-btn--secondary" href="/medicion-base/notas.zip">Descargar los cinco PDF (ZIP)</a>
        <p class="ejemplo-descargas-ayuda body-sm">«Ver en pantalla» abre la nota en HTML. «Ver PDF» la muestra en el navegador; «Descargar PDF» guarda el archivo.</p>
      </div>
      <div class="tabla-desplazable">
        <table class="datos entrega-tabla">
          <caption>Notas de la medición base</caption>
          <thead><tr>
            <th scope="col">Demo</th><th scope="col">Estado en la base</th>
            <th scope="col">Origen de cifras</th><th scope="col">Páginas</th><th scope="col">Nota</th>
          </tr></thead>
          <tbody>{"".join(filas)}</tbody>
        </table>
      </div>
      <h3>Qué responde cada demo en la base</h3>
      <dl class="entrega-resultados">{respuestas}</dl>
      <p>Se regenera con <code>.venv/bin/python -m ejemplo.generar</code> → <code>ejemplo/resultados/</code> e <code>ejemplo/notas/</code>.</p>
    </section>
    <details class="medicion-base-complementos body-sm">
      <summary>Datos sensibles, palenquero y alcance de esta referencia</summary>
      <p>Las grabaciones reales solo existen en <code>resultados/</code> en tu equipo; esta página no las sustituye.
      La radicación oficial está en <a href="/nota-tecnica">Entrega</a>.</p>
      <p>{e(AUTORIZACION_PALENQUERO)}</p>
    </details>
    <p class="body-sm"><a href="/">← Volver a la portada</a> · <a href="/demo/1">Ir al demo 1</a></p>"""
    return cuerpo + _pie()


def ejemplo() -> str:
    """Compatibilidad con la ruta /ejemplo."""
    return medicion_base()


def pagina_voz(modo: str) -> str:
    from voz.pagina import PAGINA

    return PAGINA.replace("FRASES_JSON", json.dumps(FRASES, ensure_ascii=False))


def pagina_calificar() -> str:
    path = __import__("pathlib").Path(__file__).resolve().parents[1] / "demo3_comparacion" / "calificar.html"
    return path.read_text(encoding="utf-8").replace(
        'href="/static/app.css"',
        'href="/static/app.css"',
    )
