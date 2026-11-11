"""Calificaciones humanas del demo 3: guardar archivos y calcular métricas."""

from __future__ import annotations

import json
import re
from pathlib import Path

from demo3_comparacion.metricas import calcular

RAIZ = Path(__file__).resolve().parents[1]
DEMO3 = RAIZ / "resultados" / "demo3"
CAL_DIR = DEMO3 / "calificaciones"

_NOMBRES_PRUEBA = frozenset({"test", "prueba", "demo", "sin-nombre", "calificador", "ejemplo"})


def _slug(nombre: str) -> str:
    limpio = re.sub(r"[^a-z0-9]+", "-", nombre.strip().lower()).strip("-")
    return limpio or "calificador"


def _es_calificacion_prueba(nombre: str, archivo: str) -> bool:
    slug = _slug(nombre)
    if slug in _NOMBRES_PRUEBA or slug.startswith("test-"):
        return True
    if archivo.lower().startswith("calificacion-test"):
        return True
    return False


def _cargar_archivos_calificacion(paquete: str) -> list[dict]:
    if not CAL_DIR.is_dir():
        return []
    cargados: list[dict] = []
    for path in sorted(CAL_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("paquete") != paquete or not data.get("puntajes"):
            continue
        nombre = str(data.get("calificador") or "")
        if _es_calificacion_prueba(nombre, path.name):
            continue
        cargados.append({**data, "_archivo": path.name})
    return cargados


def _elegir_par_calificadores(cargados: list[dict]) -> list[dict]:
    """Un archivo por calificador (el más reciente); toma exactamente dos personas distintas."""
    por_persona: dict[str, dict] = {}
    for item in cargados:
        slug = _slug(str(item.get("calificador") or ""))
        previo = por_persona.get(slug)
        fecha = item.get("fecha") or ""
        if not previo or fecha > (previo.get("fecha") or ""):
            por_persona[slug] = item
    ordenados = sorted(por_persona.values(), key=lambda x: x.get("fecha") or "")
    return ordenados[:2]


def listar_calificaciones(*, incluir_prueba: bool = False) -> list[dict]:
    CAL_DIR.mkdir(parents=True, exist_ok=True)
    salida: list[dict] = []
    for path in sorted(CAL_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        nombre = str(data.get("calificador") or "")
        if not incluir_prueba and _es_calificacion_prueba(nombre, path.name):
            continue
        salida.append(
            {
                "archivo": path.name,
                "calificador": data.get("calificador", ""),
                "paquete": data.get("paquete", ""),
                "fecha": data.get("fecha"),
                "puntajes": len(data.get("puntajes") or []),
            }
        )
    return salida


def guardar_calificacion(cuerpo: dict) -> Path:
    if not isinstance(cuerpo, dict):
        raise ValueError("cuerpo JSON inválido")
    puntajes = cuerpo.get("puntajes")
    if not puntajes or not isinstance(puntajes, list):
        raise ValueError("faltan puntajes en la calificación")
    if not str(cuerpo.get("paquete") or "").strip():
        raise ValueError("falta el identificador del paquete ciego")
    nombre = str(cuerpo.get("calificador") or "sin-nombre")
    if _es_calificacion_prueba(nombre, f"calificacion-{_slug(nombre)}.json"):
        raise ValueError('usa un nombre real de calificador (no "test" ni "prueba")')
    CAL_DIR.mkdir(parents=True, exist_ok=True)
    path = CAL_DIR / f"calificacion-{_slug(nombre)}.json"
    path.write_text(json.dumps(cuerpo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _fechas_calificacion(par: list[dict]) -> dict:
    fechas = [str(item["fecha"]) for item in par if item.get("fecha")]
    if not fechas:
        return {"fechas_calificacion": [], "fecha_calificacion": None, "fecha_calificacion_inicio": None}
    fechas_ord = sorted(fechas)
    return {
        "fechas_calificacion": fechas_ord,
        "fecha_calificacion_inicio": fechas_ord[0],
        "fecha_calificacion": fechas_ord[-1],
    }


def sincronizar_metricas() -> dict | None:
    """Recalcula metricas.json si hay dos calificaciones válidas para el paquete actual."""
    clave_path = DEMO3 / "clave.json"
    if not clave_path.is_file():
        return None
    clave = json.loads(clave_path.read_text(encoding="utf-8"))
    paquete = clave.get("paquete")
    if not paquete:
        return None

    cargados = _cargar_archivos_calificacion(paquete)
    par = _elegir_par_calificadores(cargados)

    gen_path = DEMO3 / "generaciones.json"
    generaciones = json.loads(gen_path.read_text(encoding="utf-8")) if gen_path.is_file() else None

    if len(par) < 2:
        resultado = {
            "estado": "parcial" if par else "pendiente",
            "motivo": "hacen falta las dos calificaciones humanas",
            "calificadores": [item.get("calificador", "") for item in par],
            "archivos_recibidos": len(par),
            "archivos_contables": len(cargados),
            "paquete": paquete,
            **_fechas_calificacion(par),
        }
        destino = DEMO3 / "metricas.json"
        destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return resultado

    limpios = [{k: v for k, v in item.items() if not k.startswith("_")} for item in par]
    resultado = calcular(clave, limpios, generaciones)
    resultado.update(_fechas_calificacion(par))
    resultado["archivos_contables"] = len(cargados)
    resultado["archivos_usados"] = [item.get("_archivo") for item in par]
    destino = DEMO3 / "metricas.json"
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resultado
