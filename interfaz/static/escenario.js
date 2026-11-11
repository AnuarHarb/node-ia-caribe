/* Cola visual de escenas mientras corre un demo (SSE). */

const PAUSA_ESCENA_MS = 700;

function pausaEscena() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : PAUSA_ESCENA_MS;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function etiquetaEntidad(id) {
  if (id === "alcaldia-santa-marta") return "Alcaldía Santa Marta";
  if (id === "gobernacion-atlantico") return "Gobernación Atlántico";
  return id || "Entidad";
}

class ReproductorEscenario {
  constructor(demoId, root) {
    this.demoId = demoId;
    this.root = root;
    this.cola = [];
    this.procesando = false;
    this.ultimoT = 0;
    this.estado = {};
  }

  reset() {
    this.cola = [];
    this.procesando = false;
    this.ultimoT = 0;
    this.estado = {};
    if (this.root) {
      this.root.hidden = false;
      this.root.classList.remove("vacio", "fin-ok", "fin-error");
      this.armarEstructura();
    }
  }

  armarEstructura() {
    if (!this.root) return;
    if (this.demoId === 5) {
      this.root.innerHTML = `
        <div class="escenario-5-grid">
          <article class="caja-entidad" data-entidad="alcaldia-santa-marta">
            <h3>Alcaldía Santa Marta</h3>
            <ul class="caja-archivos" aria-label="Archivos en la caja de la alcaldía"></ul>
          </article>
          <figure class="flecha-cruzada" aria-hidden="true"><span>↗</span></figure>
          <article class="caja-entidad" data-entidad="gobernacion-atlantico">
            <h3>Gobernación Atlántico</h3>
            <ul class="caja-archivos" aria-label="Archivos en la caja de la gobernación"></ul>
          </article>
        </div>
        <ol class="auditoria-escena" aria-label="Cadena de auditoría"></ol>
        <ol class="pruebas-escena" aria-label="Pruebas automatizadas"></ol>
        <p class="escenario-pie" aria-live="polite"></p>`;
      this.estado.bloqueoActivo = false;
    } else if (this.demoId === 3) {
      this.root.innerHTML = `
        <div class="escenario-3-grid">
          <div class="col-tareas" data-col="local">
            <h3>Local (Ollama)</h3>
            <p class="contador-tareas"><span data-contador="local">0</span> / 40</p>
            <p class="ultima-tarea" data-ultima="local">—</p>
          </div>
          <div class="col-tareas" data-col="referencia">
            <h3>Referencia comercial</h3>
            <p class="contador-tareas"><span data-contador="referencia">0</span> / 40</p>
            <p class="ultima-tarea" data-ultima="referencia">—</p>
          </div>
        </div>
        <p class="escenario-pie" aria-live="polite"></p>`;
      this.estado.local = 0;
      this.estado.referencia = 0;
    } else if (this.demoId === 4) {
      this.root.innerHTML = `
        <div class="escenario-4-grid">
          <div class="wer-medidor" data-variedad="costeno">
            <h3>Español costeño</h3>
            <meter min="0" max="100" value="0"></meter>
            <p class="wer-valor">Sin medición</p>
          </div>
          <div class="wer-medidor" data-variedad="palenquero">
            <h3>Palenquero</h3>
            <meter min="0" max="100" value="0"></meter>
            <p class="wer-valor">Sin medición</p>
          </div>
        </div>
        <p class="escenario-pie" aria-live="polite"></p>`;
    } else if (this.demoId === 2) {
      this.root.innerHTML = `
        <div class="escenario-2-grid">
          <article class="tarjeta-usuario" data-u="1"><h3>Usuario 1</h3><p class="tiempo">—</p></article>
          <article class="tarjeta-usuario" data-u="2"><h3>Usuario 2</h3><p class="tiempo">—</p></article>
          <article class="tarjeta-usuario" data-u="3"><h3>Usuario 3</h3><p class="tiempo">—</p></article>
        </div>
        <p class="escenario-pie" aria-live="polite">Esperando consultas…</p>`;
    } else {
      this.root.innerHTML = `<p class="escenario-pie" aria-live="polite"></p>`;
    }
    this.root.classList.add(`escenario-${this.demoId}`);
  }

  pie(texto) {
    const el = this.root?.querySelector(".escenario-pie");
    if (el) el.textContent = texto;
  }

  encolar(trabajo) {
    this.cola.push(trabajo);
    if (!this.procesando) this._siguiente();
  }

  _siguiente() {
    if (!this.cola.length) {
      this.procesando = false;
      return;
    }
    this.procesando = true;
    const trabajo = this.cola.shift();
    trabajo();
    setTimeout(() => this._siguiente(), pausaEscena());
  }

  onEvent(evento) {
    if (!this.root) return;
    this.root.hidden = false;
    this.root.classList.remove("vacio");
    if (evento.tipo === "inicio" && !this.root.querySelector(".escenario-pie")) {
      this.armarEstructura();
    }
    this.encolar(() => this._aplicar(evento));
  }

  _aplicar(evento) {
    const d = evento.datos || {};
    const msg = evento.mensaje || "";

    if (evento.tipo === "inicio") {
      this.pie("Corrida en curso…");
      return;
    }
    if (evento.tipo === "error") {
      this.root.classList.add("fin-error");
      this.pie(msg);
      return;
    }
    if (evento.tipo === "fin") {
      this.root.classList.add(d.ok === false ? "fin-error" : "fin-ok");
      this.pie(d.ok === false ? "Corrida terminada con error." : "Corrida terminada.");
      return;
    }

    if (this.demoId === 5) {
      this._demo5(evento);
    } else if (this.demoId === 3) {
      this._demo3(evento);
    } else if (this.demoId === 4) {
      this._demo4(evento);
    } else if (this.demoId === 2) {
      this._demo2(evento);
    } else {
      this.pie(msg);
    }
  }

  _demo5(evento) {
    const d = evento.datos || {};
    if (evento.tipo === "caja" && d.entidad && d.ruta) {
      const caja = this.root.querySelector(`.caja-entidad[data-entidad="${d.entidad}"] .caja-archivos`);
      if (caja) {
        const li = document.createElement("li");
        li.textContent = d.ruta;
        li.classList.add("nuevo");
        caja.appendChild(li);
      }
      this.pie(`${etiquetaEntidad(d.entidad)}: ${d.accion || "escritura"} en ${d.ruta}`);
      return;
    }
    if (evento.tipo === "bloqueo") {
      this.root.classList.add("bloqueo-activo");
      const flecha = this.root.querySelector(".flecha-cruzada");
      if (flecha) flecha.classList.add("rebotada");
      this.pie(d.bloqueado ? `Bloqueado: ${d.motivo || "acceso cruzado"}` : "¡Fallo! El acceso cruzado no quedó bloqueado.");
      return;
    }
    if (evento.tipo === "auditoria") {
      const lista = this.root.querySelector(".auditoria-escena");
      if (lista) {
        const li = document.createElement("li");
        const ok = d.resultado === "permitido";
        li.className = ok ? "audit-ok" : "audit-deny";
        li.innerHTML = `<span class="audit-n">#${escapeHtml(String(d.n || ""))}</span> ${escapeHtml(
          String(d.entidad || "")
        )} · ${escapeHtml(String(d.accion || ""))} · <code>${escapeHtml(String(d.ruta || ""))}</code> · ${escapeHtml(
          String(d.resultado || "")
        )}`;
        lista.appendChild(li);
      }
      this.pie(evento.mensaje);
      return;
    }
    if (evento.tipo === "prueba") {
      const lista = this.root.querySelector(".pruebas-escena");
      const obtenido = d.obtenido || evento.mensaje.split(": ").slice(1).join(": ");
      const nombre = d.prueba || evento.mensaje.split(":")[0];
      const ok = String(obtenido).toLowerCase().includes("pasó");
      if (lista) {
        const li = document.createElement("li");
        li.className = ok ? "prueba-ok" : "prueba-falla";
        li.textContent = `${nombre}: ${obtenido}`;
        lista.appendChild(li);
      }
      this.pie(`Prueba ${nombre}`);
      return;
    }
    if (evento.tipo === "informe") {
      this.pie(evento.mensaje);
      return;
    }
    this.pie(evento.mensaje);
  }

  _demo3(evento) {
    if (evento.tipo === "progreso") {
      const d = evento.datos || {};
      if (typeof d.local === "number") {
        this.estado.local = d.local;
        const span = this.root.querySelector('[data-contador="local"]');
        if (span) span.textContent = String(d.local);
      }
      if (typeof d.referencia === "number") {
        this.estado.referencia = d.referencia;
        const span = this.root.querySelector('[data-contador="referencia"]');
        if (span) span.textContent = String(d.referencia);
      }
      this.pie(evento.mensaje);
      return;
    }
    if (evento.tipo === "error") {
      this.root.classList.add("fin-error");
      this.pie(evento.mensaje);
      return;
    }
    if (evento.tipo === "tarea") {
      const esRef = /referencia/i.test(evento.mensaje);
      const col = dCol(evento.datos, esRef ? "referencia" : "local");
      const datos = evento.datos || {};
      if (!datos.reutilizada) {
        if (!this.estado[col]) this.estado[col] = 0;
        this.estado[col] += 1;
        const span = this.root.querySelector(`[data-contador="${col}"]`);
        if (span) span.textContent = String(this.estado[col]);
      }
      const ultima = this.root.querySelector(`[data-ultima="${col}"]`);
      const id = (evento.datos && evento.datos.id) || evento.mensaje.split(" ")[0];
      if (ultima) ultima.textContent = `${id} · ${evento.mensaje}`;
      this.root.querySelector(`[data-col="${col}"]`)?.classList.add("activa");
      this.pie(evento.mensaje);
      return;
    }
    if (evento.tipo === "informe" || evento.tipo === "aviso" || evento.tipo === "paso") {
      this.pie(evento.mensaje);
    }
  }

  _demo4(evento) {
    if (evento.tipo === "wer") {
      const d = evento.datos || {};
      let clave = d.clave || "";
      const match = evento.mensaje.match(/^(Costeño|Palenquero)/i);
      if (match) clave = match[0].toLowerCase().startsWith("cost") ? "costeno" : "palenquero";
      const pct = d.wer_porcentaje ?? d.wer ?? parseFloat(evento.mensaje.match(/([\d.]+)\s*%/)?.[1] || "0");
      const bloque = this.root.querySelector(`.wer-medidor[data-variedad="${clave}"]`);
      if (bloque) {
        const meter = bloque.querySelector("meter");
        const val = bloque.querySelector(".wer-valor");
        if (meter) meter.value = pct;
        if (val) val.textContent = `${pct} % WER · ${d.frases || "?"} frases`;
        bloque.classList.add("medido");
      }
      this.pie(evento.mensaje);
      return;
    }
    this.pie(evento.mensaje || "Calculando WER…");
  }

  _demo2(evento) {
    if (evento.tipo === "turno") {
      const u = (evento.datos && evento.datos.usuario) || parseInt(evento.mensaje.match(/Usuario\s+(\d+)/)?.[1] || "0", 10);
      const tarjeta = this.root.querySelector(`.tarjeta-usuario[data-u="${u}"]`);
      if (tarjeta) {
        tarjeta.classList.add("activa");
        const t = tarjeta.querySelector(".tiempo");
        const seg = (evento.datos && evento.datos.segundos) || evento.mensaje.match(/([\d.]+)\s*s/)?.[1];
        if (t) t.textContent = seg ? `${seg} s` : evento.mensaje;
      }
      this.pie(evento.mensaje);
      return;
    }
    if (evento.tipo === "paso") {
      this.pie(`${evento.mensaje} (medición parcial por texto si no hay teléfonos).`);
      return;
    }
    if (evento.tipo === "informe") {
      this.pie(evento.mensaje);
    }
  }
}

function dCol(datos, fallback) {
  if (datos && datos.columna) return datos.columna;
  return fallback;
}

function escenarioVozPaso(paso, texto) {
  const root = document.getElementById("escenario-voz");
  if (!root) return;
  root.hidden = false;
  root.classList.remove("vacio");
  root.querySelectorAll(".flujo-voz li").forEach((li) => {
    li.classList.toggle("activo", li.dataset.paso === paso);
    li.classList.toggle("hecho", ordenPaso(li.dataset.paso) < ordenPaso(paso));
  });
  const pie = root.querySelector(".escenario-pie");
  if (pie) pie.textContent = texto;
}

function ordenPaso(paso) {
  return { grabar: 0, transcribir: 1, responder: 2 }[paso] ?? 0;
}

function escenarioVozReset() {
  const root = document.getElementById("escenario-voz");
  if (!root) return;
  root.querySelectorAll(".flujo-voz li").forEach((li) => {
    li.classList.remove("activo", "hecho");
  });
}

window.ReproductorEscenario = ReproductorEscenario;
window.escenarioVozPaso = escenarioVozPaso;
window.escenarioVozReset = escenarioVozReset;
