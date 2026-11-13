"""Videos de entrega grabados desde el navegador (pantalla + audio opcional).

Se guardan en entregables/videos/ con un nombre fijo por demo. No se suben al repositorio
(.gitignore ignora *.webm).
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CARPETA = RAIZ / "entregables" / "videos"
PREFIJO = "Nodo-IA-Caribe_Demo-{demo_id}_"
MAXIMO_BYTES = 220 * 1024 * 1024  # ~2–3 min en webm suele quedar muy por debajo


def _marca() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H-%M-%S%z").replace(":", "")


def nombre_archivo(demo_id: int, marca: str | None = None) -> str:
    return f"{PREFIJO.format(demo_id=demo_id)}{marca or _marca()}.webm"


def ruta(demo_id: int, nombre: str) -> Path:
    if demo_id not in range(1, 6):
        raise ValueError("demo inválido")
    if not re.fullmatch(r"Nodo-IA-Caribe_Demo-\d_[\w\-+]+\.webm", nombre):
        raise ValueError("nombre inválido")
    if not nombre.startswith(PREFIJO.format(demo_id=demo_id)):
        raise ValueError("el archivo no corresponde a este demo")
    return CARPETA / nombre


def guardar(demo_id: int, datos: bytes) -> dict:
    if len(datos) < 4096:
        raise ValueError("el video es demasiado corto o está vacío")
    if len(datos) > MAXIMO_BYTES:
        raise ValueError(f"el video supera {MAXIMO_BYTES // (1024 * 1024)} MB")
    CARPETA.mkdir(parents=True, exist_ok=True)
    marca = _marca()
    destino = CARPETA / nombre_archivo(demo_id, marca)
    temporal = destino.with_suffix(".part")
    temporal.write_bytes(datos)
    temporal.replace(destino)
    return {
        "nombre": destino.name,
        "bytes": len(datos),
        "url": f"/api/demos/{demo_id}/videos-entrega/{destino.name}",
    }


def listar(demo_id: int) -> list[dict]:
    if demo_id not in range(1, 6):
        return []
    CARPETA.mkdir(parents=True, exist_ok=True)
    prefijo = PREFIJO.format(demo_id=demo_id)
    filas: list[dict] = []
    for archivo in sorted(CARPETA.glob(f"{prefijo}*.webm"), key=lambda p: p.stat().st_mtime, reverse=True):
        filas.append(
            {
                "nombre": archivo.name,
                "bytes": archivo.stat().st_size,
                "url": f"/api/demos/{demo_id}/videos-entrega/{archivo.name}",
            }
        )
    return filas[:20]
