/* Demo 1: sesión de voz guiada. Quién habla → grabar la frase → revisar y guardar. */

(function () {
  const raiz = document.getElementById("sesion-voz");
  if (!raiz) return;

  const LISTAS = JSON.parse(document.getElementById("frases-demo1").textContent);
  const CLAVE = "nodo-demo1-sesion";
  const $ = (selector) => raiz.querySelector(selector);

  const estado = {
    persona: "",
    variedad: "costeno",
    indice: 0,
    guardadas: new Map(), // guion → "si" | "no"
    grabador: null,
    flujo: null,
    trozos: [],
    inicio: 0,
    reloj: null,
    analizador: null,
    contextoAudio: null,
    ultimo: null,
    ultimoGuardado: null,
    hablo: false,
    ultimoSonido: 0,
    ocupado: false,
  };

  // El nivel del medidor por encima del cual se considera que hay voz, y cuánto silencio cierra la frase.
  const UMBRAL_VOZ = 0.06;
  const SILENCIO_MS = 1400;
  const MAXIMO_MS = 30000;

  // ——— utilidades ———

  function normalizar(texto) {
    return String(texto || "")
      .toLowerCase()
      .replace(/[\p{P}]/gu, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function escapar(texto) {
    const div = document.createElement("div");
    div.textContent = String(texto ?? "");
    return div.innerHTML;
  }

  /** Marca las palabras del sistema que no están, en orden, en lo que se dijo. */
  function resaltarDiferencias(correcta, sistema) {
    const a = normalizar(correcta).split(" ").filter(Boolean);
    const original = String(sistema || "").split(/\s+/).filter(Boolean);
    const b = original.map((palabra) => normalizar(palabra));
    const tabla = Array.from({ length: a.length + 1 }, () => new Array(b.length + 1).fill(0));
    for (let i = a.length - 1; i >= 0; i--) {
      for (let j = b.length - 1; j >= 0; j--) {
        tabla[i][j] = a[i] === b[j] ? tabla[i + 1][j + 1] + 1 : Math.max(tabla[i + 1][j], tabla[i][j + 1]);
      }
    }
    const iguales = new Set();
    let i = 0;
    let j = 0;
    while (i < a.length && j < b.length) {
      if (a[i] === b[j]) {
        iguales.add(j);
        i++;
        j++;
      } else if (tabla[i + 1][j] >= tabla[i][j + 1]) {
        i++;
      } else {
        j++;
      }
    }
    const distintas = original.length - iguales.size + Math.max(0, a.length - iguales.size);
    const html = original
      .map((palabra, k) => (iguales.has(k) || !b[k] ? escapar(palabra) : `<mark>${escapar(palabra)}</mark>`))
      .join(" ");
    return { html: html || "<em>(no entendió nada)</em>", distintas, coincide: normalizar(correcta) === normalizar(sistema) };
  }

  function mostrarError(panel, texto) {
    const nodo = raiz.querySelector(`[data-panel="${panel}"] .voz-error`);
    if (!nodo) return;
    nodo.hidden = !texto;
    nodo.textContent = texto || "";
  }

  function irA(paso) {
    raiz.dataset.paso = paso;
    raiz.querySelectorAll("[data-panel]").forEach((panel) => {
      panel.hidden = panel.dataset.panel !== paso;
    });
    raiz.querySelectorAll(".sesion-pasos li").forEach((li) => {
      const orden = ["quien", "grabar", "revisar"];
      li.classList.toggle("activo", li.dataset.paso === paso);
      li.classList.toggle("hecho", orden.indexOf(li.dataset.paso) < orden.indexOf(paso));
      if (li.dataset.paso === paso) li.setAttribute("aria-current", "step");
      else li.removeAttribute("aria-current");
    });
  }

  function esPalenquero() {
    return estado.variedad === "palenquero";
  }

  function frases() {
    return esPalenquero() ? LISTAS.palenquero.map((frase) => frase.texto) : LISTAS.costeno;
  }

  function fraseLibre() {
    return esPalenquero() ? $("#guion-palenquero").value.trim() : "";
  }

  function guionActual() {
    return fraseLibre() || frases()[estado.indice];
  }

  // ——— progreso ———

  async function cargarGuardadas() {
    estado.guardadas = new Map();
    try {
      const filas = await (await fetch("/api/filas")).json();
      filas
        .filter(
          (fila) =>
            (fila.persona || "").trim().toLowerCase() === estado.persona.toLowerCase() &&
            (fila.variedad || "costeno") === estado.variedad
        )
        .forEach((fila) => estado.guardadas.set(fila.guion, fila.correcta));
    } catch {
      /* Sin progreso previo: se empieza de cero. */
    }
  }

  function siguientePendiente(desde) {
    const lista = frases();
    for (let paso = 0; paso < lista.length; paso++) {
      const k = (desde + paso) % lista.length;
      if (!estado.guardadas.has(lista[k])) return k;
    }
    return -1;
  }

  function pintarProgreso() {
    const lista = frases();
    const hechas = lista.filter((frase) => estado.guardadas.has(frase)).length;
    const propias = estado.guardadas.size - hechas;
    $("#voz-progreso").innerHTML =
      `<strong>${hechas} de ${lista.length}</strong> frases guardadas` +
      (propias > 0 ? ` <span class="body-sm">(y ${propias} ${propias === 1 ? "propia" : "propias"})</span>` : "");
    $("#voz-lista-frases").innerHTML = lista.map((frase, k) => {
      const marca = estado.guardadas.get(frase);
      const etiqueta = marca === "si" ? "guardada, bien" : marca === "no" ? "guardada, con error" : "pendiente";
      const clase = marca ? `guardada-${marca}` : "pendiente";
      const actual = k === estado.indice ? ' aria-current="true"' : "";
      return `<li class="${clase}"${actual}><button type="button" class="enlace-boton" data-ir-frase="${k}">${escapar(frase)}</button> <span class="body-sm">(${etiqueta})</span></li>`;
    }).join("");
  }

  function pintarFrase() {
    const pal = esPalenquero();
    const libre = fraseLibre();
    const fuente = $("#voz-frase-fuente");
    $(".voz-palenquero").hidden = !pal;
    if (libre) {
      $("#voz-frase-titulo").textContent = "Frase acordada con el hablante";
      $("#voz-frase").textContent = libre;
      fuente.hidden = true;
    } else {
      $("#voz-frase-titulo").textContent = `Frase ${estado.indice + 1} de ${frases().length}`;
      $("#voz-frase").textContent = frases()[estado.indice];
      const ficha = pal ? LISTAS.palenquero[estado.indice] : null;
      fuente.hidden = !ficha;
      if (ficha) {
        fuente.innerHTML =
          `En español: «${escapar(ficha.espanol)}» · Fuente: ` +
          `<a href="${escapar(ficha.fuente.url)}" target="_blank" rel="noopener">${escapar(ficha.fuente.nombre)}</a>`;
      }
    }
    pintarProgreso();
  }

  // ——— paso 1: quién habla ———

  $("#voz-quien").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const form = ev.currentTarget;
    const persona = form.elements.persona.value.trim();
    if (!persona) return mostrarError("quien", "Escribe el nombre de quien va a hablar.");
    if (!form.elements.consentimiento.checked) {
      return mostrarError("quien", "Sin consentimiento firmado no se graba. Márcalo cuando la persona lo haya firmado.");
    }
    mostrarError("quien", "");
    estado.persona = persona;
    estado.variedad = form.elements.variedad.value;
    sessionStorage.setItem(CLAVE, JSON.stringify({ persona, variedad: estado.variedad }));
    $("#voz-persona-nombre").textContent = persona;
    $("#voz-variedad-nombre").textContent = esPalenquero() ? "palenquero" : "español costeño";
    await cargarGuardadas();
    const pendiente = siguientePendiente(0);
    estado.indice = pendiente < 0 ? 0 : pendiente;
    pintarFrase();
    irA("grabar");
    if (pendiente < 0) {
      avisarGuardado(`${persona} ya tiene las ${frases().length} frases guardadas. Puedes regrabar cualquiera desde la lista o cambiar de persona.`);
    }
    $("#boton-mic").focus();
  });

  $("#guion-palenquero").addEventListener("input", pintarFrase);

  $("#voz-cambiar").addEventListener("click", () => {
    if (estado.grabador?.state === "recording") return;
    irA("quien");
    $("#persona").focus();
  });

  raiz.addEventListener("click", (ev) => {
    const boton = ev.target.closest("[data-ir-frase]");
    if (!boton || estado.ocupado) return;
    estado.indice = Number(boton.dataset.irFrase);
    pintarFrase();
    $("#boton-mic").focus();
  });

  // ——— paso 2: grabar ———

  function pintarMic(grabando) {
    const boton = $("#boton-mic");
    boton.setAttribute("aria-pressed", grabando ? "true" : "false");
    boton.classList.toggle("grabando", grabando);
    boton.querySelector(".boton-mic-texto").textContent = grabando ? "Terminar" : "Grabar";
    raiz.classList.toggle("esta-grabando", grabando);
  }

  function arrancarReloj() {
    estado.inicio = performance.now();
    estado.hablo = false;
    estado.ultimoSonido = estado.inicio;
    const cronometro = $("#voz-cronometro");
    const nivel = $("#voz-nivel");
    const muestras = estado.analizador ? new Uint8Array(estado.analizador.fftSize) : null;
    const tic = () => {
      const ahora = performance.now();
      const s = Math.floor((ahora - estado.inicio) / 1000);
      cronometro.textContent = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
      if (estado.analizador && muestras) {
        estado.analizador.getByteTimeDomainData(muestras);
        let pico = 0;
        for (const valor of muestras) pico = Math.max(pico, Math.abs(valor - 128) / 128);
        nivel.value = Math.min(1, pico * 1.6);
        if (pico > UMBRAL_VOZ) {
          estado.hablo = true;
          estado.ultimoSonido = ahora;
        }
        if (estado.hablo && ahora - estado.ultimoSonido > SILENCIO_MS) return terminarGrabacion();
      }
      if (ahora - estado.inicio > MAXIMO_MS) return terminarGrabacion();
      estado.reloj = requestAnimationFrame(tic);
    };
    tic();
  }

  function pararReloj() {
    if (estado.reloj) cancelAnimationFrame(estado.reloj);
    estado.reloj = null;
    $("#voz-nivel").value = 0;
  }

  async function empezarGrabacion() {
    mostrarError("grabar", "");
    try {
      estado.flujo = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      return mostrarError("grabar", "El navegador no dio acceso al micrófono. Revisa el permiso del micrófono para esta página.");
    }
    try {
      estado.contextoAudio = new AudioContext();
      estado.analizador = estado.contextoAudio.createAnalyser();
      estado.analizador.fftSize = 1024;
      estado.contextoAudio.createMediaStreamSource(estado.flujo).connect(estado.analizador);
    } catch {
      estado.analizador = null;
    }
    estado.trozos = [];
    estado.grabador = new MediaRecorder(estado.flujo);
    estado.grabador.ondataavailable = (ev) => {
      if (ev.data.size) estado.trozos.push(ev.data);
    };
    estado.grabador.onstop = enviar;
    estado.grabador.start();
    pausarAudios();
    pintarMic(true);
    arrancarReloj();
    $("#voz-guardado").hidden = true;
    if (typeof setEstadoCorrida === "function") setEstadoCorrida("corriendo", "Grabando la frase…");
  }

  function terminarGrabacion() {
    if (estado.grabador?.state === "recording") estado.grabador.stop();
  }

  function soltarMicrofono() {
    pararReloj();
    estado.flujo?.getTracks().forEach((pista) => pista.stop());
    estado.flujo = null;
    estado.contextoAudio?.close().catch(() => {});
    estado.contextoAudio = null;
    estado.analizador = null;
  }

  $("#boton-mic").addEventListener("click", () => {
    if (estado.ocupado) return;
    if (estado.grabador?.state === "recording") terminarGrabacion();
    else empezarGrabacion();
  });

  document.addEventListener("keydown", (ev) => {
    if (ev.code !== "Space" || raiz.dataset.paso !== "grabar" || estado.ocupado) return;
    if (ev.target.closest("input, textarea, select, button, summary, a")) return;
    ev.preventDefault();
    $("#boton-mic").click();
  });

  function pasoProcesando(paso, texto) {
    if (typeof escenarioVozPaso === "function") escenarioVozPaso(paso, texto);
  }

  async function enviar() {
    const duracion = (performance.now() - estado.inicio) / 1000;
    const tipo = estado.grabador.mimeType;
    soltarMicrofono();
    pintarMic(false);
    if (duracion < 0.8 || !estado.trozos.length) {
      mostrarError("grabar", "La grabación duró menos de un segundo. Pulsa Grabar, di la frase completa y luego Terminar.");
      return;
    }
    const blob = new Blob(estado.trozos, { type: tipo });
    estado.ocupado = true;
    $("#boton-mic").disabled = true;
    $("#escenario-voz").hidden = false;
    pasoProcesando("transcribir", "Whisper está transcribiendo en este equipo…");
    if (typeof setEstadoCorrida === "function") setEstadoCorrida("corriendo", "Procesando la frase…");
    const b64 = await new Promise((resolver) => {
      const lector = new FileReader();
      lector.onload = () => resolver(String(lector.result).split(",")[1]);
      lector.readAsDataURL(blob);
    });
    let datos;
    try {
      const resp = await fetch("/api/voz/turno", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          demo: 1,
          persona: estado.persona,
          guion: guionActual(),
          variedad: estado.variedad,
          audio_b64: b64,
          mime: blob.type,
        }),
      });
      datos = await resp.json();
      if (!resp.ok) throw new Error(datos.error || `respuesta ${resp.status}`);
    } catch (err) {
      estado.ocupado = false;
      $("#boton-mic").disabled = false;
      $("#escenario-voz").hidden = true;
      if (typeof setEstadoCorrida === "function") setEstadoCorrida("error", "La frase no se pudo procesar.");
      return mostrarError("grabar", `No se pudo procesar la frase: ${err.message}. Vuelve a grabarla.`);
    }
    estado.ultimo = { ...datos, guion: guionActual() };
    const coincide = resaltarDiferencias(estado.ultimo.guion, datos.transcripcion).coincide;
    pasoProcesando("responder", coincide ? "Coincide con la frase: se guarda sola." : "No coincide: revisa lo que entendió.");
    if (coincide) {
      try {
        await guardarFila(estado.ultimo, estado.ultimo.guion, "si");
        trasGuardar(estado.ultimo, "si", true);
      } catch (err) {
        mostrarRevision();
        mostrarError("revisar", `No se pudo guardar sola: ${err.message}. Guárdala con los botones.`);
      }
    } else {
      mostrarRevision();
    }
    estado.ocupado = false;
    $("#boton-mic").disabled = false;
    $("#escenario-voz").hidden = true;
  }

  // ——— paso 3: revisar y guardar ———

  function actualizarSugerencia() {
    const ultimo = estado.ultimo;
    if (!ultimo) return;
    const comparacion = resaltarDiferencias($("#correcta").value, ultimo.transcripcion);
    $("#voz-sistema").innerHTML = comparacion.html;
    const sugerencia = $("#voz-sugerencia");
    if (!normalizar($("#correcta").value)) {
      sugerencia.textContent = "Escribe lo que de verdad se dijo para poder comparar.";
    } else if (comparacion.coincide) {
      sugerencia.textContent = "Coincide palabra por palabra con lo que se dijo.";
    } else {
      sugerencia.textContent = "Las palabras resaltadas no coinciden con lo que se dijo.";
    }
    raiz.querySelectorAll("[data-correcta]").forEach((boton) => {
      const sugerido = comparacion.coincide ? "si" : "no";
      boton.classList.toggle("fca-btn--secondary", boton.dataset.correcta !== sugerido);
    });
  }

  function mostrarRevision() {
    const ultimo = estado.ultimo;
    $("#correcta").value = ultimo.correctaGuardada || ultimo.guion || "";
    $("#voz-revisar-titulo").textContent = resaltarDiferencias(ultimo.guion, ultimo.transcripcion).coincide
      ? "Lo que entendió coincide con la frase"
      : "Lo que entendió no coincide con la frase";
    $("#voz-respuesta").textContent = ultimo.respuesta || "";
    $("#audio-respuesta").src = `data:audio/wav;base64,${ultimo.audio_b64}`;
    $(".voz-respuesta").open = false;
    const eco = $("#audio-eco");
    eco.hidden = !ultimo.eco_b64;
    if (ultimo.eco_b64) {
      eco.src = `data:audio/wav;base64,${ultimo.eco_b64}`;
      eco.play().catch(() => {});
    }
    const partes = [`${ultimo.segundos} s en total`];
    if (ultimo.asr_s != null) partes.push(`transcribir ${ultimo.asr_s} s · responder ${ultimo.llm_s} s · hablar ${ultimo.tts_s} s`);
    $("#voz-tiempos").textContent = partes.join(" · ");
    mostrarError("revisar", "");
    actualizarSugerencia();
    irA("revisar");
    if (typeof setEstadoCorrida === "function") setEstadoCorrida("corriendo", "Revisa la frase y guárdala.");
    $("#correcta").focus();
  }

  $("#correcta").addEventListener("input", actualizarSugerencia);

  $(".voz-respuesta").addEventListener("toggle", (ev) => {
    if (!ev.currentTarget.open) return $("#audio-respuesta").pause();
    $("#audio-eco").pause();
    $("#audio-respuesta").play().catch(() => {});
  });

  $("#voz-repetir").addEventListener("click", () => {
    estado.ultimo = null;
    pausarAudios();
    irA("grabar");
    if (typeof setEstadoCorrida === "function") setEstadoCorrida("reposo", "Frase descartada. Grábala de nuevo.");
    $("#boton-mic").focus();
  });

  function pausarAudios() {
    $("#audio-eco").pause();
    $("#audio-respuesta").pause();
  }

  function avisarGuardado(texto, conRevisar = false) {
    const aviso = $("#voz-guardado");
    aviso.textContent = texto;
    if (conRevisar) {
      const boton = document.createElement("button");
      boton.type = "button";
      boton.className = "enlace-boton";
      boton.id = "voz-revisar-ultima";
      boton.textContent = "Revisarla";
      aviso.append(" ", boton);
    }
    aviso.hidden = false;
  }

  async function guardarFila(ultimo, correcta, veredicto) {
    const resp = await fetch("/api/voz/fila", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: ultimo.id,
        persona: estado.persona,
        guion: ultimo.guion,
        variedad: estado.variedad,
        transcripcion_correcta: correcta,
        transcripcion_sistema: ultimo.transcripcion || "",
        correcta: veredicto,
        audio: ultimo.audio,
      }),
    });
    const datos = await resp.json();
    if (!resp.ok || !datos.ok) throw new Error(datos.error || `respuesta ${resp.status}`);
    ultimo.correctaGuardada = correcta;
  }

  function trasGuardar(ultimo, veredicto, automatica) {
    pausarAudios();
    estado.guardadas.set(ultimo.guion, veredicto);
    estado.ultimoGuardado = { ultimo, indice: estado.indice };
    const libre = !frases().includes(ultimo.guion);
    const cual = libre ? "acordada" : String(estado.indice + 1);
    const resultado = automatica
      ? `La frase ${cual} coincidió palabra por palabra y se guardó sola`
      : `Guardada la frase ${cual}, ${veredicto === "si" ? "sin error" : "con error de reconocimiento"}`;
    estado.ultimo = null;
    if (libre) $("#guion-palenquero").value = "";
    const siguiente = siguientePendiente(libre ? estado.indice : estado.indice + 1);
    if (siguiente < 0) {
      avisarGuardado(`${resultado}. ${estado.persona} terminó las ${frases().length} frases. Cambia de persona para seguir.`, true);
    } else {
      avisarGuardado(`${resultado}. Sigue con la frase ${siguiente + 1}.`, true);
      estado.indice = siguiente;
    }
    pintarFrase();
    irA("grabar");
    if (typeof setEstadoCorrida === "function") setEstadoCorrida("ok", "Frase guardada en el informe.");
    if (typeof mostrarUltimoResultado === "function") mostrarUltimoResultado(1);
    $("#boton-mic").focus();
  }

  raiz.querySelectorAll("[data-correcta]").forEach((boton) => {
    boton.addEventListener("click", async () => {
      const ultimo = estado.ultimo;
      const correcta = $("#correcta").value.trim();
      if (!ultimo) return;
      if (!correcta) return mostrarError("revisar", "Escribe lo que de verdad se dijo antes de guardar.");
      raiz.querySelectorAll("[data-correcta]").forEach((b) => (b.disabled = true));
      try {
        await guardarFila(ultimo, correcta, boton.dataset.correcta);
      } catch (err) {
        mostrarError("revisar", `No se guardó: ${err.message}. Inténtalo otra vez.`);
        return;
      } finally {
        raiz.querySelectorAll("[data-correcta]").forEach((b) => (b.disabled = false));
      }
      trasGuardar(ultimo, boton.dataset.correcta, false);
    });
  });

  raiz.addEventListener("click", (ev) => {
    if (!ev.target.closest("#voz-revisar-ultima") || !estado.ultimoGuardado || estado.ocupado) return;
    estado.ultimo = estado.ultimoGuardado.ultimo;
    estado.indice = estado.ultimoGuardado.indice;
    $("#voz-guardado").hidden = true;
    pintarFrase();
    mostrarRevision();
  });

  // ——— arranque ———

  try {
    const previo = JSON.parse(sessionStorage.getItem(CLAVE) || "null");
    if (previo?.persona) {
      $("#persona").value = previo.persona;
      const radio = raiz.querySelector(`input[name="variedad"][value="${previo.variedad}"]`);
      if (radio) radio.checked = true;
    }
  } catch {
    /* nada guardado */
  }
  irA("quien");
})();
