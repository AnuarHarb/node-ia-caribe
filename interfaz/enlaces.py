"""Enlaces de entrega (repositorio y video por demo) que no se pueden medir: los escribe una persona."""

from __future__ import annotations

import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO = RAIZ / "entregables" / "enlaces.json"
REPOSITORIO = "https://github.com/AnuarHarb/node-ia-caribe"


def _leer() -> dict:
    if not ARCHIVO.is_file():
        return {}
    try:
        datos = json.loads(ARCHIVO.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return datos if isinstance(datos, dict) else {}


def repositorio() -> str:
    return (
        os.environ.get("NODO_REPO_URL", "").strip()
        or str(_leer().get("repositorio") or "").strip()
        or REPOSITORIO
    )


def video(demo_id: int) -> str:
    """URL del video del demo, o cadena vacía si todavía no se ha subido."""
    videos = _leer().get("video")
    if not isinstance(videos, dict):
        return ""
    return str(videos.get(str(demo_id)) or "").strip()
