/* Graba la pestaña Experimento mientras corre una corrida y sube el .webm al historial. */

(function () {
  const FPS = 2;
  const INTERVALO_MS = 1000 / FPS;

  function tipoMime() {
    const candidatos = ["video/webm;codecs=vp9", "video/webm;codecs=vp8", "video/webm"];
    return candidatos.find((tipo) => MediaRecorder.isTypeSupported(tipo)) || "video/webm";
  }

  async function cargarHtml2Canvas() {
    if (window.html2canvas) return window.html2canvas;
    await new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js";
      script.async = true;
      script.onload = resolve;
      script.onerror = () => reject(new Error("No se pudo cargar html2canvas"));
      document.head.appendChild(script);
    });
    return window.html2canvas;
  }

  class CorridaVideo {
    constructor(demoId) {
      this.demoId = demoId;
      this.canvas = document.createElement("canvas");
      this.canvas.width = 1280;
      this.canvas.height = 720;
      this.ctx = this.canvas.getContext("2d");
      this.chunks = [];
      this.recorder = null;
      this.activo = false;
      this.temporizador = null;
      this.h2c = null;
      this.soportado =
        typeof MediaRecorder !== "undefined" && typeof HTMLCanvasElement !== "undefined";
    }

    async iniciar() {
      if (!this.soportado) return false;
      try {
        this.h2c = await cargarHtml2Canvas();
      } catch {
        return false;
      }
      const stream = this.canvas.captureStream(FPS);
      this.chunks = [];
      this.recorder = new MediaRecorder(stream, { mimeType: tipoMime() });
      this.recorder.ondataavailable = (ev) => {
        if (ev.data && ev.data.size) this.chunks.push(ev.data);
      };
      this.recorder.start(1000);
      this.activo = true;
      this._dibujarMarca("Corrida en curso…");
      this._bucle();
      return true;
    }

    _zona() {
      return document.getElementById("tab-experimento");
    }

    _dibujarMarca(pie) {
      this.ctx.fillStyle = "#0f1a1c";
      this.ctx.fillRect(0, 0, 1280, 720);
      this.ctx.fillStyle = "#e8f2f4";
      this.ctx.font = "600 28px Poppins, system-ui, sans-serif";
      this.ctx.fillText(`Demo ${this.demoId} · Nodo IA Caribe`, 48, 64);
      this.ctx.font = "400 22px Poppins, system-ui, sans-serif";
      this.ctx.fillStyle = "#b8d4da";
      const lineas = String(pie || "").split("\n").slice(0, 4);
      lineas.forEach((linea, i) => {
        this.ctx.fillText(linea.slice(0, 90), 48, 120 + i * 32);
      });
    }

    async _fotograma() {
      const zona = this._zona();
      if (!zona || !this.h2c) return;
      try {
        const shot = await this.h2c(zona, {
          scale: Math.min(1.25, 1280 / Math.max(zona.offsetWidth, 1)),
          logging: false,
          useCORS: true,
          backgroundColor: "#0f1a1c",
        });
        this.ctx.fillStyle = "#0f1a1c";
        this.ctx.fillRect(0, 0, 1280, 720);
        const ratio = Math.min(1280 / shot.width, 720 / shot.height);
        const ancho = shot.width * ratio;
        const alto = shot.height * ratio;
        this.ctx.drawImage(shot, (1280 - ancho) / 2, (720 - alto) / 2, ancho, alto);
      } catch {
        this._dibujarMarca("Capturando escena…");
      }
    }

    _bucle() {
      if (!this.activo) return;
      this._fotograma().finally(() => {
        this.temporizador = window.setTimeout(() => this._bucle(), INTERVALO_MS);
      });
    }

    onEvento(evento) {
      if (!this.activo || !evento) return;
      const pie = evento.mensaje || evento.tipo || "";
      this._dibujarMarca(pie);
    }

    async detenerYSubir(corridaId) {
      if (!this.recorder || !this.activo) return false;
      this.activo = false;
      if (this.temporizador) window.clearTimeout(this.temporizador);
      const blob = await new Promise((resolve) => {
        this.recorder.onstop = () => {
          resolve(new Blob(this.chunks, { type: tipoMime() }));
        };
        try {
          this.recorder.stop();
        } catch {
          resolve(null);
        }
      });
      if (!blob || blob.size < 2048 || !corridaId) return false;
      const url = `/api/demos/${this.demoId}/corrida-video?corrida_id=${encodeURIComponent(corridaId)}`;
      const resp = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "video/webm" },
        body: blob,
      });
      return resp.ok;
    }
  }

  window.CorridaVideo = CorridaVideo;
})();
