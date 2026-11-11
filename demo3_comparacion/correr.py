"""Corre el modelo local y, si hay con qué, la referencia externa.

Guarda cada respuesta apenas llega, para poder retomar. El paquete ciego solo se arma
cuando las dos respuestas de cada tarea existen. Sin la referencia no hay comparación:
no se inventa un segundo sistema.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections.abc import Callable
from pathlib import Path

import httpx

from demo3_comparacion.paquete import SISTEMA, construir_paquete, mensaje_de
from demo3_comparacion.tareas import TAREAS, por_id

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "resultados" / "demo3"
OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
MODELO_LOCAL = os.environ.get("MODELO_LOCAL", "qwen2.5:3b")


def _cargar(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _guardar(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporal = path.with_suffix(".tmp")
    temporal.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporal.replace(path)


def preguntar_ollama(modelo: str, usuario: str) -> tuple[str, float]:
    inicio = time.perf_counter()
    respuesta = httpx.post(
        f"{OLLAMA}/api/chat",
        json={
            "model": modelo,
            "stream": False,
            "messages": [
                {"role": "system", "content": SISTEMA},
                {"role": "user", "content": usuario},
            ],
            "options": {"temperature": 0, "seed": 7, "num_predict": 500},
        },
        timeout=180,
    )
    respuesta.raise_for_status()
    cuerpo = respuesta.json()
    texto = (cuerpo.get("message") or {}).get("content") or ""
    return texto.strip(), round(time.perf_counter() - inicio, 3)


def preguntar_anthropic(modelo: str, usuario: str, api_key: str | None = None) -> tuple[str, float, dict]:
    clave = (api_key or os.environ.get("ANTHROPIC_API_KEY", "")).strip()
    if not clave:
        raise RuntimeError("falta la API key de Anthropic")
    inicio = time.perf_counter()
    respuesta = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": clave,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": modelo,
            "max_tokens": 4096,
            "temperature": 0,
            "system": SISTEMA,
            "messages": [{"role": "user", "content": usuario}],
        },
        timeout=180,
    )
    respuesta.raise_for_status()
    cuerpo = respuesta.json()
    bloques = cuerpo.get("content") or []
    texto = next((b.get("text", "") for b in bloques if b.get("type") == "text"), "").strip()
    uso = cuerpo.get("usage") or {}
    segundos = round(time.perf_counter() - inicio, 3)
    return texto, segundos, uso


def preguntar_openai(modelo: str, usuario: str, api_key: str | None = None) -> tuple[str, float, dict]:
    clave = (api_key or os.environ.get("OPENAI_API_KEY", "")).strip()
    if not clave:
        raise RuntimeError("falta la API key de OpenAI")
    inicio = time.perf_counter()
    respuesta = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {clave}"},
        json={
            "model": modelo,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": SISTEMA},
                {"role": "user", "content": usuario},
            ],
        },
        timeout=180,
    )
    respuesta.raise_for_status()
    cuerpo = respuesta.json()
    texto = cuerpo["choices"][0]["message"]["content"].strip()
    uso = cuerpo.get("usage") or {}
    segundos = round(time.perf_counter() - inicio, 3)
    return texto, segundos, uso


def correr_referencia(
    proveedor: str,
    modelo_referencia: str,
    api_key: str,
    *,
    modelo_local: str | None = None,
    semilla: int = 20261110,
    emitir: Callable[[str, str, dict | None], None] | None = None,
) -> dict:
    """Solo la mitad comercial; exige respuestas locales ya guardadas."""
    if proveedor not in ("anthropic", "openai"):
        raise ValueError("proveedor debe ser anthropic u openai")
    clave = api_key.strip()
    if not clave:
        raise ValueError("falta la API key")
    modelo_local = modelo_local or MODELO_LOCAL
    generaciones = _cargar(SALIDA / "generaciones.json")
    tareas = por_id()
    locales = sum(1 for item in generaciones.values() if item.get("local", {}).get("texto"))
    if locales < len(TAREAS):
        raise RuntimeError(
            f"Primero corre la mitad local ({locales}/{len(TAREAS)} tareas con respuesta local)."
        )
    pendientes_ref = [t for t in TAREAS if not (generaciones.get(t["id"], {}).get("referencia") or {}).get("texto")]
    if not pendientes_ref and emitir:
        emitir(
            "aviso",
            "Las 40 respuestas de referencia ya están guardadas; no se vuelve a llamar a la API.",
        )
        for tarea in TAREAS:
            seg = (generaciones.get(tarea["id"], {}).get("referencia") or {}).get("segundos")
            emitir(
                "tarea",
                f"{tarea['id']} referencia (reutilizada{f', {seg} s' if seg is not None else ''})",
                {"id": tarea["id"], "columna": "referencia", "reutilizada": True, "segundos": seg},
            )
    for tarea in TAREAS:
        actual = generaciones.get(tarea["id"], {})
        if (actual.get("referencia") or {}).get("texto"):
            continue
        if emitir:
            emitir("paso", f"Referencia {tarea['id']}…", {"id": tarea["id"], "fase": "referencia"})
        try:
            if proveedor == "anthropic":
                texto, segundos, uso = preguntar_anthropic(modelo_referencia, mensaje_de(tarea), api_key=clave)
            else:
                texto, segundos, uso = preguntar_openai(modelo_referencia, mensaje_de(tarea), api_key=clave)
        except httpx.HTTPError as exc:
            detalle = (getattr(exc, "response", None) and exc.response.text or str(exc))[:400]
            raise RuntimeError(f"Tarea {tarea['id']} ({proveedor}): {detalle}") from exc
        actual.setdefault("local", generaciones.get(tarea["id"], {}).get("local", {}))
        actual["referencia"] = {
            "texto": texto,
            "segundos": segundos,
            "tokens": uso,
            "costo_usd": None,
            "modelo": modelo_referencia,
            "nota_costo": "Tokens guardados. El costo en dólares se calcula cuando se confirma la tarifa del día.",
        }
        generaciones[tarea["id"]] = actual
        _guardar(SALIDA / "generaciones.json", generaciones)
        if emitir:
            emitir(
                "tarea",
                f"{tarea['id']} referencia {segundos} s",
                {"id": tarea["id"], "segundos": segundos, "columna": "referencia"},
            )
    completas = {
        tarea_id: {
            "local": generaciones[tarea_id]["local"]["texto"],
            "referencia": generaciones[tarea_id]["referencia"]["texto"],
        }
        for tarea_id in tareas
        if generaciones.get(tarea_id, {}).get("local", {}).get("texto")
        and generaciones.get(tarea_id, {}).get("referencia", {}).get("texto")
    }
    meta = {
        "tareas": len(TAREAS),
        "con_respuesta_local": locales,
        "con_las_dos_respuestas": len(completas),
        "modelo_local": modelo_local,
        "modelo_referencia": modelo_referencia if len(completas) == len(TAREAS) else None,
        "proveedor_referencia": proveedor,
        "actualizado": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if len(completas) == len(TAREAS):
        ciego, clave_paquete = construir_paquete(
            completas,
            semilla=semilla,
            modelo_local=modelo_local,
            modelo_referencia=modelo_referencia,
        )
        _guardar(SALIDA / "ciego.json", ciego)
        _guardar(SALIDA / "clave.json", clave_paquete)
        meta["paquete"] = ciego["paquete"]
        meta["ciego"] = str(SALIDA / "ciego.json")
        meta["falta"] = None
    else:
        meta["ciego"] = None
        meta["falta"] = "La hoja de calificación se arma cuando las 40 tareas tienen las dos respuestas."
    _guardar(SALIDA / "estado.json", meta)
    _nota(generaciones, meta)
    return meta


def leer_archivo_referencia(path: Path) -> dict[str, str]:
    crudo = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(crudo, dict) and "respuestas" in crudo:
        crudo = crudo["respuestas"]
    return {str(clave): str(valor) for clave, valor in crudo.items()}


def correr(args: argparse.Namespace) -> dict:
    generaciones = _cargar(SALIDA / "generaciones.json")
    tareas = por_id()
    seleccion = TAREAS[: args.limite] if args.limite else TAREAS
    for tarea in seleccion:
        actual = generaciones.get(tarea["id"], {})
        if args.local and not (actual.get("local") or {}).get("texto"):
            texto, segundos = preguntar_ollama(args.modelo_local, mensaje_de(tarea))
            actual["local"] = {
                "texto": texto,
                "segundos": segundos,
                "costo_usd": 0.0,
                "modelo": args.modelo_local,
            }
            generaciones[tarea["id"]] = actual
            _guardar(SALIDA / "generaciones.json", generaciones)
            print(f"{tarea['id']} local {segundos}s", flush=True)
        if args.referencia in ("openai", "anthropic") and not (actual.get("referencia") or {}).get("texto"):
            if args.referencia == "anthropic":
                texto, segundos, uso = preguntar_anthropic(args.modelo_referencia, mensaje_de(tarea))
            else:
                texto, segundos, uso = preguntar_openai(args.modelo_referencia, mensaje_de(tarea))
            actual["referencia"] = {
                "texto": texto,
                "segundos": segundos,
                "tokens": uso,
                "costo_usd": None,
                "modelo": args.modelo_referencia,
                "nota_costo": "Tokens guardados. El costo en dólares se calcula cuando se confirma la tarifa del día.",
            }
            generaciones[tarea["id"]] = actual
            _guardar(SALIDA / "generaciones.json", generaciones)
            print(f"{tarea['id']} referencia {segundos}s", flush=True)
        if args.referencia_archivo and not (actual.get("referencia") or {}).get("texto"):
            externas = leer_archivo_referencia(args.referencia_archivo)
            if tarea["id"] not in externas:
                continue
            actual["referencia"] = {
                "texto": externas[tarea["id"]],
                "segundos": None,
                "costo_usd": None,
                "modelo": args.modelo_referencia,
            }
            generaciones[tarea["id"]] = actual

    if args.referencia_archivo:
        _guardar(SALIDA / "generaciones.json", generaciones)

    completas = {
        tarea_id: {
            "local": generaciones[tarea_id]["local"]["texto"],
            "referencia": generaciones[tarea_id]["referencia"]["texto"],
        }
        for tarea_id in tareas
        if generaciones.get(tarea_id, {}).get("local", {}).get("texto")
        and generaciones.get(tarea_id, {}).get("referencia", {}).get("texto")
    }
    meta = {
        "tareas": len(TAREAS),
        "con_respuesta_local": sum(1 for item in generaciones.values() if item.get("local", {}).get("texto")),
        "con_las_dos_respuestas": len(completas),
        "modelo_local": args.modelo_local,
        "modelo_referencia": args.modelo_referencia if len(completas) == len(TAREAS) else None,
    }
    if len(completas) == len(TAREAS):
        ciego, clave = construir_paquete(
            completas,
            semilla=args.semilla,
            modelo_local=args.modelo_local,
            modelo_referencia=args.modelo_referencia,
        )
        _guardar(SALIDA / "ciego.json", ciego)
        _guardar(SALIDA / "clave.json", clave)
        meta["paquete"] = ciego["paquete"]
        meta["ciego"] = str(SALIDA / "ciego.json")
    else:
        meta["ciego"] = None
        meta["falta"] = "La hoja de calificación se arma cuando las 40 tareas tienen las dos respuestas."
    _guardar(SALIDA / "estado.json", meta)
    _nota(generaciones, meta)
    return meta


def _nota(generaciones: dict, meta: dict) -> None:
    from interfaz.demo3_informe import construir_informe_demo3, escribir_nota_tecnica_demo3

    informe = construir_informe_demo3()
    if informe:
        escribir_nota_tecnica_demo3(informe)


def main() -> int:
    parser = argparse.ArgumentParser(description="Corre la comparación del demo 3.")
    parser.add_argument("--modelo-local", default=MODELO_LOCAL)
    parser.add_argument(
        "--modelo-referencia",
        default=os.environ.get(
            "MODELO_REFERENCIA",
            os.environ.get("ANTHROPIC_DEFAULT_MODEL", "claude-haiku-4-5")
            if os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("OPENAI_API_KEY")
            else "gpt-4o-mini",
        ),
    )
    parser.add_argument("--referencia", choices=("ninguna", "openai", "anthropic"), default="ninguna")
    parser.add_argument("--referencia-archivo", type=Path)
    parser.add_argument("--semilla", type=int, default=20261110)
    parser.add_argument("--sin-local", action="store_true")
    parser.add_argument("--limite", type=int, default=0, help="Si es mayor que cero, corre solo las primeras N tareas.")
    args = parser.parse_args()
    args.local = not args.sin_local
    meta = correr(args)
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
