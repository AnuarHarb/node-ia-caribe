"""Corpus del demo 4 (audios + referencia) desde la interfaz."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CORPUS = RAIZ / "demo4_wer" / "corpus"


def _carpeta(variedad: str) -> Path:
    v = variedad.strip().lower()
    if v.startswith("pal"):
        return CORPUS / "palenquero"
    return CORPUS / "costeno"


def _stem_valido(stem: str) -> str:
    limpio = re.sub(r"[^a-zA-Z0-9_-]+", "", stem.strip())
    if not limpio:
        raise ValueError("id de frase inválido (usa por ejemplo 001 o P01)")
    return limpio


def listar_corpus() -> dict:
    salida: dict[str, list[dict]] = {"costeno": [], "palenquero": []}
    for clave, nombre in (("costeno", "costeno"), ("palenquero", "palenquero")):
        carpeta = CORPUS / nombre
        if not carpeta.is_dir():
            continue
        for ref in sorted(carpeta.glob("*.txt")):
            if ref.name.endswith(".hip.txt") or ref.stem.upper() in ("LEEME", "README"):
                continue
            stem = ref.stem
            audio = None
            for ext in (".wav", ".webm", ".m4a", ".mp3", ".flac"):
                cand = carpeta / f"{stem}{ext}"
                if cand.is_file():
                    audio = cand.name
                    break
            hip = carpeta / f"{stem}.hip.txt"
            salida[clave].append(
                {
                    "id": stem,
                    "referencia": ref.read_text(encoding="utf-8").strip()[:120],
                    "audio": audio,
                    "hipotesis": hip.is_file(),
                }
            )
    demo1 = RAIZ / "resultados" / "demo1" / "filas.json"
    filas_demo1 = {"costeno": 0, "palenquero": 0}
    if demo1.is_file():
        for fila in json.loads(demo1.read_text(encoding="utf-8")):
            from demo4_wer.wer import _variedad_demo1

            filas_demo1[_variedad_demo1(fila)] = filas_demo1.get(_variedad_demo1(fila), 0) + 1
    return {"carpetas": salida, "demo1_filas": filas_demo1}


def guardar_frase(variedad: str, stem: str, referencia: str, audio_b64: str, mime: str) -> Path:
    carpeta = _carpeta(variedad)
    carpeta.mkdir(parents=True, exist_ok=True)
    sid = _stem_valido(stem)
    ref = referencia.strip()
    if not ref:
        raise ValueError("falta la transcripción de referencia")
    if not audio_b64:
        raise ValueError("falta el audio")
    ext = ".webm"
    if "wav" in (mime or ""):
        ext = ".wav"
    elif "mp4" in (mime or "") or "m4a" in (mime or ""):
        ext = ".m4a"
    audio_path = carpeta / f"{sid}{ext}"
    ref_path = carpeta / f"{sid}.txt"
    audio_path.write_bytes(base64.b64decode(audio_b64))
    ref_path.write_text(ref + "\n", encoding="utf-8")
    hip = carpeta / f"{sid}.hip.txt"
    if hip.is_file():
        hip.unlink()
    return ref_path
