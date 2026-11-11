"""Servidor local de los demos 1 y 2. No depende de internet para responder."""

from __future__ import annotations

import base64
import json
import socket
import threading
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from medicion import coincide
from voz.frases import FRASES
from voz.motor import Motor
from voz.pagina import PAGINA

RAIZ = Path(__file__).resolve().parents[1]
GRABACIONES = RAIZ / "grabaciones"
DEMO1 = RAIZ / "resultados" / "demo1"
DEMO2 = RAIZ / "resultados" / "demo2"
PUERTO = 8765

_candado = threading.Lock()
_motor: Motor | None = None


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


def _anexar(path: Path, fila: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")


def nota_demo1(filas: list[dict]) -> None:
    errores = [fila for fila in filas if fila.get("correcta") == "no"]
    aciertos = [fila for fila in filas if fila.get("correcta") == "si"]
    personas = sorted({fila.get("persona", "") for fila in filas if fila.get("persona")})
    lineas = [
        "# Nota técnica · Voz en español costeño",
        "",
        f"Filas guardadas: {len(filas)}. Personas: {', '.join(personas) if personas else 'ninguna'}.",
        f"Coincidencias marcadas como sí: {len(aciertos)}. Errores reales marcados como no: {len(errores)}.",
        "",
        "El flujo cuenta como completo cuando una grabación produce transcripción, respuesta y voz.",
        "El criterio del video pide, además, al menos un error real de reconocimiento.",
        "",
        "| Persona | Transcripción correcta | Transcripción del sistema | ¿Correcta? |",
        "| --- | --- | --- | --- |",
    ]
    for fila in filas:
        lineas.append(
            f"| {fila.get('persona','')} | {fila.get('transcripcion_correcta','')} | {fila.get('transcripcion_sistema','')} | {fila.get('correcta','')} |"
        )
    if not filas:
        lineas.append("| | | | |")
        lineas += ["", "Pendiente: todavía no hay grabaciones con consentimiento."]
    elif not errores:
        lineas += ["", "Pendiente del criterio de video: en estas filas todavía no aparece un error de reconocimiento."]
    (RAIZ / "notas").mkdir(exist_ok=True)
    (RAIZ / "notas" / "Demo-1_Voz-en-espanol-costeno.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


class Manejador(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, formato: str, *args) -> None:
        print(f"{self.address_string()} {formato % args}", flush=True)

    def do_GET(self) -> None:
        ruta = urlparse(self.path)
        if ruta.path == "/":
            pagina = PAGINA.replace("FRASES_JSON", json.dumps(FRASES, ensure_ascii=False))
            self._enviar(200, "text/html; charset=utf-8", pagina.encode("utf-8"))
            return
        if ruta.path == "/api/red":
            self._json(200, {"internet": hay_internet()})
            return
        if ruta.path == "/api/filas":
            self._json(200, _leer_json(DEMO1 / "filas.json", []))
            return
        if ruta.path == "/api/turnos":
            demo = parse_qs(ruta.query).get("demo", ["2"])[0]
            self._json(200, _turnos(demo))
            return
        if ruta.path == "/api/salud":
            self._json(200, {"ok": True, "modelos": _motor.describir() if _motor else {}})
            return
        self._json(404, {"error": "no existe"})

    def do_POST(self) -> None:
        ruta = urlparse(self.path).path
        try:
            cuerpo = self._cuerpo()
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
            return
        try:
            if ruta == "/api/turno":
                self._json(200, turno(cuerpo))
                return
            if ruta == "/api/fila":
                self._json(200, guardar_fila(cuerpo))
                return
            if ruta == "/api/consumo":
                self._json(200, guardar_consumo(cuerpo))
                return
        except Exception as exc:  # noqa: BLE001 - se devuelve al cliente de la prueba
            self._json(500, {"error": str(exc)})
            return
        self._json(404, {"error": "no existe"})

    def _cuerpo(self) -> dict:
        largo = int(self.headers.get("Content-Length", "0"))
        if largo > 12_000_000:
            raise ValueError("el audio pasa de 12 MB")
        crudo = self.rfile.read(largo) if largo else b"{}"
        return json.loads(crudo.decode("utf-8"))

    def _json(self, codigo: int, data: dict | list) -> None:
        self._enviar(codigo, "application/json; charset=utf-8", json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _enviar(self, codigo: int, tipo: str, datos: bytes) -> None:
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)


def turno(cuerpo: dict) -> dict:
    if _motor is None or _motor._piper is None:
        raise RuntimeError("los modelos todavía no están cargados")
    persona = (cuerpo.get("persona") or "sin-nombre").strip()
    demo = int(cuerpo.get("demo") or 1)
    identificador = uuid.uuid4().hex[:12]
    inicio = time.perf_counter()
    if cuerpo.get("audio_b64"):
        mime = cuerpo.get("mime") or "audio/webm"
        extension = ".m4a" if "mp4" in mime or "m4a" in mime else ".webm"
        GRABACIONES.mkdir(parents=True, exist_ok=True)
        origen = GRABACIONES / f"{identificador}{extension}"
        origen.write_bytes(base64.b64decode(cuerpo["audio_b64"]))
        transcripcion, asr_s = _motor.transcribir(origen, idioma="es")
        audio_guardado = str(origen)
        entrada = "voz"
    elif cuerpo.get("texto"):
        transcripcion = str(cuerpo["texto"]).strip()
        asr_s = 0.0
        audio_guardado = ""
        entrada = "texto"
    else:
        raise ValueError("falta el audio o el texto")
    respuesta, llm_s = _motor.responder(transcripcion or cuerpo.get("guion") or "Buenas.")
    wav, tts_s = _motor.hablar(respuesta or "No te entendí. ¿Me repites la pregunta?")
    segundos = round(time.perf_counter() - inicio, 3)
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
    destino = DEMO1 if demo == 1 else DEMO2
    with _candado:
        _anexar(destino / "turnos.jsonl", fila)
    fila["audio_b64"] = base64.b64encode(wav).decode("ascii")
    return fila


def guardar_fila(cuerpo: dict) -> dict:
    necesaria = ("id", "persona", "transcripcion_correcta", "transcripcion_sistema", "correcta")
    if any(not str(cuerpo.get(campo, "")).strip() for campo in necesaria):
        raise ValueError("la fila está incompleta")
    if cuerpo["correcta"] not in {"si", "no"}:
        raise ValueError("la marca tiene que ser si o no")
    fila = {
        "id": cuerpo["id"],
        "persona": cuerpo["persona"].strip(),
        "guion": cuerpo.get("guion") or "",
        "transcripcion_correcta": cuerpo["transcripcion_correcta"].strip(),
        "transcripcion_sistema": cuerpo["transcripcion_sistema"].strip(),
        "correcta": cuerpo["correcta"],
        "correcta_automatica": "si" if coincide(cuerpo["transcripcion_correcta"], cuerpo["transcripcion_sistema"]) else "no",
        "audio": cuerpo.get("audio") or "",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    with _candado:
        filas = _leer_json(DEMO1 / "filas.json", [])
        filas = [existente for existente in filas if existente.get("id") != fila["id"]]
        filas.append(fila)
        _escribir_json(DEMO1 / "filas.json", filas)
        nota_demo1(filas)
    return {"ok": True, "filas": len(filas)}


def guardar_consumo(cuerpo: dict) -> dict:
    dato = {
        "reposo_w": cuerpo.get("reposo_w"),
        "carga_w": cuerpo.get("carga_w"),
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    with _candado:
        _escribir_json(DEMO2 / "consumo.json", dato)
    return dato


def _turnos(demo: str) -> list[dict]:
    path = (DEMO1 if demo == "1" else DEMO2) / "turnos.jsonl"
    if not path.exists():
        return []
    filas = []
    for linea in path.read_text(encoding="utf-8").splitlines():
        if not linea.strip():
            continue
        fila = json.loads(linea)
        fila.pop("audio_b64", None)
        filas.append(fila)
    return filas


def calentar(motor: Motor) -> None:
    """La primera pasada carga los pesos. No entra en los tiempos del demo."""
    wav, tts_s = motor.hablar("Buenas.")
    temporal = DEMO1 / "calentamiento.wav"
    temporal.parent.mkdir(parents=True, exist_ok=True)
    temporal.write_bytes(wav)
    _texto, asr_s = motor.transcribir(temporal, idioma="es")
    respuesta, llm_s = motor.responder("Buenas.")
    _voz, tts2_s = motor.hablar(respuesta or "Buenas.")
    temporal.unlink(missing_ok=True)
    print(
        f"Calentamiento, fuera de la medición: reconocimiento {asr_s} s, modelo {llm_s} s, voz {round(tts_s + tts2_s, 3)} s.",
        flush=True,
    )


def main() -> None:
    global _motor
    print("Cargando Whisper small, Piper y la conexión con Ollama.", flush=True)
    _motor = Motor()
    _motor.cargar()
    print(_motor.describir(), flush=True)
    calentar(_motor)
    servidor = ThreadingHTTPServer(("0.0.0.0", PUERTO), Manejador)
    print(f"Abre http://127.0.0.1:{PUERTO}/  para el demo 1", flush=True)
    print(f"Teléfono: http://<ip-de-este-equipo>:{PUERTO}/?modo=telefono", flush=True)
    print(f"Sala:     http://127.0.0.1:{PUERTO}/?modo=sala", flush=True)
    servidor.serve_forever()


if __name__ == "__main__":
    main()
