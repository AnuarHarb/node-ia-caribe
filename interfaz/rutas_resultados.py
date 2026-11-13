"""Dónde leer y escribir mediciones.

- `resultados/` queda en el equipo: voz, historial completo, calificaciones, etc. No se sube al repo.
- `ejemplo/resultados/` es la medición base en el clon (generada con `python -m ejemplo.generar`; ver `/medicion-base`).
"""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MEDIDOS = RAIZ / "resultados"
PUBLICO = RAIZ / "ejemplo" / "resultados"

_MARCADORES: dict[int, tuple[str, ...]] = {
    1: ("filas.json", "turnos.jsonl"),
    2: ("turnos.jsonl",),
    3: ("generaciones.json", "informe.json"),
    4: ("informe.json",),
    5: ("informe.json", "pruebas.csv"),
}


def usa_medicion_local(demo_id: int) -> bool:
    """True si hay datos medidos en `resultados/demoN/` (no solo la carpeta vacía)."""
    carpeta = MEDIDOS / f"demo{demo_id}"
    if not carpeta.is_dir():
        return False
    return any((carpeta / nombre).is_file() for nombre in _MARCADORES.get(demo_id, ()))


def carpeta_demo(demo_id: int) -> Path:
    """Carpeta de lectura del demo: local si existe medición; si no, el juego de ejemplo."""
    if usa_medicion_local(demo_id):
        return MEDIDOS / f"demo{demo_id}"
    return PUBLICO / f"demo{demo_id}"


def carpeta_escritura(demo_id: int) -> Path:
    """Siempre escribe mediciones nuevas en `resultados/`."""
    return MEDIDOS / f"demo{demo_id}"


def traduccion_publica() -> Path | None:
    for ruta in (MEDIDOS / "demo4" / "traduccion.json", PUBLICO / "demo4" / "traduccion.json"):
        if ruta.is_file():
            return ruta
    return None
