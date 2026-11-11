"""WER de corpus con jiwer, sobre el texto ya normalizado.

El número que se informa es el WER del corpus: ediciones totales divididas por
las palabras totales de la referencia. No es el promedio de los WER de cada frase.
"""

from __future__ import annotations

import json
from pathlib import Path

import jiwer

from medicion import normalizar

RAIZ = Path(__file__).resolve().parents[1]


def wer_corpus(referencias: list[str], hipotesis: list[str]) -> dict:
    if len(referencias) != len(hipotesis) or not referencias:
        raise ValueError("hacen falta pares de referencia e hipótesis")
    refs = [normalizar(texto) for texto in referencias]
    hyps = [normalizar(texto) for texto in hipotesis]
    if any(not texto for texto in refs):
        raise ValueError("una referencia quedó vacía después de normalizar")
    salida = jiwer.process_words(refs, hyps)
    por_frase = [
        {
            "referencia": referencia,
            "hipotesis": hipotesis,
            "wer": jiwer.wer(normalizar(referencia), normalizar(hipotesis)),
        }
        for referencia, hipotesis in zip(referencias, hipotesis)
    ]
    return {
        "frases": len(refs),
        "wer": salida.wer,
        "wer_porcentaje": round(salida.wer * 100, 2),
        "sustituciones": salida.substitutions,
        "inserciones": salida.insertions,
        "eliminaciones": salida.deletions,
        "palabras_referencia": salida.hits + salida.substitutions + salida.deletions,
        "por_frase": por_frase,
    }


def pares_de_carpeta(carpeta: Path) -> list[tuple[str, str, str]]:
    pares = []
    if not carpeta.exists():
        return pares
    for referencia in sorted(carpeta.glob("*.txt")):
        audio = None
        for extension in (".wav", ".webm", ".mp3", ".m4a", ".flac"):
            candidato = referencia.with_suffix(extension)
            if candidato.exists():
                audio = candidato
                break
        pares.append((referencia.stem, str(audio) if audio else "", referencia.read_text(encoding="utf-8")))
    return pares


def pares_demo1(path: Path) -> list[tuple[str, str, str]]:
    if not path.exists():
        return []
    filas = json.loads(path.read_text(encoding="utf-8"))
    pares = []
    for fila in filas:
        correcta = (fila.get("transcripcion_correcta") or "").strip()
        sistema = (fila.get("transcripcion_sistema") or "").strip()
        if correcta and sistema:
            pares.append((fila.get("id", ""), fila.get("audio", ""), correcta, sistema))
    return pares


def tabla(variedades: list[dict]) -> dict:
    return {
        "definicion": "WER de corpus con jiwer, tras pasar a minúsculas y quitar la puntuación.",
        "variedades": variedades,
    }
