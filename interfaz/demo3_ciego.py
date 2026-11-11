"""Paquetes ciegos del demo 3 disponibles para calificar."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DEMO3 = RAIZ / "resultados" / "demo3"
HISTORIAL = DEMO3 / "historial"


def _leer_ciego(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not data.get("tareas"):
        return None
    return data


def _metadatos_paquete(ciego: dict, paquete_id: str, etiqueta_base: str) -> dict:
    estado_path = DEMO3 / "estado.json"
    estado = json.loads(estado_path.read_text(encoding="utf-8")) if estado_path.is_file() else {}
    tareas = ciego.get("tareas") or []
    return {
        "id": paquete_id,
        "paquete": ciego.get("paquete") or "",
        "etiqueta": etiqueta_base,
        "tareas": len(tareas),
        "fecha": estado.get("actualizado"),
        "modelo_local": estado.get("modelo_local"),
        "modelo_referencia": estado.get("modelo_referencia"),
        "proveedor_referencia": estado.get("proveedor_referencia"),
    }


def _sembrar_ciegos_en_historial() -> None:
    """Copia ciego.json al historial si la corrida lo generó y aún no tiene copia."""
    principal = DEMO3 / "ciego.json"
    if not principal.is_file() or not HISTORIAL.is_dir():
        return
    for snap in HISTORIAL.glob("*.json"):
        if snap.name == "indice.json":
            continue
        destino = snap.with_suffix(".ciego.json")
        if destino.is_file():
            continue
        try:
            datos = json.loads(snap.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if datos.get("comparacion_completa") or datos.get("demo") == 3 and datos.get("tareas_referencia", 0) >= 40:
            shutil.copy2(principal, destino)


def falta_calificacion_ciega() -> bool:
    if not (DEMO3 / "ciego.json").is_file():
        return False
    metricas = DEMO3 / "metricas.json"
    if not metricas.is_file():
        return True
    data = json.loads(metricas.read_text(encoding="utf-8"))
    return data.get("estado") != "calculado"


def resumen_calificacion_demo3() -> dict:
    paquetes = listar_paquetes_ciegos()
    return {
        "paquetes": paquetes,
        "falta_calificacion": falta_calificacion_ciega() if paquetes else False,
        "ruta": str(DEMO3 / "ciego.json"),
    }


def listar_paquetes_ciegos() -> list[dict]:
    _sembrar_ciegos_en_historial()
    paquetes: list[dict] = []
    vistos: set[str] = set()

    principal = _leer_ciego(DEMO3 / "ciego.json")
    if principal:
        h = principal.get("paquete") or "actual"
        estado_path = DEMO3 / "estado.json"
        estado = json.loads(estado_path.read_text(encoding="utf-8")) if estado_path.is_file() else {}
        etiqueta = (
            f"Paquete actual · {len(principal['tareas'])} tareas · "
            f"{estado.get('modelo_local', 'local')} vs {estado.get('modelo_referencia', 'referencia')}"
        )
        paquetes.append(_metadatos_paquete(principal, "actual", etiqueta))
        vistos.add(h)

    if HISTORIAL.is_dir():
        for path in sorted(HISTORIAL.glob("*.ciego.json"), reverse=True):
            ciego = _leer_ciego(path)
            if not ciego:
                continue
            h = ciego.get("paquete") or ""
            if h and h in vistos:
                continue
            corrida_id = path.name[: -len(".ciego.json")]
            etiqueta = f"Corrida {corrida_id} · {len(ciego['tareas'])} tareas"
            paquetes.append(_metadatos_paquete(ciego, corrida_id, etiqueta))
            if h:
                vistos.add(h)

    return paquetes


def cargar_paquete_ciego(paquete_id: str) -> dict | None:
    if paquete_id == "actual":
        return _leer_ciego(DEMO3 / "ciego.json")
    ruta_hist = HISTORIAL / f"{paquete_id}.ciego.json"
    if ruta_hist.is_file():
        return _leer_ciego(ruta_hist)
    if (HISTORIAL / f"{paquete_id}.json").is_file() and (DEMO3 / "ciego.json").is_file():
        return _leer_ciego(DEMO3 / "ciego.json")
    return None
