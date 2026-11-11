"""Reconocimiento, respuesta y síntesis en un solo equipo.

Whisper small corre con MLX. El modelo de lenguaje es el de Ollama.
Piper habla la respuesta. Las tres piezas se cargan cuando hace falta.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import threading
import time
import wave
from pathlib import Path

import httpx

RAIZ = Path(__file__).resolve().parents[1]
MODELOS = RAIZ / "models"
WHISPER_REPO = os.environ.get("WHISPER_REPO", "mlx-community/whisper-small-mlx")
OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
MODELO_LOCAL = os.environ.get("MODELO_LOCAL", "qwen2.5:3b")

PIPER_MAIN = "https://huggingface.co/rhasspy/piper-voices/resolve/main"

VOZ_ASISTENTE_ONNX = MODELOS / "es_MX-ald-medium.onnx"
VOZ_ASISTENTE_JSON = MODELOS / "es_MX-ald-medium.onnx.json"
VOZ_ASISTENTE_URL = f"{PIPER_MAIN}/es/es_MX/ald/medium/es_MX-ald-medium.onnx"

# Piper no publica es_CO: guardamos como es_CO-narracion.onnx.
# Por defecto: es_MX-claude-high (única voz high latina en el catálogo Piper sin usar la argentina).
# Modelo colombiano propio: reemplaza el .onnx en models/ o define PIPER_NARRACION_URL.
VOZ_NARRACION_ONNX = MODELOS / os.environ.get("PIPER_NARRACION", "es_CO-narracion.onnx")
VOZ_NARRACION_JSON = VOZ_NARRACION_ONNX.with_suffix(".onnx.json")
_narracion_rel = os.environ.get(
    "PIPER_NARRACION_PATH",
    "es/es_MX/claude/high/es_MX-claude-high",
)
VOZ_NARRACION_URL = os.environ.get(
    "PIPER_NARRACION_URL",
    f"{PIPER_MAIN}/{_narracion_rel}.onnx",
)

SISTEMA_VOZ = (
    "Eres la voz de una ventanilla de una alcaldía del Caribe colombiano, en una prueba de laboratorio. "
    "Responde en una o dos frases cortas, en español sencillo. "
    "Si no tienes el dato, dilo y pide uno. No inventes números de radicado ni horarios."
)


def _bajar(url: str, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(destino.suffix + ".parcial")
    with httpx.stream("GET", url, follow_redirects=True, timeout=300) as respuesta:
        respuesta.raise_for_status()
        with temporal.open("wb") as archivo:
            for bloque in respuesta.iter_bytes():
                archivo.write(bloque)
    temporal.replace(destino)


def _compat_voz(path: Path) -> None:
    """Las voces publicadas en 1.0 traen el tipo como 'PhonemeType.ESPEAK'. Piper 1.8 espera 'espeak'."""
    datos = json.loads(path.read_text(encoding="utf-8"))
    tipo = datos.get("phoneme_type")
    if isinstance(tipo, str) and tipo.startswith("PhonemeType."):
        datos["phoneme_type"] = tipo.split(".", 1)[1].lower()
        path.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def asegurar_voz(onnx: Path, json_path: Path, url_onnx: str) -> Path:
    if not onnx.exists():
        _bajar(url_onnx, onnx)
    if not json_path.exists():
        _bajar(url_onnx + ".json", json_path)
    _compat_voz(json_path)
    return onnx


def asegurar_piper() -> Path:
    return asegurar_voz(VOZ_ASISTENTE_ONNX, VOZ_ASISTENTE_JSON, VOZ_ASISTENTE_URL)


def asegurar_piper_narracion() -> Path:
    return asegurar_voz(VOZ_NARRACION_ONNX, VOZ_NARRACION_JSON, VOZ_NARRACION_URL)


def _cargar_piper(onnx: Path, json_path: Path):
    try:
        from piper.voice import PiperVoice
    except ImportError:
        from piper import PiperVoice
    return PiperVoice.load(str(onnx), config_path=str(json_path))


def a_wav(origen: Path) -> Path:
    destino = Path(tempfile.mkstemp(suffix=".wav")[1])
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(origen), "-ac", "1", "-ar", "16000", str(destino)],
        check=True,
        capture_output=True,
    )
    return destino


def partir_texto_narracion(texto: str, max_chars: int = 420) -> list[str]:
    """Trocea por frases para que Piper no se apresure en párrafos largos."""
    texto = re.sub(r"\s+", " ", texto.strip())
    if not texto:
        return []
    if len(texto) <= max_chars:
        return [texto]
    partes = re.split(r"(?<=[.!?])\s+", texto)
    bloques: list[str] = []
    actual = ""
    for parte in partes:
        cand = f"{actual} {parte}".strip() if actual else parte
        if len(cand) <= max_chars:
            actual = cand
        else:
            if actual:
                bloques.append(actual)
            actual = parte
    if actual:
        bloques.append(actual)
    return bloques or [texto]


def _unir_wavs(rutas: list[Path]) -> bytes:
    if not rutas:
        return b""
    if len(rutas) == 1:
        return rutas[0].read_bytes()
    salida = Path(tempfile.mkstemp(suffix=".wav")[1])
    try:
        params = None
        frames: list[bytes] = []
        for ruta in rutas:
            with wave.open(str(ruta), "rb") as entrada:
                if params is None:
                    params = entrada.getparams()
                elif entrada.getparams()[:3] != params[:3]:
                    raise ValueError("Parámetros WAV distintos al unir narración")
                frames.append(entrada.readframes(entrada.getnframes()))
        with wave.open(str(salida), "wb") as salida_wav:
            salida_wav.setparams(params)
            for bloque in frames:
                salida_wav.writeframes(bloque)
        return salida.read_bytes()
    finally:
        salida.unlink(missing_ok=True)


class Motor:
    def __init__(self) -> None:
        self.modelo_local = MODELO_LOCAL
        self.whisper_repo = WHISPER_REPO
        self._asr = threading.Lock()
        self._tts = threading.Lock()
        self._piper = None
        self._piper_narracion = None
        self._whisper = None

    def describir(self) -> dict:
        return {
            "whisper": self.whisper_repo,
            "lenguaje_whisper_en_el_asistente": "es",
            "ollama": self.modelo_local,
            "piper_asistente": VOZ_ASISTENTE_ONNX.name if VOZ_ASISTENTE_ONNX.exists() else "sin descargar",
            "piper_narracion": VOZ_NARRACION_ONNX.name if VOZ_NARRACION_ONNX.exists() else "bajo demanda",
        }

    def cargar(self, piper: bool = True) -> None:
        import mlx_whisper

        self._whisper = mlx_whisper
        if not piper:
            return
        asegurar_piper()
        self._piper = _cargar_piper(VOZ_ASISTENTE_ONNX, VOZ_ASISTENTE_JSON)

    def _asegurar_narracion(self) -> None:
        if self._piper_narracion is not None:
            return
        asegurar_piper_narracion()
        self._piper_narracion = _cargar_piper(VOZ_NARRACION_ONNX, VOZ_NARRACION_JSON)

    def transcribir(self, audio: Path, idioma: str | None = "es") -> tuple[str, float]:
        wav = a_wav(audio)
        try:
            with self._asr:
                inicio = time.perf_counter()
                resultado = self._whisper.transcribe(
                    str(wav),
                    path_or_hf_repo=self.whisper_repo,
                    language=idioma,
                    verbose=False,
                )
                segundos = time.perf_counter() - inicio
            return (resultado.get("text") or "").strip(), round(segundos, 3)
        finally:
            wav.unlink(missing_ok=True)

    def responder(self, texto: str, sistema: str = SISTEMA_VOZ, max_tokens: int = 120) -> tuple[str, float]:
        inicio = time.perf_counter()
        respuesta = httpx.post(
            f"{OLLAMA}/api/chat",
            json={
                "model": self.modelo_local,
                "stream": False,
                "messages": [
                    {"role": "system", "content": sistema},
                    {"role": "user", "content": texto},
                ],
                "options": {"temperature": 0.2, "num_predict": max_tokens},
            },
            timeout=180,
        )
        respuesta.raise_for_status()
        contenido = ((respuesta.json().get("message") or {}).get("content") or "").strip()
        return contenido, round(time.perf_counter() - inicio, 3)

    def hablar(self, texto: str) -> tuple[bytes, float]:
        with self._tts:
            inicio = time.perf_counter()
            destino = Path(tempfile.mkstemp(suffix=".wav")[1])
            try:
                self._escribir_wav(texto, destino, self._piper)
                datos = destino.read_bytes()
            finally:
                destino.unlink(missing_ok=True)
            return datos, round(time.perf_counter() - inicio, 3)

    def hablar_narracion(self, texto: str) -> tuple[bytes, float]:
        with self._tts:
            inicio = time.perf_counter()
            self._asegurar_narracion()
            voz = self._piper_narracion
            if voz is None:
                raise RuntimeError("Voz de narración no disponible")
            partes = partir_texto_narracion(texto)
            temporales: list[Path] = []
            try:
                for parte in partes:
                    destino = Path(tempfile.mkstemp(suffix=".wav")[1])
                    self._escribir_wav(parte, destino, voz)
                    temporales.append(destino)
                datos = _unir_wavs(temporales)
            finally:
                for t in temporales:
                    t.unlink(missing_ok=True)
            return datos, round(time.perf_counter() - inicio, 3)

    def _escribir_wav(self, texto: str, destino: Path, voz) -> None:
        if voz is None:
            raise RuntimeError("Piper no está cargado")
        if hasattr(voz, "synthesize_wav"):
            with wave.open(str(destino), "wb") as archivo:
                voz.synthesize_wav(texto, archivo)
            return
        with wave.open(str(destino), "wb") as archivo:
            voz.synthesize(texto, archivo)
