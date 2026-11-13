/* Graba pantalla (y audio de pestaña o sistema si el navegador lo ofrece) para el video de entrega. */

(function () {
  function tipoMimeVideo() {
    const candidatos = [
      "video/webm;codecs=vp9,opus",
      "video/webm;codecs=vp8,opus",
      "video/webm",
    ];
    return candidatos.find((tipo) => typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported(tipo));
  }

  function formatearBytes(bytes) {
    if (!Number.isFinite(bytes)) return "";
    if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  class GrabacionPantalla {
    constructor(demoId, elementos) {
      this.demoId = demoId;
      this.btnIniciar = elementos.iniciar;
      this.btnDetener = elementos.detener;
      this.estado = elementos.estado;
      this.lista = elementos.lista;
      this.stream = null;
      this.recorder = null;
      this.chunks = [];
      this.mime = tipoMimeVideo() || "video/webm";
    }

    soportado() {
      return typeof navigator !== "undefined" && navigator.mediaDevices?.getDisplayMedia && typeof MediaRecorder !== "undefined";
    }

    setEstado(texto, esError) {
      if (!this.estado) return;
      this.estado.textContent = texto;
      this.estado.classList.toggle("error-texto", Boolean(esError));
    }

    async refrescarLista() {
      if (!this.lista) return;
      try {
        const resp = await fetch(`/api/demos/${this.demoId}/videos-entrega`);
        const datos = await resp.json();
        const videos = datos.videos || [];
        if (!videos.length) {
          this.lista.innerHTML = "<li>Todavía no hay grabaciones guardadas en este equipo.</li>";
          return;
        }
        this.lista.innerHTML = videos
          .map(
            (v) =>
              `<li><a href="${v.url}" download="${v.nombre}">${v.nombre}</a> <span class="body-sm">(${formatearBytes(v.bytes)})</span></li>`
          )
          .join("");
      } catch {
        this.lista.innerHTML = "<li>No se pudo cargar la lista de videos.</li>";
      }
    }

    _pararPistas() {
      this.stream?.getTracks().forEach((pista) => pista.stop());
      this.stream = null;
    }

    async iniciar() {
      if (!this.soportado()) {
        this.setEstado("Este navegador no puede grabar pantalla. Usa Chrome o Edge en este mismo equipo.", true);
        return;
      }
      try {
        this.stream = await navigator.mediaDevices.getDisplayMedia({
          video: { frameRate: { ideal: 30, max: 30 } },
          audio: true,
        });
      } catch (err) {
        if (err?.name === "NotAllowedError") {
          this.setEstado("No diste permiso o cancelaste la ventana de compartir pantalla.", true);
        } else {
          this.setEstado(`No se pudo iniciar: ${err?.message || err}`, true);
        }
        return;
      }

      this.chunks = [];
      this.recorder = new MediaRecorder(this.stream, { mimeType: this.mime });
      this.recorder.ondataavailable = (ev) => {
        if (ev.data?.size) this.chunks.push(ev.data);
      };

      const videoTrack = this.stream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.onended = () => {
          if (this.recorder?.state === "recording") this.detenerYGuardar();
        };
      }

      this.recorder.start(1000);
      this.btnIniciar.disabled = true;
      this.btnDetener.disabled = false;
      this.setEstado(
        "Grabando… Comparte la pantalla o la ventana donde corre el demo. Cuando termines (2 a 3 min), pulsa «Detener y guardar».",
        false
      );
    }

    async detenerYGuardar() {
      if (!this.recorder || this.recorder.state === "inactive") {
        this.setEstado("No hay ninguna grabación en curso.", true);
        return;
      }
      this.btnDetener.disabled = true;
      this.setEstado("Guardando en el equipo…", false);

      const blob = await new Promise((resolve) => {
        this.recorder.onstop = () => resolve(new Blob(this.chunks, { type: this.mime }));
        try {
          this.recorder.stop();
        } catch {
          resolve(null);
        }
      });
      this._pararPistas();
      this.recorder = null;
      this.btnIniciar.disabled = false;

      if (!blob || blob.size < 4096) {
        this.setEstado("La grabación quedó vacía. Vuelve a intentar y deja grabar al menos unos segundos.", true);
        return;
      }

      try {
        const resp = await fetch(`/api/demos/${this.demoId}/videos-entrega`, {
          method: "POST",
          headers: { "Content-Type": "video/webm" },
          body: blob,
        });
        const datos = await resp.json();
        if (!resp.ok) throw new Error(datos.error || `respuesta ${resp.status}`);
        this.setEstado(
          `Listo: ${datos.nombre} (${formatearBytes(datos.bytes)}). Descárgalo abajo y súbelo como no listado; luego pega el enlace en entregables/enlaces.json.`,
          false
        );
        await this.refrescarLista();
      } catch (err) {
        this.setEstado(`No se guardó: ${err.message}`, true);
      }
    }
  }

  function init() {
    const demoId = Number(document.body.dataset.demo);
    const panel = document.getElementById("grabacion-pantalla");
    if (!demoId || !panel) return;

    const grabador = new GrabacionPantalla(demoId, {
      iniciar: document.getElementById("btn-video-iniciar"),
      detener: document.getElementById("btn-video-detener"),
      estado: document.getElementById("video-entrega-estado"),
      lista: document.getElementById("video-entrega-lista"),
    });

    document.getElementById("btn-video-iniciar")?.addEventListener("click", () => grabador.iniciar());
    document.getElementById("btn-video-detener")?.addEventListener("click", () => grabador.detenerYGuardar());
    grabador.refrescarLista();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
