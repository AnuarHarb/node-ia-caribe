function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function estadoInforme(demoId, data) {
  if (!data) {
    return { clase: "pendiente", texto: "Sin medición aún" };
  }
  if (data.criterio_cumplido === true) {
    return { clase: "ok", texto: "Criterio cumplido" };
  }
  if (demoId === 2) {
    // Igual que en el servidor: el criterio son tres partes medidas, no solo el tiempo.
    if (!data.consultas_voz || data.entrada === "texto") {
      return { clase: "pendiente", texto: "Falta la medición por voz" };
    }
    if (data.criterios?.tiempo === false || data.criterio_10s === false) {
      return { clase: "falla", texto: "Promedio por encima de 10 s" };
    }
    return { clase: "parcial", texto: "Medición por voz · criterio incompleto" };
  }
  if (demoId === 4) {
    const medidas = (data.variedades || []).length;
    if (!medidas) return { clase: "pendiente", texto: "Sin frases medidas" };
    return {
      clase: "parcial",
      texto: medidas < 2 ? "Falta una variedad por medir" : "Cifra por variedad · muestra corta",
    };
  }
  if (demoId === 5 && data.criterio_cumplido === false) {
    return { clase: "falla", texto: "Criterio no cumplido" };
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
    if (data.bloqueo?.bloqueado != null) {
      items.push({ etiqueta: "Acceso cruzado", valor: data.bloqueo.bloqueado ? "Bloqueado" : "No bloqueado" });
    }
  } else if (demoId === 1) {
    items.push({ etiqueta: "Frases medidas", valor: data.filas ?? 0 });
    items.push({ etiqueta: "Hablantes", valor: data.cobertura?.hablantes ?? "—" });
    items.push({ etiqueta: "Frases con error", valor: data.errores_marcados ?? 0 });
    items.push({ etiqueta: "WER", valor: data.wer_corpus?.wer_porcentaje != null ? `${data.wer_corpus.wer_porcentaje} %` : "—" });
  } else if (demoId === 2) {
    const voz = data.consultas_voz > 0 && data.entrada !== "texto";
    items.push({ etiqueta: "Usuarios a la vez", valor: voz ? data.usuarios_simultaneos ?? "—" : "Sin medir" });
    items.push({ etiqueta: "Promedio", valor: voz && data.tiempo_promedio_s != null ? `${data.tiempo_promedio_s} s` : "Sin medir" });
    items.push({ etiqueta: "Máximo", valor: voz && data.tiempo_maximo_s != null ? `${data.tiempo_maximo_s} s` : "Sin medir" });
    items.push({
      etiqueta: "Red",
      valor: !voz ? "Sin medir" : data.sin_internet === true ? "Sin internet" : data.sin_internet === false ? "Con internet" : "Sin registrar",
    });
  } else if (demoId === 3) {
    const calidad = data.paquete_ciego?.calificacion?.calidad_promedio;
    if (calidad?.local != null) {
      items.push({ etiqueta: "Calidad local / ref.", valor: `${Number(calidad.local).toFixed(2)} / ${Number(calidad.referencia).toFixed(2)}` });
    }
    const c = data.comparacion || {};
    items.push({ etiqueta: "Local / ref.", valor: `${c.respuestas_local ?? data.tareas_local ?? 0}/${c.respuestas_referencia ?? data.tareas_referencia ?? 0}` });
    items.push({ etiqueta: "Caliente", valor: data.tiempo_promedio_caliente_s != null ? `${data.tiempo_promedio_caliente_s} s` : "—" });
    const cal = data.paquete_ciego?.calificacion;
    items.push({
      etiqueta: "Ciego",
      valor: data.comparacion_completa ? (cal?.estado === "calculado" ? "Calificado" : cal?.estado === "parcial" ? "1/2 cal." : "Listo") : "Pendiente",
    });
  } else if (demoId === 4) {
    const medidas = data.variedades || [];
    for (const v of medidas) {
      items.push({ etiqueta: `${v.variedad} · ${v.frases} frases`, valor: `${v.wer_porcentaje} % WER` });
    }
    if (!medidas.some((v) => (v.clave || v.variedad) === "palenquero")) {
      items.push({ etiqueta: "palenquero", valor: "Sin medir" });
    }
    if (!medidas.some((v) => (v.clave || "").startsWith("coste") || String(v.variedad).includes("coste"))) {
      items.push({ etiqueta: "español costeño", valor: "Sin medir" });
    }
  }
  return items.slice(0, 4);
}

function audiosDemo1(data) {
  // Los audios no van en la nota (no se publican); aquí se pueden oír en el equipo donde se grabaron.
  const conAudio = (data.tabla || []).filter((f) => f.audio_entrada_url);
  if (!conAudio.length) return "";
  const filas = (data.tabla || [])
    .map(
      (f, i) =>
        `<tr>
          <th scope="row">${i + 1}</th>
          <td>${escapeHtml(f.persona || "")}</td>
          <td class="col-texto">${escapeHtml(f.transcripcion_correcta || "")}</td>
          <td>${
            f.audio_entrada_url
              ? `<audio controls preload="none" src="${escapeHtml(f.audio_entrada_url)}" aria-label="Grabación de la frase ${i + 1}"></audio>`
              : "Sin audio"
          }</td>
        </tr>`
    )
    .join("");
  return `<details class="informe-details">
    <summary>Escuchar las grabaciones (solo en este equipo)</summary>
    <table class="datos informe-tabla">
      <caption>Grabación de cada frase medida</caption>
      <thead><tr><th scope="col">#</th><th scope="col">Hablante</th><th scope="col">Lo que se dijo</th><th scope="col">Grabación</th></tr></thead>
      <tbody>${filas}</tbody>
    </table>
  </details>`;
}

async function cargarNota(destino, demoId, corridaId) {
  // La nota técnica la arma el servidor: es el mismo documento del PDF y de la vista para imprimir.
  const consulta = corridaId ? `?corrida=${encodeURIComponent(corridaId)}` : "";
  try {
    const resp = await fetch(`/api/demos/${demoId}/nota${consulta}`);
    if (!resp.ok) throw new Error(`respuesta ${resp.status}`);
    destino.innerHTML = await resp.text();
  } catch (err) {
    destino.innerHTML = `<p class="error-texto" role="alert">No se pudo cargar la nota técnica (${escapeHtml(err.message)}). Recarga la página.</p>`;
  }
}

function renderInforme(container, data, demoId, opciones = {}) {
  demoId = demoId ?? (Number(document.body.dataset.demo) || 0);
  if (!data) {
    container.innerHTML = `<p class="pendiente">Todavía no hay informe. Sigue el protocolo o usa <strong>Correr de nuevo</strong>.</p>`;
    return;
  }
  const extraDemo3 =
    demoId === 3 && data.ultima_corrida_error
      ? `<p class="informe-alerta error-texto" role="alert"><strong>Última corrida comercial/local:</strong> ${escapeHtml(
          data.ultima_corrida_error
        )}</p>`
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

  if (opciones.completo) {
    // Vista completa: la nota técnica entera y, en el demo 1, los audios de cada frase.
    container.innerHTML = `<div class="informe-resumen">
      ${extraDemo3}
      ${ctaCiego}
      <div class="nota-en-pantalla" aria-live="polite"><p class="pendiente">Cargando la nota técnica…</p></div>
      ${demoId === 1 ? audiosDemo1(data) : ""}
    </div>`;
    cargarNota(container.querySelector(".nota-en-pantalla"), demoId, opciones.corridaId);
    return;
  }

  // Vista corta, al terminar una corrida: estado, cifras principales y el camino a la nota.
  const estado = estadoInforme(demoId, data);
  const kpis = kpisDeInforme(demoId, data);
  const kpiHtml = kpis.length
    ? `<ul class="kpi-row" aria-label="Indicadores principales">${kpis.map((k) => `<li><span class="kpi-valor">${escapeHtml(String(k.valor))}</span><span class="kpi-etiqueta">${escapeHtml(k.etiqueta)}</span></li>`).join("")}</ul>`
    : "";
  const faltantes = [...(data.faltantes || []), ...(Array.isArray(data.pendiente) ? data.pendiente : []), ...(data.advertencias || [])];
  container.innerHTML = `<div class="informe-resumen estado-${estado.clase}">
    <span class="estado-badge ${estado.clase}">${escapeHtml(estado.texto)}</span>
    ${extraDemo3}
    ${ctaCiego}
    ${kpiHtml}
    ${data.resumen_ejecutivo ? `<p class="informe-nota">${escapeHtml(data.resumen_ejecutivo)}</p>` : ""}
    ${faltantes.length ? `<ul class="informe-faltantes">${faltantes.map((f) => `<li>${escapeHtml(String(f))}</li>`).join("")}</ul>` : ""}
    <p class="informe-exportar">
      <a class="enlace-json" href="/demo/${demoId}/informe/imprimir" target="_blank" rel="noopener">Ver la nota técnica</a>
      <a class="enlace-json" href="/api/demos/${demoId}/informe.pdf">Descargar PDF</a>
    </p>
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
  nav.innerHTML = `<a class="enlace-json" href="/demo/${demoId}/informe/imprimir?corrida=${q}" target="_blank" rel="noopener">Abrir la nota para imprimir</a>
    <a class="enlace-json" href="/api/demos/${demoId}/informe.pdf?corrida=${q}">Descargar PDF</a>
    ${videoLink}
    ${enlaceCiego}`;
  const cuerpo = document.createElement("div");
  detalle.appendChild(nav);
  detalle.appendChild(cuerpo);
  renderInforme(cuerpo, data, demoId, { completo: true, corridaId });
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
      // Sin corridas todavía: se muestra la nota tal como está, con el montaje y el procedimiento.
      detalle.innerHTML = `<nav class="informe-exportar" aria-label="Exportar la nota">
          <a class="enlace-json" href="/demo/${demoId}/informe/imprimir" target="_blank" rel="noopener">Abrir la nota para imprimir</a>
          <a class="enlace-json" href="/api/demos/${demoId}/informe.pdf">Descargar PDF</a>
        </nav>
        <div class="nota-en-pantalla" aria-live="polite"><p class="pendiente">Cargando la nota técnica…</p></div>`;
      cargarNota(detalle.querySelector(".nota-en-pantalla"), demoId);
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

function initDemo2Medicion() {
  if (document.body.dataset.demo !== "2") return;
  const estadoRed = document.getElementById("red-estado");
  const form = document.getElementById("form-consumo");
  const estadoConsumo = document.getElementById("consumo-estado");

  async function comprobarRed() {
    if (!estadoRed || document.hidden) return;
    try {
      const datos = await (await fetch("/api/red")).json();
      estadoRed.dataset.red = datos.internet ? "con" : "sin";
      estadoRed.textContent = datos.internet
        ? "Este equipo SÍ tiene salida a internet ahora. Desconecta el router antes de medir."
        : "Este equipo está sin salida a internet. Se puede medir.";
    } catch {
      estadoRed.dataset.red = "desconocida";
      estadoRed.textContent = "No se pudo comprobar la red.";
    }
  }
  comprobarRed();
  setInterval(comprobarRed, 10000);

  fetch("/api/demos/2/informe")
    .then((resp) => (resp.ok ? resp.json() : null))
    .then((informe) => {
      const consumo = informe?.consumo;
      if (!consumo || !form) return;
      if (consumo.reposo_w != null) form.elements.reposo_w.value = consumo.reposo_w;
      if (consumo.carga_w != null) form.elements.carga_w.value = consumo.carga_w;
      if (consumo.instrumento) form.elements.instrumento.value = consumo.instrumento;
    })
    .catch(() => {});

  form?.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const cuerpo = {
      reposo_w: form.elements.reposo_w.value,
      carga_w: form.elements.carga_w.value,
      instrumento: form.elements.instrumento.value,
    };
    estadoConsumo.hidden = false;
    estadoConsumo.classList.remove("error-texto");
    estadoConsumo.textContent = "Guardando…";
    try {
      const resp = await fetch("/api/demos/2/consumo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cuerpo),
      });
      const datos = await resp.json();
      if (!resp.ok) throw new Error(datos.error || "no se pudo guardar");
      estadoConsumo.textContent = "Consumo guardado. Entra en el informe y en la nota técnica.";
    } catch (err) {
      estadoConsumo.classList.add("error-texto");
      estadoConsumo.textContent = `No se guardó: ${err.message}. Escribe al menos una lectura en vatios.`;
    }
  });
}

initDemo2Medicion();

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

function filaCorpusLista(items) {
  if (!items?.length) return "<p class=\"pendiente\">Ningún archivo todavía.</p>";
  const rows = items
    .map(
      (it) =>
        `<tr><td>${escapeHtml(it.id)}</td><td>${escapeHtml(it.referencia)}</td><td>${it.audio ? "Sí" : "—"}</td><td>${it.hipotesis ? "Sí" : "pendiente"}</td></tr>`
    )
    .join("");
  return `<table class="informe-tabla"><thead><tr><th>Id</th><th>Referencia</th><th>Audio</th><th>.hip.txt</th></tr></thead><tbody>${rows}</tbody></table>`;
}

async function initDemo4Corpus() {
  if (document.body.dataset.demo !== "4") return;
  const resumen = document.getElementById("corpus-resumen");
  const tablas = document.getElementById("corpus-tablas");
  const form = document.getElementById("form-corpus-demo4");
  const estado = document.getElementById("corpus-estado");
  if (!form || !resumen) return;

  const pintar = async () => {
    const resp = await fetch("/api/demos/4/corpus");
    const data = await resp.json();
    const d1 = data.demo1_filas || {};
    resumen.textContent = `Demo 1: ${d1.costeno ?? 0} filas costeñas, ${d1.palenquero ?? 0} filas palenqueras. En carpeta: costeño ${(data.carpetas?.costeno || []).length}, palenquero ${(data.carpetas?.palenquero || []).length}.`;
    if (tablas) {
      tablas.innerHTML = `<h3>Costeño</h3>${filaCorpusLista(data.carpetas?.costeno)}<h3>Palenquero</h3>${filaCorpusLista(data.carpetas?.palenquero)}`;
    }
  };

  await pintar();

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const archivo = document.getElementById("corpus-audio")?.files?.[0];
    if (!archivo) return;
    estado.hidden = false;
    estado.textContent = "Subiendo…";
    const b64 = await new Promise((resolve, reject) => {
      const r = new FileReader();
      r.onload = () => resolve(String(r.result).split(",")[1]);
      r.onerror = reject;
      r.readAsDataURL(archivo);
    });
    const resp = await fetch("/api/demos/4/corpus", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        variedad: document.getElementById("corpus-variedad")?.value || "palenquero",
        id: document.getElementById("corpus-id")?.value.trim(),
        referencia: document.getElementById("corpus-ref")?.value.trim(),
        audio_b64: b64,
        mime: archivo.type || "audio/webm",
      }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      estado.textContent = data.error || "No se pudo guardar.";
      return;
    }
    estado.textContent = "Guardado. Al correr el experimento, Whisper generará .hip.txt si hace falta.";
    form.reset();
    await pintar();
  });
}

initDemo4Corpus();

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
