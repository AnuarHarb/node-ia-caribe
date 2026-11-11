"""Normalización compartida por el sí/no del demo 1 y el WER del demo 4.

La especificación pide minúsculas y sin puntuación. Se conservan tildes y dígitos.
"""

from __future__ import annotations

import re
import unicodedata


def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.category(caracter).startswith("P")
    )
    return re.sub(r"\s+", " ", texto).strip()


def coincide(correcta: str, sistema: str) -> bool:
    izquierda = normalizar(correcta)
    derecha = normalizar(sistema)
    return bool(izquierda) and izquierda == derecha
