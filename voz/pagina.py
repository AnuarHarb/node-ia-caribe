"""Página del demo 1 y del demo 2. El modo llega por la consulta de la URL."""

from __future__ import annotations

PAGINA = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Voz del nodo · medición</title>
  <link rel="stylesheet" href="/static/fca/fca-fonts.css">
  <link rel="stylesheet" href="/static/fca/FCA_Sistema-de-diseno/tokens.css">
  <link rel="stylesheet" href="/static/fca/FCA_Sistema-de-diseno/componentes/fca-componentes.css">
  <link rel="stylesheet" href="/static/app.css">
  <style>[role="status"] { min-height: 1.3em; }</style>
</head>
<body class="fca-root pagina-auxiliar">
  <header>
    <a class="brand-lockup" href="/">
      <img src="/static/fca/FCA_Sistema-de-diseno/logos/fca-lockup-color.png" width="180" height="36" alt="Fundación Código Abierto">
    </a>
    <p class="fca-kicker"><span class="fca-bars" aria-hidden="true"><i></i><i></i><i></i></span>Nodo IA Caribe</p>
    <h1 id="titulo">Voz en español costeño</h1>
    <p id="red" role="status"></p>
  </header>
  <main>
    <form id="sesion">
      <label>Nombre de quien habla
        <input id="persona" name="persona" type="text" autocomplete="name" required>
      </label>
      <label>
        <input id="consentimiento" name="consentimiento" type="checkbox" required>
        Hay consentimiento escrito de donación de voz. Se guarda y no se publica.
      </label>
    </form>

    <section id="bloque-frase" aria-labelledby="titulo-frase">
      <h2 id="titulo-frase">Frase para decir, en costeño natural</h2>
      <p id="frase"></p>
      <div class="fila-flex">
        <button type="button" class="fca-btn fca-btn--secondary" id="anterior">Frase anterior</button>
        <button type="button" class="fca-btn fca-btn--secondary" id="siguiente">Frase siguiente</button>
      </div>
    </section>

    <section id="bloque-grabar" aria-labelledby="titulo-grabar">
      <h2 id="titulo-grabar">Grabación</h2>
      <div class="fila-flex">
        <button type="button" class="fca-btn" id="grabar">Grabar</button>
        <button type="button" class="fca-btn fca-btn--secondary" id="detener" disabled>Detener y enviar</button>
      </div>
      <p id="estado" role="status"></p>
    </section>

    <section id="bloque-resultado" aria-live="polite">
      <h2>Transcripción del sistema</h2>
      <p id="transcripcion">Todavía no hay una.</p>
      <h2>Respuesta hablada</h2>
      <p id="respuesta"></p>
      <audio id="audio" controls></audio>
      <p id="tiempos"></p>
    </section>

    <form id="medicion">
      <label>Transcripción correcta, palabra por palabra
        <textarea id="correcta" name="correcta" rows="3" required></textarea>
      </label>
      <fieldset>
        <legend>¿La transcripción del sistema quedó bien?</legend>
        <label><input type="radio" name="correcta_si" value="si" required> Sí</label>
        <label><input type="radio" name="correcta_si" value="no"> No</label>
      </fieldset>
      <button type="submit" class="fca-btn">Guardar fila de medición</button>
    </form>

    <section id="sala" hidden aria-labelledby="titulo-sala">
      <h2 id="titulo-sala">Sala: consultas de todos los teléfonos</h2>
      <form id="consumo">
        <label>Consumo en reposo (W)
          <input id="reposo" name="reposo" type="number" min="0" step="0.1" inputmode="decimal">
        </label>
        <label>Consumo en carga (W)
          <input id="carga" name="carga" type="number" min="0" step="0.1" inputmode="decimal">
        </label>
        <button type="submit" class="fca-btn fca-btn--secondary">Anotar consumo</button>
      </form>
      <table>
        <caption>Tiempos de las consultas recibidas</caption>
        <thead>
          <tr><th>Quién</th><th>Transcripción</th><th>Respuesta</th><th>Segundos</th></tr>
        </thead>
        <tbody id="turnos"></tbody>
      </table>
    </section>

    <section id="tabla-demo1">
      <h2>Medición del demo 1</h2>
      <table>
        <caption>Frase dicha, transcripción correcta, transcripción del sistema y si coincidió</caption>
        <thead>
          <tr>
            <th>Persona</th>
            <th>Transcripción correcta</th>
            <th>Transcripción del sistema</th>
            <th>¿Correcta?</th>
          </tr>
        </thead>
        <tbody id="filas"></tbody>
      </table>
    </section>
  </main>
  <script>
    const params = new URLSearchParams(location.search);
    const modo = params.get("modo") || "medicion";
    const frases = FRASES_JSON;
    let indice = 0;
    let grabacion = null;
    let trozos = [];
    let ultimo = null;

    if (modo === "sala") {
      document.querySelector("#titulo").textContent = "Sala del nodo, sin internet";
      document.querySelector("#bloque-frase").hidden = true;
      document.querySelector("#bloque-grabar").hidden = true;
      document.querySelector("#bloque-resultado").hidden = true;
      document.querySelector("#medicion").hidden = true;
      document.querySelector("#tabla-demo1").hidden = true;
      document.querySelector("#sala").hidden = false;
      document.querySelector("#sesion").hidden = true;
      setInterval(cargarTurnos, 2000);
      cargarTurnos();
    }
    if (modo === "telefono") {
      document.querySelector("#titulo").textContent = "Consulta por voz";
      document.querySelector("#medicion").hidden = true;
      document.querySelector("#tabla-demo1").hidden = true;
    }

    const frase = document.querySelector("#frase");
    function mostrarFrase() { frase.textContent = frases[indice]; }
    mostrarFrase();
    document.querySelector("#anterior").addEventListener("click", () => {
      indice = (indice + frases.length - 1) % frases.length;
      mostrarFrase();
    });
    document.querySelector("#siguiente").addEventListener("click", () => {
      indice = (indice + 1) % frases.length;
      mostrarFrase();
    });

    async function red() {
      const datos = await (await fetch("/api/red")).json();
      document.querySelector("#red").textContent = datos.internet
        ? "Este equipo sí alcanza internet ahora."
        : "Este equipo no alcanza internet ahora.";
    }
    red();

    document.querySelector("#grabar").addEventListener("click", async () => {
      if (!document.querySelector("#consentimiento").checked || !document.querySelector("#persona").value.trim()) {
        if (modo !== "sala") {
          document.querySelector("#estado").textContent = "Hace falta el nombre y el consentimiento escrito.";
          return;
        }
      }
      trozos = [];
      const flujo = await navigator.mediaDevices.getUserMedia({ audio: true });
      grabacion = new MediaRecorder(flujo);
      grabacion.ondataavailable = (evento) => { if (evento.data.size) trozos.push(evento.data); };
      grabacion.onstop = enviar;
      grabacion.start();
      document.querySelector("#grabar").disabled = true;
      document.querySelector("#detener").disabled = false;
      document.querySelector("#estado").textContent = "Grabando.";
    });

    document.querySelector("#detener").addEventListener("click", () => {
      if (grabacion && grabacion.state !== "inactive") grabacion.stop();
      document.querySelector("#detener").disabled = true;
    });

    async function enviar() {
      document.querySelector("#estado").textContent = "Transcribiendo en este equipo.";
      const blob = new Blob(trozos, { type: grabacion.mimeType || "audio/webm" });
      grabacion.stream.getTracks().forEach((pista) => pista.stop());
      const audioB64 = await blobABase64(blob);
      const cuerpo = {
        demo: modo === "telefono" || modo === "sala" ? 2 : 1,
        persona: (document.querySelector("#persona").value || "sala").trim(),
        guion: frases[indice],
        audio_b64: audioB64,
        mime: blob.type
      };
      const respuesta = await fetch("/api/turno", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cuerpo)
      });
      const datos = await respuesta.json();
      document.querySelector("#grabar").disabled = false;
      if (!respuesta.ok) {
        document.querySelector("#estado").textContent = datos.error || "El turno falló.";
        return;
      }
      ultimo = datos;
      document.querySelector("#transcripcion").textContent = datos.transcripcion || "(vacía)";
      document.querySelector("#respuesta").textContent = datos.respuesta;
      document.querySelector("#tiempos").textContent = "Tiempo total " + datos.segundos + " s. Reconocimiento " + datos.asr_s + " s, modelo " + datos.llm_s + " s, voz " + datos.tts_s + " s.";
      document.querySelector("#audio").src = "data:audio/wav;base64," + datos.audio_b64;
      document.querySelector("#correcta").value = "";
      document.querySelector("#estado").textContent = "Listo.";
      if (modo !== "medicion") cargarTurnos();
    }

    function blobABase64(blob) {
      return new Promise((resolver) => {
        const lector = new FileReader();
        lector.onload = () => resolver(String(lector.result).split(",")[1]);
        lector.readAsDataURL(blob);
      });
    }

    document.querySelector("#medicion").addEventListener("submit", async (evento) => {
      evento.preventDefault();
      if (!ultimo) {
        document.querySelector("#estado").textContent = "Primero graba una frase.";
        return;
      }
      const correcta = document.querySelector("#correcta").value.trim();
      const marcada = new FormData(evento.target).get("correcta_si");
      const fila = {
        id: ultimo.id,
        persona: document.querySelector("#persona").value.trim(),
        guion: frases[indice],
        transcripcion_correcta: correcta,
        transcripcion_sistema: ultimo.transcripcion,
        correcta: marcada,
        audio: ultimo.audio
      };
      const respuesta = await fetch("/api/fila", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(fila)
      });
      if (!respuesta.ok) {
        document.querySelector("#estado").textContent = "No se guardó la fila.";
        return;
      }
      document.querySelector("#estado").textContent = "Fila guardada.";
      cargarFilas();
    });

    async function cargarFilas() {
      const filas = await (await fetch("/api/filas")).json();
      const cuerpo = document.querySelector("#filas");
      cuerpo.replaceChildren();
      for (const fila of filas) {
        const tr = document.createElement("tr");
        for (const texto of [fila.persona, fila.transcripcion_correcta, fila.transcripcion_sistema, fila.correcta]) {
          const td = document.createElement("td");
          td.textContent = texto;
          tr.append(td);
        }
        cuerpo.append(tr);
      }
    }

    async function cargarTurnos() {
      const turnos = await (await fetch("/api/turnos?demo=2")).json();
      const cuerpo = document.querySelector("#turnos");
      cuerpo.replaceChildren();
      for (const turno of turnos.slice(-12)) {
        const tr = document.createElement("tr");
        for (const texto of [turno.persona, turno.transcripcion, turno.respuesta, String(turno.segundos)]) {
          const td = document.createElement("td");
          td.textContent = texto;
          tr.append(td);
        }
        cuerpo.append(tr);
      }
    }

    document.querySelector("#consumo").addEventListener("submit", async (evento) => {
      evento.preventDefault();
      await fetch("/api/consumo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reposo_w: numero("reposo"),
          carga_w: numero("carga")
        })
      });
      document.querySelector("#estado").textContent = "Consumo anotado.";
    });

    function numero(id) {
      const valor = document.querySelector("#" + id).value;
      return valor === "" ? null : Number(valor);
    }

    if (modo === "medicion") cargarFilas();
  </script>
</body>
</html>
"""
