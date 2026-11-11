const ETIQUETAS = {
  fecha: "Fecha de la corrida",
  fecha_corrida: "Fecha de la corrida (40+40)",
  fecha_calificacion: "Fecha de calificación ciega",
  costo_local_nota: "Costo local",
  titulo: "Título",
  pruebas_pasadas: "Pruebas pasadas",
  pruebas_total: "Pruebas totales",
  criterio: "Criterio",
  criterio_cumplido: "Criterio cumplido",
  internet: "Internet durante la prueba",
  auditoria_integra: "Auditoría íntegra",
  filas: "Mediciones",
  errores_marcados: "Errores marcados",
  aciertos_marcados: "Aciertos marcados",
  consultas: "Consultas",
  consultas_voz: "Consultas por voz",
  tiempo_promedio_s: "Tiempo promedio (s)",
  parcial: "Solo carga parcial",
  tareas_local: "Tareas con respuesta local",
  tiempo_promedio_caliente_s: "Promedio en caliente (s)",
  tiempo_maximo_caliente_s: "Máximo en caliente (s)",
  tiempo_promedio_todas_s: "Promedio todas las tareas (s)",
  modelo_local: "Modelo local",
  comparacion_completa: "Paquete ciego listo",
  pendiente: "Pendiente",
  pendiente_calificacion: "Falta calificación",
  costo_local_usd: "Costo local (USD)",
  datos: "Origen de datos",
  criterio_flujo: "Flujo registrado",
  criterio_video_error_real: "Error real para video",
};

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatoValor(clave, valor) {
  if (typeof valor === "boolean") return valor ? "Sí" : "No";
  if (valor === null || valor === undefined) return "—";
  if (clave === "fecha" && typeof valor === "string") {
    try {
      const d = new Date(valor);
      if (!Number.isNaN(d.getTime())) {
        return d.toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" });
      }
    } catch {
      /* seguir */
    }
  }
  return String(valor);
}

function estadoInforme(demoId, data) {
  if (!data) {
    return { clase: "pendiente", texto: "Sin medición aún" };
  }
  if (data.criterio_cumplido === true) {
    return { clase: "ok", texto: "Criterio cumplido" };
  }
  if (demoId === 1 && data.criterio_cumplido) {
    return { clase: "ok", texto: "Flujo completo y error real registrado" };
  }
  if (demoId === 3) {
    if (data.criterio_metodo_armado && !data.criterio_calificacion_completa) {
      const cal = data.paquete_ciego?.calificacion || {};
      if (cal.estado === "calculado") {
        return { clase: "ok", texto: "Método y calificación cerrados" };
      }
      if (cal.estado === "parcial") {
        return { clase: "parcial", texto: cal.descripcion || "Falta segunda calificación" };
      }
      if (data.comparacion_completa) {
        return {
          clase: "ok",
          texto: "40/40 · paquete ciego listo (siguiente: calificación ciega)",
        };
      }
    }
    if (data.ultima_corrida_error) {
      return { clase: "falla", texto: `Última corrida: ${data.ultima_corrida_error}` };
    }
    if (data.comparacion_completa) {
      return {
        clase: "ok",
        texto: "40/40 · paquete ciego listo (siguiente: calificación ciega)",
      };
    }
    const refs = data.tareas_referencia ?? data.con_las_dos_respuestas ?? 0;
    if (data.tareas_local >= 40 && refs < 40) {
      return { clase: "parcial", texto: `Local listo · referencia ${refs}/40` };
    }
    if (data.criterio_cumplido === false) {
      return { clase: "falla", texto: "Criterio no cumplido" };
    }
    if (data.tareas_local > 0) {
      return { clase: "parcial", texto: `Local ${data.tareas_local}/40` };
    }
    return { clase: "pendiente", texto: "Sin respuestas locales aún" };
  }
  if (data.parcial || data.pendiente || data.pendiente_calificacion) {
    return { clase: "parcial", texto: "Evidencia parcial" };
  }
  if (demoId === 1 && data.filas > 0) {
    return { clase: data.criterio_video_error_real ? "ok" : "parcial", texto: data.criterio_video_error_real ? "Listo para video" : "Falta error real" };
  }
  if (demoId === 4 && (data.variedades || []).length) {
    return { clase: "ok", texto: "WER calculado" };
  }
  if (data.filas?.length || data.consultas) {
    return { clase: "parcial", texto: "Medición en curso" };
  }
  return { clase: "pendiente", texto: "Revisar protocolo" };
}

function kpisDeInforme(demoId, data) {
  if (!data) return [];
  const items = [];
  if (demoId === 5) {
    if (data.pruebas_pasadas != null) {
      items.push({ etiqueta: "Pruebas", valor: `${data.pruebas_pasadas}/${data.pruebas_total}` });
    }
    if (data.auditoria_integra != null) {
      items.push({ etiqueta: "Auditoría", valor: data.auditoria_integra ? "Íntegra" : "Revisar" });
    }
    items.push({ etiqueta: "Red", valor: data.internet === false ? "Sin internet" : data.internet === true ? "Con internet" : "—" });
  } else if (demoId === 1) {
    items.push({ etiqueta: "Filas", valor: data.filas ?? 0 });
    items.push({ etiqueta: "WER corpus", valor: data.wer_corpus?.wer_porcentaje != null ? `${data.wer_corpus.wer_porcentaje} %` : "—" });
    items.push({ etiqueta: "Errores", valor: data.errores_marcados ?? 0 });
  } else if (demoId === 2) {
    items.push({ etiqueta: "Consultas", valor: data.consultas_voz ?? data.consultas ?? 0 });
    items.push({ etiqueta: "Promedio", valor: data.tiempo_promedio_s != null ? `${data.tiempo_promedio_s} s` : "—" });
    items.push({ etiqueta: "Modo", valor: data.parcial ? "Texto (parcial)" : "Voz" });
  } else if (demoId === 3) {
    const c = data.comparacion || {};
    items.push({ etiqueta: "Local / ref.", valor: `${c.respuestas_local ?? data.tareas_local ?? 0}/${c.respuestas_referencia ?? data.tareas_referencia ?? 0}` });
    items.push({ etiqueta: "Caliente", valor: data.tiempo_promedio_caliente_s != null ? `${data.tiempo_promedio_caliente_s} s` : "—" });
    const cal = data.paquete_ciego?.calificacion;
    items.push({
      etiqueta: "Ciego",
      valor: data.comparacion_completa ? (cal?.estado === "calculado" ? "Calificado" : cal?.estado === "parcial" ? "1/2 cal." : "Listo") : "Pendiente",
    });
  } else if (demoId === 4) {
    for (const v of data.variedades || []) {
      items.push({ etiqueta: v.variedad, valor: `${v.wer_porcentaje} % WER` });
    }
    if (!items.length && data.pendiente) {
      items.push({ etiqueta: "Estado", valor: "Faltan pares" });
    }
  }
  return items.slice(0, 4);
}

function filasDetalleDemo1(data) {
  if (!data.tabla?.length || data.wer_corpus == null && !data.modelos) return "";
  const m = data.modelos || {};
  const wc = data.wer_corpus || {};
  const tp = data.tiempos_promedio || {};
  const filas = data.tabla
    .map(
      (f) =>
        `<tr>
          <td>${escapeHtml(f.persona || "")}</td>
          <td class="col-texto">${escapeHtml(f.transcripcion_sistema || "")}</td>
          <td>${f.wer_porcentaje != null ? `${f.wer_porcentaje} %` : "—"}</td>
          <td class="col-texto">${escapeHtml(f.respuesta_asistente || "—")}</td>
          <td>${f.asr_s != null ? `${f.asr_s} / ${f.llm_s} / ${f.tts_s}` : "—"}</td>
          <td>${f.audio_entrada_url ? `<a href="${escapeHtml(f.audio_entrada_url)}">Escuchar</a>` : "—"}</td>
        </tr>`
    )
    .join("");
  const porPersona = (data.wer_por_persona || [])
    .map((p) => `<li>${escapeHtml(p.persona)}: ${p.wer_porcentaje} % WER (${p.frases} frases)</li>`)
    .join("");
  const video =
    data.video_corrida || data.corrida_id
      ? `<p><a class="fca-btn fca-btn--secondary" href="${escapeHtml(data.video_corrida || `/api/demos/1/historial/${data.corrida_id}.webm`)}">Video de la corrida</a></p>`
      : "<p class=\"body-sm\">Sube el video de la sesión desde el historial del demo (botón de grabación en pantalla).</p>";
  return `<details class="informe-details" open>
    <summary>Modelos, WER y flujo punta a punta</summary>
    ${data.resumen_ejecutivo ? `<p class="informe-resumen">${escapeHtml(data.resumen_ejecutivo)}</p>` : ""}
    <dl class="informe-dl compacto">
      <dt>Whisper</dt><dd>${escapeHtml(m.whisper || "—")}</dd>
      <dt>Ollama</dt><dd>${escapeHtml(m.ollama || "—")}</dd>
      <dt>Piper (voz asistente)</dt><dd>${escapeHtml(m.piper_asistente || "—")}</dd>
      <dt>WER corpus</dt><dd>${wc.wer_porcentaje != null ? `${wc.wer_porcentaje} %` : "—"}</dd>
      ${porPersona ? `<dt>WER por hablante</dt><dd><ul class="lista-inline">${porPersona}</ul></dd>` : ""}
      ${tp.asr_promedio_s != null ? `<dt>Tiempos prom.</dt><dd>ASR ${tp.asr_promedio_s} s · LLM ${tp.llm_promedio_s} s · TTS ${tp.tts_promedio_s} s · total ${tp.total_promedio_s} s</dd>` : ""}
    </dl>
    ${data.nota_referencias ? `<p class="informe-nota">${escapeHtml(data.nota_referencias)}</p>` : ""}
    ${
      (data.observaciones_llm || []).length
        ? `<section><h3 class="informe-subtitulo">Alucinaciones del asistente</h3><ul>${(data.observaciones_llm || [])
            .map((h) => `<li>${escapeHtml(h.observacion || "")}</li>`)
            .join("")}</ul><p class="informe-nota">${escapeHtml(data.implicacion_alucinaciones || "")}</p></section>`
        : ""
    }
    ${video}
    <table class="datos informe-tabla">
      <thead><tr><th>Persona</th><th>ASR</th><th>WER</th><th>Respuesta</th><th>ASR/LLM/TTS (s)</th><th>Audio</th></tr></thead>
      <tbody>${filas}</tbody>
    </table>
  </details>`;
}

function filasDetalleDemo3(data) {
  if (!data.comparacion && !data.paquete_ciego) return "";
  const c = data.comparacion || {};
  const rl = data.rendimiento?.local || {};
  const rr = data.rendimiento?.referencia || {};
  const p = data.paquete_ciego || {};
  const cal = p.calificacion || {};
  const chk = (data.protocolo_checklist || [])
    .map(
      (f) =>
        `<tr><td>${escapeHtml(f.item || "")}</td><td>${escapeHtml(String(f.medido ?? ""))}</td><td>${f.cumple ? "Sí" : "No"}</td></tr>`
    )
    .join("");
  return `<details class="informe-details" open>
    <summary>Comparación y paquete ciego</summary>
    ${data.resumen_ejecutivo ? `<p class="informe-resumen">${escapeHtml(data.resumen_ejecutivo)}</p>` : ""}
    <table class="datos informe-tabla">
      <thead><tr><th></th><th>Local</th><th>Referencia</th></tr></thead>
      <tbody>
        <tr><th scope="row">Modelo</th><td>${escapeHtml(c.modelo_local || "—")}</td><td>${escapeHtml((c.proveedor_referencia || "") + " · " + (c.modelo_referencia || "—"))}</td></tr>
        <tr><th scope="row">Respuestas</th><td>${c.respuestas_local ?? "—"} / ${c.tareas_total ?? 40}</td><td>${c.respuestas_referencia ?? "—"} / ${c.tareas_total ?? 40}</td></tr>
        <tr><th scope="row">Promedio caliente (s)</th><td>${rl.promedio_caliente_s ?? "—"}</td><td>${rr.promedio_caliente_s ?? "—"}</td></tr>
        <tr><th scope="row">Promedio todas (s)</th><td>${rl.promedio_todas_s ?? "—"}</td><td>${rr.promedio_todas_s ?? "—"}</td></tr>
      </tbody>
    </table>
    <h3 class="informe-subtitulo">Paquete ciego</h3>
    <dl class="informe-dl compacto">
      <dt>Estado</dt><dd>${p.listo ? "Generado" : "Pendiente"}</dd>
      <dt>Hash</dt><dd><code>${escapeHtml(p.hash || "—")}</code></dd>
      <dt>Archivo</dt><dd><code>${escapeHtml(p.archivo || "—")}</code></dd>
      <dt>Evaluadores</dt><dd>${escapeHtml((cal.calificadores || []).join(", ") || "—")}</dd>
      <dt>Calificación</dt><dd>${escapeHtml(cal.descripcion || "Pendiente")}</dd>
      ${cal.kappa_cohen_promedio != null ? `<dt>Kappa Cohen</dt><dd>${cal.kappa_cohen_promedio}</dd>` : ""}
      ${cal.calidad_promedio ? `<dt>Calidad media</dt><dd>Local ${cal.calidad_promedio.local ?? "—"} · Referencia ${cal.calidad_promedio.referencia ?? "—"}</dd>` : ""}
      <dt>Fecha corrida</dt><dd>${escapeHtml(formatoValor("fecha_corrida", data.fecha_corrida || data.fecha))}</dd>
      <dt>Fecha calificación</dt><dd>${escapeHtml(formatoValor("fecha_calificacion", data.fecha_calificacion))}</dd>
      ${data.costo_local_nota ? `<dt>Costo local</dt><dd>${escapeHtml(data.costo_local_nota)}</dd>` : ""}
    </dl>
    ${data.limitacion_calificadores ? `<p class="informe-nota">${escapeHtml(data.limitacion_calificadores)}</p>` : ""}
    ${chk ? `<table class="datos informe-tabla"><thead><tr><th>Paso</th><th>Medido</th><th>OK</th></tr></thead><tbody>${chk}</tbody></table>` : ""}
  </details>`;
}

function filasDetalle(data) {
  if (data.demo === 1 || (data.tabla?.length && data.modelos)) {
    return filasDetalleDemo1(data);
  }
  if (data.comparacion || data.paquete_ciego) {
    return filasDetalleDemo3(data);
  }
  if (data.tabla && data.tabla.length && !data.modelos) {
    const rows = data.tabla
      .map(
        (f) =>
          `<tr><td>${escapeHtml(f.persona || "")}</td><td>${escapeHtml(f.transcripcion_sistema || "")}</td><td>${escapeHtml(f.correcta || "")}</td></tr>`
      )
      .join("");
    return `<details class="informe-details" open><summary>Tabla de voz (${data.tabla.length})</summary>
      <table class="datos informe-tabla"><thead><tr><th>Persona</th><th>Transcripción</th><th>¿Correcta?</th></tr></thead><tbody>${rows}</tbody></table></details>`;
  }
  if (data.filas && Array.isArray(data.filas) && data.filas[0]?.prueba) {
    const rows = data.filas
      .map((f) => {
        const ok = String(f.obtenido || "").toLowerCase().includes("pasó");
        return `<tr class="${ok ? "fila-ok" : "fila-falla"}"><td>${escapeHtml(f.prueba || "")}</td><td>${escapeHtml(f.obtenido || "")}</td></tr>`;
      })
      .join("");
    return `<details class="informe-details" open><summary>Pruebas automatizadas (${data.filas.length})</summary>
      <table class="datos informe-tabla"><thead><tr><th>Prueba</th><th>Resultado</th></tr></thead><tbody>${rows}</tbody></table></details>`;
  }
  if (data.tabla && data.tabla.length) {
    const rows = data.tabla
      .map(
        (f) =>
          `<tr><td>${escapeHtml(f.persona || "")}</td><td>${escapeHtml(f.transcripcion_sistema || "")}</td><td>${escapeHtml(f.correcta || "")}</td></tr>`
      )
      .join("");
    return `<details class="informe-details" open><summary>Tabla de voz (${data.tabla.length} filas)</summary>
      <table class="datos informe-tabla"><thead><tr><th>Persona</th><th>Sistema</th><th>¿Correcta?</th></tr></thead><tbody>${rows}</tbody></table></details>`;
  }
  if (data.variedades && data.variedades.length) {
    const rows = data.variedades
      .map((v) => `<tr><td>${escapeHtml(v.variedad)}</td><td>${v.frases}</td><td>${v.wer_porcentaje} %</td></tr>`)
      .join("");
    return `<details class="informe-details" open><summary>WER por variedad</summary>
      <table class="datos informe-tabla"><thead><tr><th>Variedad</th><th>Frases</th><th>WER</th></tr></thead><tbody>${rows}</tbody></table></details>`;
  }
  if (typeof data.filas === "number") {
    return `<p class="informe-nota">${data.filas} filas registradas en el informe completo (JSON).</p>`;
  }
  return "";
}

function renderInforme(container, data, demoId) {
  demoId = demoId ?? (Number(document.body.dataset.demo) || 0);
  if (!data) {
    container.innerHTML = `<p class="pendiente">Todavía no hay informe. Sigue el protocolo o usa <strong>Correr de nuevo</strong>.</p>`;
    return;
  }
  const estado = estadoInforme(demoId, data);
  const kpis = kpisDeInforme(demoId, data);
  const kpiHtml = kpis.length
    ? `<ul class="kpi-row" aria-label="Indicadores principales">${kpis.map((k) => `<li><span class="kpi-valor">${escapeHtml(String(k.valor))}</span><span class="kpi-etiqueta">${escapeHtml(k.etiqueta)}</span></li>`).join("")}</ul>`
  : "";

  const omitidas = new Set([
    "comparacion",
    "rendimiento",
    "paquete_ciego",
    "protocolo_checklist",
    "resumen_ejecutivo",
    "criterio_protocolo",
    "criterio_metodo_armado",
    "criterio_calificacion_completa",
    "limitacion_calificadores",
    "costo_local_nota",
    "fecha_corrida",
    "fecha_calificacion",
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
    "tabla",
    "filas",
    "eventos",
    "variedades",
    "detalle",
    "equipo",
    "bloqueo",
    "demo",
    "titulo",
    "ultima_corrida_error",
  ]);
  const extraDemo3 =
    demoId === 3 && data.ultima_corrida_error
      ? `<p class="informe-alerta error-texto" role="alert"><strong>Última corrida comercial/local:</strong> ${escapeHtml(
          data.ultima_corrida_error
        )}</p>`
      : "";
  const metadatos = Object.entries(data)
    .filter(([clave, valor]) => !omitidas.has(clave) && valor !== null && typeof valor !== "object")
    .map(([clave, valor]) => {
      const etiqueta = ETIQUETAS[clave] || clave.replaceAll("_", " ");
      return `<dt>${escapeHtml(etiqueta)}</dt><dd>${escapeHtml(formatoValor(clave, valor))}</dd>`;
    })
    .join("");

  const equipo = data.equipo
    ? `<details class="informe-details"><summary>Equipo de medición</summary><dl class="informe-dl compacto">${Object.entries(data.equipo)
        .map(([k, v]) => `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(String(v))}</dd>`)
        .join("")}</dl></details>`
    : "";

  const calEstado = data.paquete_ciego?.calificacion?.estado;
  const ctaCiego =
    demoId === 3 &&
    (data.comparacion_completa || data.tareas_referencia >= 40) &&
    calEstado !== "calculado"
      ? `<p class="informe-cta-ciego"><a class="fca-btn" href="/calificar?paquete=actual">Calificar paquete ciego</a> <span class="body-sm">${
          calEstado === "parcial" ? "(falta segunda evaluación)" : "(paquete listo · falta calificación humana)"
        }</span></p>`
      : "";
  container.innerHTML = `<div class="informe-resumen estado-${estado.clase}">
    <span class="estado-badge ${estado.clase}">${escapeHtml(estado.texto)}</span>
    ${extraDemo3}
    ${ctaCiego}
    ${kpiHtml}
    <dl class="informe-dl">${metadatos}</dl>
    ${filasDetalle(data)}
    ${equipo}
  </div>`;
}

async function cargarInforme(demoId) {
  const resp = await fetch(`/api/demos/${demoId}/informe`);
  if (!resp.ok) return null;
  return resp.json();
}

function formatoFechaCorta(fecha) {
  try {
    return new Date(fecha).toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" });
  } catch {
    return String(fecha);
  }
}

function setEstadoCorrida(estado, texto) {
  const el = document.getElementById("estado-corrida");
  if (!el) return;
  el.dataset.estado = estado;
  const span = el.querySelector(".estado-texto");
  if (span) span.textContent = texto;
}

function bloquearHeroes(bloquear) {
  document.querySelectorAll(".hero-correr").forEach((btn) => {
    btn.disabled = bloquear;
    btn.classList.toggle("corriendo", bloquear);
  });
}

function activarTab(nombre) {
  document.querySelectorAll(".demo-tab").forEach((tab) => {
    const on = tab.dataset.tab === nombre;
    tab.classList.toggle("activa", on);
    tab.setAttribute("aria-selected", on ? "true" : "false");
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    const on = panel.id === `tab-${nombre}`;
    panel.classList.toggle("activa", on);
    panel.hidden = !on;
  });
  const demoId = Number(document.body.dataset.demo);
  if (nombre === "resultados" && demoId) {
    cargarHistorial(demoId);
    if (demoId === 3 && typeof initDemo3PaqueteCiego === "function") initDemo3PaqueteCiego();
  }
}

async function mostrarUltimoResultado(demoId) {
  const data = await cargarInforme(demoId);
  const panel = document.getElementById("resultado-rapido");
  const contenedor = document.getElementById("informe-rapido");
  if (!data || !panel || !contenedor) return;
  renderInforme(contenedor, data, demoId);
  panel.hidden = false;
}
window.setEstadoCorrida = setEstadoCorrida;
window.mostrarUltimoResultado = mostrarUltimoResultado;

async function seleccionarCorrida(demoId, corridaId, boton) {
  document.querySelectorAll(".historial-item").forEach((b) => b.classList.remove("seleccionado"));
  boton?.classList.add("seleccionado");
  const detalle = document.getElementById("historial-detalle");
  if (!detalle) return;
  const resp = await fetch(`/api/demos/${demoId}/historial/${encodeURIComponent(corridaId)}`);
  if (!resp.ok) return;
  const data = await resp.json();
  detalle.replaceChildren();
  const nav = document.createElement("nav");
  nav.className = "informe-exportar";
  nav.setAttribute("aria-label", "Exportar esta corrida");
  const q = encodeURIComponent(corridaId);
  const videoUrl = `/api/demos/${demoId}/historial/${q}.webm`;
  const nombreVideo = `Nodo-IA-Caribe_Demo-${demoId}_${corridaId}.webm`;
  const videoLink = boton?.dataset?.video === "1"
    ? `<a class="enlace-json enlace-video-corrida" href="${videoUrl}" download="${escapeHtml(nombreVideo)}">Descargar video</a>`
    : "";
  const enlaceCiego =
    demoId === 3 && (data.comparacion_completa || (data.tareas_referencia ?? 0) >= 40)
      ? `<a class="enlace-json enlace-calificar-ciego" href="/calificar?paquete=actual">Calificar paquete ciego</a>`
      : "";
  nav.innerHTML = `<a class="enlace-json" href="/demo/${demoId}/informe/imprimir?corrida=${q}" target="_blank" rel="noopener">Vista PDF</a>
    <a class="enlace-json" href="/api/demos/${demoId}/informe.pdf?corrida=${q}">Descargar PDF</a>
    ${videoLink}
    ${enlaceCiego}`;
  const cuerpo = document.createElement("div");
  detalle.appendChild(nav);
  detalle.appendChild(cuerpo);
  renderInforme(cuerpo, data, demoId);
}

async function cargarHistorial(demoId) {
  const lista = document.getElementById("historial-lista");
  const vacio = document.getElementById("historial-vacio");
  if (!lista) return;
  const resp = await fetch(`/api/demos/${demoId}/historial`);
  const payload = await resp.json();
  const corridas = payload.corridas || [];
  lista.replaceChildren();
  if (!corridas.length) {
    if (vacio) vacio.hidden = false;
    const detalle = document.getElementById("historial-detalle");
    if (detalle) {
      detalle.replaceChildren();
      detalle.innerHTML = "<p class=\"pendiente\">Elige una corrida de la lista para ver el detalle.</p>";
    }
    return;
  }
  if (vacio) vacio.hidden = true;
  corridas.forEach((corrida, indice) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `historial-item estado-${corrida.estado || "pendiente"}`;
    if (corrida.video) btn.dataset.video = "1";
    const marcaVideo = corrida.video
      ? '<span class="historial-video" aria-label="Tiene video">▶</span>'
      : "";
    btn.innerHTML = `${marcaVideo}<time datetime="${escapeHtml(corrida.fecha || "")}">${escapeHtml(
      formatoFechaCorta(corrida.fecha)
    )}</time><span class="historial-resumen">${escapeHtml(corrida.resumen || "")}</span>`;
    btn.addEventListener("click", () => seleccionarCorrida(demoId, corrida.id, btn));
    li.appendChild(btn);
    lista.appendChild(li);
    if (indice === 0) seleccionarCorrida(demoId, corrida.id, btn);
  });
}

function conectarEventos(demoId, lista) {
  const escenarioRoot = document.getElementById("escenario");
  const reproductor =
    escenarioRoot && window.ReproductorEscenario
      ? new window.ReproductorEscenario(demoId, escenarioRoot)
      : null;
  reproductor?.reset();

  const rapido = document.getElementById("resultado-rapido");
  if (rapido) rapido.hidden = true;

  const grabador = window.CorridaVideo ? new window.CorridaVideo(demoId) : null;

  function agregar(evento) {
    const li = document.createElement("li");
    if (evento.tipo === "error") li.className = "error";
    let texto = evento.mensaje || "";
    if (evento.datos?.detalle && !texto.includes(evento.datos.detalle)) {
      texto += ` — ${evento.datos.detalle}`;
    }
    li.textContent = texto;
    lista.prepend(li);
  }

  async function finalizarVideo(evento) {
    const corridaId = evento?.datos?.corrida_id;
    if (!grabador || !corridaId) return;
    const subio = await grabador.detenerYSubir(corridaId);
    if (subio) cargarHistorial(demoId);
  }

  return new Promise((resolve, reject) => {
    const fuente = new EventSource(`/api/demos/${demoId}/eventos`);
    let listo = false;

    const cerrar = () => {
      if (listo) return;
      listo = true;
      fuente.close();
    };

    fuente.onopen = () => {
      if (!listo) {
        grabador?.iniciar();
        resolve({ cerrar, fuente, grabador });
      }
    };

    fuente.onmessage = (mensaje) => {
      const evento = JSON.parse(mensaje.data);
      agregar(evento);
      reproductor?.onEvent(evento);
      grabador?.onEvento(evento);
      if (evento.tipo === "error") {
        const detalle = evento.datos?.detalle ? ` ${evento.datos.detalle}` : "";
        setEstadoCorrida("error", (evento.mensaje || "Error en la corrida") + detalle);
        if (lista?.closest("details")) lista.closest("details").open = true;
      }
      if (evento.tipo === "fin") {
        cerrar();
        bloquearHeroes(false);
        const ok = evento.datos?.ok !== false;
        const msgError = evento.datos?.mensaje_error || evento.mensaje;
        setEstadoCorrida(
          ok ? "ok" : "error",
          ok ? "Listo · revisa el resultado abajo" : msgError || "La corrida terminó con error"
        );
        mostrarUltimoResultado(demoId);
        if (demoId === 3 && typeof initDemo3PaqueteCiego === "function") initDemo3PaqueteCiego();
        finalizarVideo(evento);
      }
    };

    fuente.onerror = () => {
      if (!listo && fuente.readyState === EventSource.CONNECTING) {
        cerrar();
        reject(new Error("No se pudo abrir el avance en vivo."));
        return;
      }
      cerrar();
      bloquearHeroes(false);
      setEstadoCorrida("error", "Se perdió la conexión con el avance en vivo.");
    };
  });
}

document.querySelectorAll(".demo-tab").forEach((tab) => {
  tab.addEventListener("click", () => activarTab(tab.dataset.tab));
});

document.querySelectorAll("[data-ir-tab]").forEach((btn) => {
  btn.addEventListener("click", () => activarTab(btn.dataset.irTab));
});

function cuerpoCorrerDemo(demoId) {
  if (demoId !== 3) return undefined;
  const proveedor = document.getElementById("ref-proveedor");
  const modelo = document.getElementById("ref-modelo");
  const clave = document.getElementById("ref-api-key");
  const MODELOS = { anthropic: "claude-haiku-4-5", openai: "gpt-4o-mini" };
  const prov = proveedor?.value || "anthropic";
  return {
    proveedor: prov,
    modelo_referencia: modelo?.value.trim() || MODELOS[prov] || "claude-haiku-4-5",
    api_key: clave?.value.trim() || "",
  };
}

document.querySelectorAll("[data-demo-correr]").forEach((boton) => {
  const demoId = Number(boton.dataset.demoCorrer);
  const lista = document.querySelector("#avance");
  boton.addEventListener("click", async () => {
    lista.replaceChildren();
    const escenarioRoot = document.getElementById("escenario");
    if (escenarioRoot) {
      escenarioRoot.hidden = false;
      escenarioRoot.classList.remove("vacio", "fin-ok", "fin-error");
    }
    setEstadoCorrida("corriendo", demoId === 3 ? "Conectando avance en vivo…" : "Iniciando corrida…");
    bloquearHeroes(true);
    let enVivo = null;
    try {
      enVivo = await conectarEventos(demoId, lista);
    } catch (err) {
      bloquearHeroes(false);
      setEstadoCorrida("error", err.message || "No se pudo conectar el avance en vivo.");
      const li = document.createElement("li");
      li.className = "error";
      li.textContent = err.message || "No se pudo conectar el avance en vivo.";
      lista.prepend(li);
      return;
    }
    setEstadoCorrida("corriendo", demoId === 3 ? "Demo 3: local y referencia si hay API key…" : "Corrida en curso…");
    const cuerpo = cuerpoCorrerDemo(demoId);
    const resp = await fetch(`/api/demos/${demoId}/correr`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo || {}),
    });
    const data = await resp.json();
    if (!resp.ok || data.error) {
      enVivo.cerrar();
      bloquearHeroes(false);
      setEstadoCorrida("error", data.error || data.mensaje || "No se pudo iniciar.");
      const li = document.createElement("li");
      li.className = "error";
      li.textContent = data.error || data.mensaje || "No se pudo iniciar.";
      lista.prepend(li);
      return;
    }
    if (!data.sse) {
      enVivo.cerrar();
      bloquearHeroes(false);
      setEstadoCorrida("reposo", "Listo");
      if (data.mensaje) {
        const li = document.createElement("li");
        li.textContent = data.mensaje;
        lista.prepend(li);
      }
    }
  });
});

const CLAVE_IP_DEMO2 = "nodo-demo2-ip-manual";

async function aplicarEnlaceTelefono(ipQuery) {
  const params = new URLSearchParams();
  if (ipQuery) params.set("ip", ipQuery);
  const query = params.toString();
  const sufijo = query ? `?${query}` : "";
  const resp = await fetch(`/api/demo2/enlace${sufijo}`);
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error || "No se pudo actualizar el enlace");
  const img = document.getElementById("qr-telefono");
  const code = document.getElementById("url-telefono");
  const link = document.getElementById("url-telefono-abrir");
  const aviso = document.getElementById("aviso-ip");
  if (img) {
    const sep = query ? "&" : "?";
    img.src = `/api/demo2/qr.svg${sufijo}${sep}t=${Date.now()}`;
  }
  if (code) code.textContent = data.texto;
  if (link) {
    link.href = data.url;
    link.textContent = data.texto;
  }
  if (aviso) aviso.hidden = Boolean(data.ip);
  return data;
}

function initDemo2Telefono() {
  if (document.body.dataset.demo !== "2") return;
  const input = document.getElementById("ip-manual");
  const form = document.getElementById("form-ip-telefono");
  const detectar = document.getElementById("ip-detectar");
  const copiar = document.getElementById("copiar-url-telefono");
  const estado = document.getElementById("ip-estado");

  function mostrarEstado(texto, esError) {
    if (!estado) return;
    estado.hidden = false;
    estado.textContent = texto;
    estado.classList.toggle("error-texto", Boolean(esError));
  }

  const guardada = localStorage.getItem(CLAVE_IP_DEMO2);
  if (guardada && input) {
    input.value = guardada;
    aplicarEnlaceTelefono(guardada).catch((err) => mostrarEstado(err.message, true));
  }

  form?.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const ip = input?.value.trim();
    if (!ip) {
      mostrarEstado("Escribe la IPv4 del Mac en la red del router.", true);
      return;
    }
    try {
      const data = await aplicarEnlaceTelefono(ip);
      localStorage.setItem(CLAVE_IP_DEMO2, ip);
      mostrarEstado(
        data.origen === "manual"
          ? `Enlace listo con IP ${data.ip}. Escanéalo desde los teléfonos en la misma Wi‑Fi.`
          : "Enlace actualizado.",
        false
      );
    } catch (err) {
      mostrarEstado(err.message, true);
    }
  });

  detectar?.addEventListener("click", async () => {
    localStorage.removeItem(CLAVE_IP_DEMO2);
    try {
      const data = await aplicarEnlaceTelefono();
      if (input) input.value = data.ip_detectada || data.ip || "";
      mostrarEstado(data.ip_detectada ? `IP detectada: ${data.ip_detectada}` : "No hay IP en la LAN; escríbela a mano.", !data.ip_detectada);
    } catch (err) {
      mostrarEstado(err.message, true);
    }
  });

  copiar?.addEventListener("click", async () => {
    const texto = document.getElementById("url-telefono")?.textContent;
    if (!texto || texto.includes("<ip-de-este-equipo>")) {
      mostrarEstado("Primero define una IP válida.", true);
      return;
    }
    try {
      await navigator.clipboard.writeText(texto);
      mostrarEstado("Enlace copiado.", false);
    } catch {
      mostrarEstado("No pude copiar; selecciona el enlace a mano.", true);
    }
  });
}

initDemo2Telefono();

const CLAVE_REF_API = "nodo-demo3-api-key";
const CLAVE_REF_REC = "nodo-demo3-recordar-clave";

function actualizarAvisoApiDemo3() {
  const aviso = document.getElementById("demo3-aviso-api");
  const clave = document.getElementById("ref-api-key");
  if (!aviso) return;
  if (clave?.value.trim()) {
    aviso.textContent =
      "Con API key: en un solo clic se corre la mitad local (si falta) y luego la referencia comercial.";
  } else {
    aviso.textContent =
      "Sin API key de referencia comercial: solo se ejecutará la mitad local (40 respuestas en Ollama).";
  }
}

function initDemo3Referencia() {
  if (document.body.dataset.demo !== "3") return;
  const proveedor = document.getElementById("ref-proveedor");
  const modelo = document.getElementById("ref-modelo");
  const clave = document.getElementById("ref-api-key");
  const recordar = document.getElementById("ref-recordar");

  const MODELOS = {
    anthropic: "claude-haiku-4-5",
    openai: "gpt-4o-mini",
  };

  if (sessionStorage.getItem(CLAVE_REF_REC) === "1") {
    const guardada = sessionStorage.getItem(CLAVE_REF_API);
    if (guardada && clave) {
      clave.value = guardada;
      if (recordar) recordar.checked = true;
    }
  }

  proveedor?.addEventListener("change", () => {
    if (modelo && MODELOS[proveedor.value]) {
      modelo.value = MODELOS[proveedor.value];
    }
  });

  clave?.addEventListener("input", actualizarAvisoApiDemo3);

  recordar?.addEventListener("change", () => {
    if (!recordar.checked) {
      sessionStorage.removeItem(CLAVE_REF_API);
      sessionStorage.removeItem(CLAVE_REF_REC);
    }
  });

  clave?.addEventListener("change", () => {
    if (recordar?.checked && clave?.value.trim()) {
      sessionStorage.setItem(CLAVE_REF_REC, "1");
      sessionStorage.setItem(CLAVE_REF_API, clave.value.trim());
    }
    actualizarAvisoApiDemo3();
  });

  actualizarAvisoApiDemo3();
}

async function initDemo3PaqueteCiego() {
  if (document.body.dataset.demo !== "3") return;
  const bloques = [
    {
      panel: document.getElementById("demo3-paso-ciego"),
      resumen: document.getElementById("demo3-ciego-resumen"),
      btn: document.getElementById("btn-calificar-ciego"),
    },
    {
      panel: document.getElementById("demo3-resultados-ciego"),
      resumen: document.getElementById("demo3-res-ciego-resumen"),
      btn: document.getElementById("btn-calificar-ciego-resultados"),
    },
  ];
  try {
    let payload = { paquetes: [] };
    for (const url of ["/api/demos/3/paquetes-ciegos", "/api/demo3/paquetes-ciegos"]) {
      const resp = await fetch(url);
      if (resp.ok) {
        payload = await resp.json();
        break;
      }
    }
    const paquetes = payload.paquetes || [];
    const mostrar = paquetes.length > 0 && (payload.falta_calificacion ?? true);
    const principal = paquetes[0];
    const href = principal ? `/calificar?paquete=${encodeURIComponent(principal.id)}` : "/calificar";
    const textoResumen = principal?.etiqueta || (principal ? `Paquete con ${principal.tareas} tareas.` : "");
    for (const { panel, resumen, btn } of bloques) {
      if (!panel) continue;
      panel.hidden = !mostrar;
      if (mostrar && resumen) resumen.textContent = textoResumen;
      if (btn) btn.href = href;
    }
    return { mostrar, paquetes, href };
  } catch {
    for (const { panel } of bloques) {
      if (panel) panel.hidden = true;
    }
    return { mostrar: false, paquetes: [], href: "/calificar" };
  }
}

initDemo3Referencia();
initDemo3PaqueteCiego();
window.initDemo3PaqueteCiego = initDemo3PaqueteCiego;

function initDemoCarrusel() {
  const carrusel = document.getElementById("demo-carrusel");
  if (!carrusel) return;
  const paso = () => Math.max(240, Math.round(carrusel.clientWidth * 0.72));
  document.querySelectorAll(".demo-carrusel-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const dir = Number(btn.dataset.dir);
      const movimiento = prefersReducedMotion() ? "auto" : "smooth";
      carrusel.scrollBy({ left: dir * paso(), behavior: movimiento });
    });
  });
}

function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

initDemoCarrusel();

function initLecturaExplicacion() {
  const demoId = Number(document.body.dataset.demo);
  const btn = document.getElementById("leer-explicacion");
  const audio = document.getElementById("audio-explicacion");
  const estado = document.getElementById("leer-explicacion-estado");
  const etiqueta = btn?.querySelector(".demo-btn-voz-texto");
  if (!btn || !audio || !demoId || !etiqueta) return;

  const textos = {
    reposo: "Escuchar explicación",
    cargando: "Preparando voz…",
    repro: "Detener lectura",
  };
  let cargando = false;

  const ponerEstado = (txt, visible = Boolean(txt)) => {
    if (!estado) return;
    estado.textContent = txt;
    estado.hidden = !visible;
  };

  const esReproduciendo = () => !audio.paused && !audio.ended && audio.currentTime > 0;

  btn.addEventListener("click", async () => {
    if (cargando) return;
    if (esReproduciendo()) {
      audio.pause();
      audio.currentTime = 0;
      etiqueta.textContent = textos.reposo;
      ponerEstado("");
      return;
    }
    cargando = true;
    btn.disabled = true;
    etiqueta.textContent = textos.cargando;
    ponerEstado("Voz narradora Piper (alta calidad) en este computador, sin internet…");
    try {
      const resp = await fetch(`/api/demos/${demoId}/explicacion-voz`, { method: "POST" });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "No se pudo generar la voz");
      audio.src = `data:audio/wav;base64,${data.audio_b64}`;
      etiqueta.textContent = textos.repro;
      const nombreVoz = data.voz ? data.voz.replace(".onnx", "") : "narración";
      ponerEstado(`Reproduciendo con ${nombreVoz} (${data.tts_s ?? "?"} s de síntesis)…`);
      await audio.play();
    } catch (err) {
      etiqueta.textContent = textos.reposo;
      ponerEstado(err.message || "Error al leer");
      btn.disabled = false;
      cargando = false;
      return;
    }
    btn.disabled = false;
    cargando = false;
  });

  audio.addEventListener("ended", () => {
    etiqueta.textContent = textos.reposo;
    ponerEstado("");
  });
}

initLecturaExplicacion();

const demoEnPagina = document.body.dataset.demo;
if (demoEnPagina) {
  const id = Number(demoEnPagina);
  fetch(`/api/demos/${id}/estado`)
    .then((r) => r.json())
    .then((d) => {
      if (d.corriendo) {
        setEstadoCorrida("corriendo", "Hay una corrida en curso en este demo…");
        bloquearHeroes(true);
      }
    })
    .catch(() => {});
}
