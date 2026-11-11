"""Servidor único en el puerto 8765: portada, cinco demos, voz y eventos."""

from __future__ import annotations

import json
import mimetypes
import queue
import re
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from interfaz import paginas
from interfaz.catalogo import DEMOS
from interfaz.corridas import lanzar
from interfaz.demo3_calificacion import guardar_calificacion, listar_calificaciones, sincronizar_metricas
from interfaz.demo3_ciego import cargar_paquete_ciego, listar_paquetes_ciegos, resumen_calificacion_demo3
from interfaz.eventos import BUS
from interfaz.informe_export import html_imprimible, pdf_bytes
from interfaz.informes import (
    asegurar_informe_demo1,
    cargar,
    cargar_corrida,
    guardar_video_corrida,
    listar_historial,
    resumen_tarjeta,
    ruta_video_corrida,
)
from interfaz.qr import svg_de_enlace
from interfaz.red import enlace_telefono
from medicion import coincide
from voz.frases import FRASES
from voz.motor import Motor

RAIZ = Path(__file__).resolve().parents[1]
STATIC = Path(__file__).resolve().parent / "static"
PUERTO = 8765

_candado_voz = threading.Lock()
_motor: Motor | None = None
_motor_lock = threading.Lock()


def hay_internet() -> bool:
    try:
        with socket.create_connection(("1.1.1.1", 443), timeout=2):
            return True
    except OSError:
        return False


def _leer_json(path: Path, vacio):
    if not path.exists():
        return vacio
    return json.loads(path.read_text(encoding="utf-8"))


def _escribir_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporal = path.with_suffix(".tmp")
    temporal.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporal.replace(path)


def motor_listo() -> Motor:
    global _motor
    with _motor_lock:
        if _motor is None:
            _motor = Motor()
            _motor.cargar()
        return _motor


def calentar_voz() -> None:
    motor = motor_listo()
    from voz.servidor import calentar

    calentar(motor)


class Manejador(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, formato: str, *args) -> None:
        print(f"{self.address_string()} {formato % args}", flush=True)

    def do_GET(self) -> None:
        ruta = urlparse(self.path)
        path = ruta.path.rstrip("/") or "/"
        if path == "/":
            self._html(paginas.inicio())
            return
        if path == "/nota-tecnica":
            self._html(paginas.nota_tecnica())
            return
        if path == "/calificar":
            cal = RAIZ / "demo3_comparacion" / "calificar.html"
            self._enviar(200, "text/html; charset=utf-8", cal.read_bytes())
            return
        m_demo = re.fullmatch(r"/demo/(\d)", path)
        if m_demo:
            demo_id = int(m_demo.group(1))
            if demo_id in DEMOS:
                self._html(paginas.demo(demo_id))
                return
        m_imprimir = re.fullmatch(r"/demo/(\d)/informe/imprimir", path)
        if m_imprimir:
            demo_id = int(m_imprimir.group(1))
            if demo_id not in DEMOS:
                self._json(404, {"error": "no existe"})
                return
            corrida = parse_qs(ruta.query).get("corrida", [None])[0]
            informe = cargar_corrida(demo_id, corrida) if corrida else cargar(demo_id)
            if informe is None:
                self._html(
                    html_imprimible(
                        demo_id,
                        {"fecha": None, "pendiente": "Aún no hay informe medido para este demo."},
                        auto_imprimir=False,
                    ),
                    codigo=404,
                )
                return
            auto = parse_qs(ruta.query).get("auto", ["0"])[0] in ("1", "true", "sí", "si")
            self._html(html_imprimible(demo_id, informe, auto_imprimir=auto))
            return
        if path == "/voz/telefono":
            html = paginas.pagina_voz("telefono").replace('?modo=telefono', "").replace(
                'const modo = params.get("modo") || "medicion";',
                'const modo = "telefono";',
            )
            self._enviar(200, "text/html; charset=utf-8", html.encode("utf-8"))
            return
        if path == "/voz/sala":
            html = paginas.pagina_voz("sala").replace(
                'const modo = params.get("modo") || "medicion";',
                'const modo = "sala";',
            )
            self._enviar(200, "text/html; charset=utf-8", html.encode("utf-8"))
            return
        if path.startswith("/static/"):
            archivo = STATIC / path.removeprefix("/static/")
            if archivo.is_file():
                tipo = mimetypes.guess_type(str(archivo))[0] or "application/octet-stream"
                self._enviar(200, tipo, archivo.read_bytes())
                return
        if path in ("/api/demo3/paquetes-ciegos", "/api/demos/3/paquetes-ciegos"):
            self._json(200, resumen_calificacion_demo3())
            return
        if path in ("/api/demo3/calificaciones", "/api/demos/3/calificaciones"):
            self._json(200, {"calificaciones": listar_calificaciones()})
            return
        if path in ("/api/demo3/calificacion", "/api/demos/3/calificacion"):
            self._json(200, {"metodo": "POST", "envio_laboratorio": True})
            return
        m_grab1 = re.fullmatch(r"/api/demos/1/grabacion/([^/]+)", path)
        if m_grab1:
            identificador = m_grab1.group(1)
            for extension, tipo in (
                (".webm", "video/webm"),
                (".m4a", "audio/mp4"),
                (".wav", "audio/wav"),
            ):
                archivo = RAIZ / "grabaciones" / f"{identificador}{extension}"
                if archivo.is_file():
                    datos = archivo.read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", tipo)
                    self.send_header("Content-Length", str(len(datos)))
                    self.send_header("Cache-Control", "private, max-age=3600")
                    self.end_headers()
                    self.wfile.write(datos)
                    return
            self._json(404, {"error": "audio no encontrado"})
            return
        m_ciego = re.fullmatch(r"/api/(?:demo3|demos/3)/paquetes-ciegos/([^/]+)", path)
        if m_ciego:
            datos = cargar_paquete_ciego(m_ciego.group(1))
            if datos is None:
                self._json(
                    404,
                    {
                        "error": "paquete no encontrado",
                        "ruta": str(RAIZ / "resultados" / "demo3" / "ciego.json"),
                    },
                )
            else:
                self._json(200, datos)
            return
        if path == "/api/resumen":
            datos = {str(i): resumen_tarjeta(i) for i in DEMOS}
            self._json(200, datos)
            return
        if path == "/api/red":
            self._json(200, {"internet": hay_internet()})
            return
        if path == "/api/demo2/enlace":
            consulta = parse_qs(ruta.query)
            ip = consulta.get("ip", [None])[0]
            try:
                self._json(200, enlace_telefono(PUERTO, ip_manual=ip))
            except ValueError as exc:
                self._json(400, {"error": str(exc)})
            return
        if path == "/api/demo2/qr.svg":
            consulta = parse_qs(ruta.query)
            ip = consulta.get("ip", [None])[0]
            try:
                datos = enlace_telefono(PUERTO, ip_manual=ip)
            except ValueError:
                self.send_error(400)
                return
            svg = svg_de_enlace(datos["url"])
            self._enviar(200, "image/svg+xml; charset=utf-8", svg)
            return
        if path == "/api/filas":
            self._json(200, _leer_json(RAIZ / "resultados" / "demo1" / "filas.json", []))
            return
        if path == "/api/turnos":
            demo = parse_qs(ruta.query).get("demo", ["2"])[0]
            self._json(200, self._turnos_jsonl(demo))
            return
        m_inf = re.fullmatch(r"/api/demos/(\d)/informe", path)
        if m_inf:
            demo_id = int(m_inf.group(1))
            informe = cargar(demo_id)
            if informe is None:
                self._json(404, {"error": "sin informe"})
            else:
                self._json(200, informe)
            return
        m_hist = re.fullmatch(r"/api/demos/(\d)/historial", path)
        if m_hist:
            demo_id = int(m_hist.group(1))
            if demo_id not in DEMOS:
                self._json(404, {"error": "no existe"})
                return
            self._json(200, {"corridas": listar_historial(demo_id)})
            return
        m_hist_video = re.fullmatch(r"/api/demos/(\d)/historial/([^/]+)\.webm", path)
        if m_hist_video:
            demo_id = int(m_hist_video.group(1))
            corrida_id = m_hist_video.group(2)
            if demo_id not in DEMOS:
                self._json(404, {"error": "no existe"})
                return
            archivo = ruta_video_corrida(demo_id, corrida_id)
            if not archivo.is_file():
                self._json(404, {"error": "sin video"})
                return
            datos = archivo.read_bytes()
            nombre = f'Nodo-IA-Caribe_Demo-{demo_id}_{corrida_id}.webm'
            consulta = parse_qs(urlparse(self.path).query)
            forzar_descarga = (consulta.get("download") or ["0"])[0] in ("1", "true", "sí", "si")
            self.send_response(200)
            self.send_header("Content-Type", "video/webm")
            self.send_header("Content-Length", str(len(datos)))
            self.send_header("Cache-Control", "private, max-age=3600")
            if forzar_descarga:
                self.send_header("Content-Disposition", f'attachment; filename="{nombre}"')
            self.end_headers()
            self.wfile.write(datos)
            return
        m_hist_uno = re.fullmatch(r"/api/demos/(\d)/historial/([^/]+)", path)
        if m_hist_uno:
            demo_id = int(m_hist_uno.group(1))
            corrida_id = m_hist_uno.group(2)
            if demo_id not in DEMOS:
                self._json(404, {"error": "no existe"})
                return
            informe = cargar_corrida(demo_id, corrida_id)
            if informe is None:
                self._json(404, {"error": "sin corrida"})
            else:
                self._json(200, informe)
            return
        m_pdf = re.fullmatch(r"/api/demos/(\d)/informe\.pdf", path)
        if m_pdf:
            demo_id = int(m_pdf.group(1))
            if demo_id not in DEMOS:
                self._json(404, {"error": "no existe"})
                return
            corrida = parse_qs(ruta.query).get("corrida", [None])[0]
            informe = cargar_corrida(demo_id, corrida) if corrida else cargar(demo_id)
            if informe is None:
                self._json(404, {"error": "sin informe"})
                return
            try:
                datos = pdf_bytes(demo_id, informe)
                destino = RAIZ / "resultados" / f"demo{demo_id}" / "informe.pdf"
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(datos)
            except Exception as exc:  # noqa: BLE001
                self._json(500, {"error": f"No se pudo generar el PDF: {exc}"})
                return
            nombre = f"Nodo-IA-Caribe_Demo-{demo_id}_informe.pdf"
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'attachment; filename="{nombre}"')
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)
            return
        m_evt = re.fullmatch(r"/api/demos/(\d)/eventos", path)
        if m_evt:
            demo_id = int(m_evt.group(1))
            self._sse(demo_id)
            return
        m_est = re.fullmatch(r"/api/demos/(\d)/estado", path)
        if m_est:
            demo_id = int(m_est.group(1))
            estado = BUS.de(demo_id)
            self._json(200, {"corriendo": estado.corriendo})
            return
        self._json(404, {"error": "no existe"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        try:
            cuerpo = self._cuerpo()
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
            return
        if path in ("/api/demo3/calificacion", "/api/demos/3/calificacion"):
            try:
                guardado = guardar_calificacion(cuerpo)
                metricas = sincronizar_metricas()
                from interfaz.informes import cargar

                informe = cargar(3)
            except (TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
                self._json(400, {"error": str(exc)})
                return
            except Exception as exc:  # noqa: BLE001
                self._json(500, {"error": f"No se pudo guardar la calificación: {exc}"})
                return
            self._json(
                200,
                {
                    "ok": True,
                    "archivo": guardado.name,
                    "metricas": metricas,
                    "criterio_cumplido": informe.get("criterio_cumplido") if informe else None,
                },
            )
            return
        m_correr = re.fullmatch(r"/api/demos/(\d)/correr", path)
        if m_correr:
            demo_id = int(m_correr.group(1))
            if demo_id == 1:
                self._json(200, {"sse": False, "mensaje": "Usa la grabación en esta misma página."})
                return
            if BUS.de(demo_id).corriendo:
                BUS.de(demo_id).emitir("error", "Ya hay una corrida en curso en este demo.")
                self._json(409, {"error": "Ya hay una corrida en curso."})
                return
            opciones = None
            if demo_id == 3:
                proveedor = str(cuerpo.get("proveedor") or "anthropic").strip().lower()
                if proveedor not in ("anthropic", "openai"):
                    self._json(400, {"error": "Proveedor inválido. Usa anthropic u openai."})
                    return
                opciones = {
                    "api_key": str(cuerpo.get("api_key") or "").strip(),
                    "proveedor": proveedor,
                    "modelo_referencia": str(cuerpo.get("modelo_referencia") or "").strip(),
                }
            ok = lanzar(demo_id, opciones)
            if not ok:
                BUS.de(demo_id).emitir(
                    "error",
                    "No se pudo iniciar la corrida. Revisa Ollama u otro requisito en la bitácora.",
                )
                self._json(503, {"error": "No se pudo iniciar. Revisa el avance o Ollama."})
                return
            self._json(200, {"sse": True})
            return
        if path in ("/api/voz/turno", "/api/turno"):
            try:
                self._json(200, self._turno_voz(cuerpo))
            except Exception as exc:  # noqa: BLE001
                self._json(500, {"error": str(exc)})
            return
        if path in ("/api/voz/fila", "/api/fila"):
            try:
                self._json(200, self._guardar_fila(cuerpo))
            except Exception as exc:  # noqa: BLE001
                self._json(500, {"error": str(exc)})
            return
        m_video = re.fullmatch(r"/api/demos/(\d)/corrida-video", path)
        if m_video:
            demo_id = int(m_video.group(1))
            if demo_id not in DEMOS:
                self._json(404, {"error": "no existe"})
                return
            consulta = parse_qs(urlparse(self.path).query)
            corrida_id = (consulta.get("corrida_id") or [None])[0]
            if not corrida_id:
                self._json(400, {"error": "falta corrida_id"})
                return
            try:
                datos = self._leer_binario(maximo=48_000_000)
            except ValueError as exc:
                self._json(400, {"error": str(exc)})
                return
            if len(datos) < 512:
                self._json(400, {"error": "video vacío"})
                return
            try:
                guardar_video_corrida(demo_id, corrida_id, datos)
            except ValueError as exc:
                self._json(400, {"error": str(exc)})
                return
            self._json(200, {"ok": True, "corrida_id": corrida_id})
            return
        m_leer = re.fullmatch(r"/api/demos/(\d)/explicacion-voz", path)
        if m_leer:
            demo_id = int(m_leer.group(1))
            if demo_id not in DEMOS:
                self._json(404, {"error": "no existe"})
                return
            try:
                self._json(200, self._explicacion_voz(demo_id))
            except Exception as exc:  # noqa: BLE001
                self._json(500, {"error": str(exc)})
            return
        self._json(404, {"error": "no existe"})

    def _explicacion_voz(self, demo_id: int) -> dict:
        import base64

        meta = DEMOS[demo_id]
        texto = (meta.get("explicacion_simple") or meta.get("tesis") or "").strip()
        if not texto:
            raise ValueError("Este demo no tiene texto de explicación.")
        motor = motor_listo()
        with _candado_voz:
            wav, tts_s = motor.hablar_narracion(texto)
        return {
            "demo": demo_id,
            "tts_s": tts_s,
            "voz": "es_CO-narracion",
            "audio_b64": base64.b64encode(wav).decode("ascii"),
        }

    def _turno_voz(self, cuerpo: dict) -> dict:
        import base64
        import uuid
        from datetime import datetime

        from voz.servidor import GRABACIONES

        motor = motor_listo()
        import time as time_mod

        persona = (cuerpo.get("persona") or "sin-nombre").strip()
        demo = int(cuerpo.get("demo") or 1)
        identificador = uuid.uuid4().hex[:12]
        inicio = time_mod.perf_counter()
        if cuerpo.get("audio_b64"):
            mime = cuerpo.get("mime") or "audio/webm"
            extension = ".m4a" if "mp4" in mime or "m4a" in mime else ".webm"
            GRABACIONES.mkdir(parents=True, exist_ok=True)
            origen = GRABACIONES / f"{identificador}{extension}"
            origen.write_bytes(base64.b64decode(cuerpo["audio_b64"]))
            transcripcion, asr_s = motor.transcribir(origen, idioma="es")
            entrada = "voz"
            audio_guardado = str(origen)
        elif cuerpo.get("texto"):
            transcripcion = str(cuerpo["texto"]).strip()
            asr_s = 0.0
            entrada = "texto"
            audio_guardado = ""
        else:
            raise ValueError("falta audio o texto")
        respuesta, llm_s = motor.responder(transcripcion or cuerpo.get("guion") or "Buenas.")
        wav, tts_s = motor.hablar(respuesta or "No te entendí.")
        segundos = round(time_mod.perf_counter() - inicio, 3)
        fila = {
            "id": identificador,
            "demo": demo,
            "persona": persona,
            "guion": cuerpo.get("guion") or "",
            "entrada": entrada,
            "transcripcion": transcripcion,
            "respuesta": respuesta,
            "segundos": segundos,
            "asr_s": asr_s,
            "llm_s": llm_s,
            "tts_s": tts_s,
            "audio": audio_guardado,
            "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        destino = RAIZ / "resultados" / ("demo1" if demo == 1 else "demo2")
        destino.mkdir(parents=True, exist_ok=True)
        with _candado_voz:
            with (destino / "turnos.jsonl").open("a", encoding="utf-8") as archivo:
                archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
        fila["audio_b64"] = base64.b64encode(wav).decode("ascii")
        return fila

    def _guardar_fila(self, cuerpo: dict) -> dict:
        necesaria = ("id", "persona", "transcripcion_correcta", "transcripcion_sistema", "correcta")
        if any(not str(cuerpo.get(campo, "")).strip() for campo in necesaria):
            raise ValueError("fila incompleta")
        fila = {
            "id": cuerpo["id"],
            "persona": cuerpo["persona"].strip(),
            "guion": cuerpo.get("guion") or "",
            "transcripcion_correcta": cuerpo["transcripcion_correcta"].strip(),
            "transcripcion_sistema": cuerpo["transcripcion_sistema"].strip(),
            "correcta": cuerpo["correcta"],
            "correcta_automatica": "si"
            if coincide(cuerpo["transcripcion_correcta"], cuerpo["transcripcion_sistema"])
            else "no",
            "audio": cuerpo.get("audio") or "",
        }
        path = RAIZ / "resultados" / "demo1" / "filas.json"
        with _candado_voz:
            filas = _leer_json(path, [])
            filas = [f for f in filas if f.get("id") != fila["id"]]
            filas.append(fila)
            _escribir_json(path, filas)
            asegurar_informe_demo1(filas)
        return {"ok": True, "filas": len(filas)}

    def _sse(self, demo_id: int) -> None:
        estado = BUS.de(demo_id)
        cola = estado.suscribir()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        try:
            while True:
                try:
                    linea = cola.get(timeout=25)
                    self.wfile.write(linea.encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(": ping\n\n".encode("utf-8"))
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            estado.desuscribir(cola)

    def _cuerpo(self) -> dict:
        largo = int(self.headers.get("Content-Length", "0"))
        if largo > 12_000_000:
            raise ValueError("cuerpo demasiado grande")
        crudo = self.rfile.read(largo) if largo else b"{}"
        return json.loads(crudo.decode("utf-8"))

    def _leer_binario(self, maximo: int = 48_000_000) -> bytes:
        largo = int(self.headers.get("Content-Length", "0"))
        if largo > maximo:
            raise ValueError("cuerpo demasiado grande")
        return self.rfile.read(largo) if largo else b""

    def _json(self, codigo: int, data: dict) -> None:
        self._enviar(codigo, "application/json; charset=utf-8", json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _html(self, texto: str, codigo: int = 200) -> None:
        self._enviar(codigo, "text/html; charset=utf-8", texto.encode("utf-8"))

    def _enviar(self, codigo: int, tipo: str, datos: bytes) -> None:
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def _turnos_jsonl(self, demo: str) -> list:
        path = RAIZ / "resultados" / ("demo1" if demo == "1" else "demo2") / "turnos.jsonl"
        if not path.exists():
            return []
        filas = []
        for linea in path.read_text(encoding="utf-8").splitlines():
            if linea.strip():
                fila = json.loads(linea)
                fila.pop("audio_b64", None)
                filas.append(fila)
        return filas


def main() -> None:
    threading.Thread(target=calentar_voz, daemon=True).start()
    servidor = ThreadingHTTPServer(("0.0.0.0", PUERTO), Manejador)
    print(f"Nodo IA Caribe · interfaz en http://127.0.0.1:{PUERTO}/", flush=True)
    servidor.serve_forever()


if __name__ == "__main__":
    main()
