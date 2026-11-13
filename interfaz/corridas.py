"""Dispara cada demo en un hilo y emite eventos."""

from __future__ import annotations

import json
import os
import statistics
import threading
import unittest
from datetime import datetime
from pathlib import Path

import httpx

from demo3_comparacion.tareas import TAREAS
from demo5_agentes import en_vivo as demo5_en_vivo
from demo5_agentes.test_aislamiento import Aislamiento
from demo4_wer.calcular import CORPUS as CORPUS_DEMO4
from demo4_wer.calcular import medir as medir_demo4
from demo4_wer.calcular import transcribir_faltantes
from equipo import describir_equipo
from interfaz.eventos import BUS
from interfaz.informes import (
    asegurar_informe_demo2,
    asegurar_informe_demo3,
    persistir_informe,
    registrar_fallo_demo3,
    ruta_informe,
)

RAIZ = Path(__file__).resolve().parents[1]
OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
MODELO_LOCAL = os.environ.get("MODELO_LOCAL", "qwen2.5:3b")

_lock_por_demo: dict[int, threading.Lock] = {i: threading.Lock() for i in range(1, 6)}


def ollama_vivo() -> bool:
    try:
        httpx.get(f"{OLLAMA}/api/version", timeout=2.0).raise_for_status()
        return True
    except httpx.HTTPError:
        return False


def _inicio(demo_id: int) -> bool:
    estado = BUS.de(demo_id)
    with _lock_por_demo[demo_id]:
        if estado.corriendo:
            estado.emitir("error", "Ya hay una corrida en curso en este demo.")
            return False
        estado.corriendo = True
    with estado._lock:
        estado.historial.clear()
    estado.emitir("inicio", "La corrida empezó.")
    return True


def _mensaje_excepcion(exc: Exception) -> str:
    import httpx

    if isinstance(exc, httpx.ConnectError):
        return (
            f"No hay conexión con {getattr(exc.request, 'url', 'el servicio')}. "
            "¿Ollama está encendido? Prueba `ollama serve` y `ollama pull qwen2.5:3b`."
        )
    if isinstance(exc, httpx.HTTPStatusError):
        cuerpo = (exc.response.text or "").strip().replace("\n", " ")[:400]
        return f"HTTP {exc.response.status_code} en {exc.request.url}: {cuerpo or exc.response.reason_phrase}"
    if isinstance(exc, httpx.TimeoutException):
        return f"Tiempo de espera agotado al llamar a {getattr(exc.request, 'url', 'el servicio')}."
    return str(exc) or exc.__class__.__name__


def _fin(
    demo_id: int,
    ok: bool = True,
    corrida_id: str | None = None,
    *,
    mensaje_error: str | None = None,
) -> None:
    estado = BUS.de(demo_id)
    estado.corriendo = False
    datos: dict = {"ok": ok}
    if corrida_id:
        datos["corrida_id"] = corrida_id
    if mensaje_error:
        datos["mensaje_error"] = mensaje_error
    if ok:
        texto_fin = "La corrida terminó."
    elif mensaje_error:
        texto_fin = mensaje_error
    else:
        texto_fin = "La corrida terminó con error."
    estado.emitir("fin", texto_fin, datos)


def lanzar(demo_id: int, opciones: dict | None = None) -> bool:
    opciones = opciones or {}
    if demo_id == 5:
        threading.Thread(target=_correr_demo5, daemon=True).start()
        return True
    if demo_id == 3:
        if not ollama_vivo():
            BUS.de(3).emitir("error", "Ollama no responde. Arranca ollama serve y vuelve a intentar.")
            return False
        threading.Thread(target=_correr_demo3_completo, args=(opciones,), daemon=True).start()
        return True
    if demo_id == 4:
        threading.Thread(target=_correr_demo4, daemon=True).start()
        return True
    if demo_id == 2:
        if not ollama_vivo():
            BUS.de(2).emitir("error", "Ollama no responde. La carga simultánea necesita el servidor de voz.")
            return False
        threading.Thread(target=_correr_demo2, daemon=True).start()
        return True
    if demo_id == 1:
        BUS.de(1).emitir(
            "aviso",
            "El demo 1 se mide con la grabación en esta página. Usa el bloque de voz abajo.",
        )
        return False
    return False


def _correr_demo5() -> None:
    if not _inicio(5):
        return
    estado = BUS.de(5)
    try:
        equipo = describir_equipo()
        entorno = RAIZ / "resultados" / "demo5" / "entorno"

        def emitir_paso(tipo: str, mensaje: str, datos: dict | None = None) -> None:
            estado.emitir(tipo, mensaje, datos)

        visible = demo5_en_vivo.corrida_visible(entorno, emitir=emitir_paso)
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Aislamiento)
        filas = []
        for prueba in suite:
            resultado = unittest.TestResult()
            prueba.run(resultado)
            nombre = prueba.id().split(".")[-1]
            esperado = prueba.shortDescription() or ""
            if resultado.wasSuccessful():
                obtenido = "pasó"
            else:
                detalle = resultado.failures + resultado.errors
                mensaje = detalle[0][1].strip().splitlines()[-1] if detalle else "falló"
                obtenido = "falló: " + mensaje
            filas.append({"prueba": nombre, "esperado": esperado, "obtenido": obtenido})
            estado.emitir(
                "prueba",
                f"{nombre}: {obtenido}",
                {"prueba": nombre, "obtenido": obtenido, "esperado": esperado},
            )
        informe = demo5_en_vivo.guardar(filas, visible, equipo)
        corrida_id = persistir_informe(5, informe)
        estado.emitir(
            "informe",
            f"Criterio {'cumplido' if informe['criterio_cumplido'] else 'no cumplido'}.",
            {"pruebas": f"{informe['pruebas_pasadas']}/{informe['pruebas_total']}"},
        )
        _fin(5, informe["criterio_cumplido"], corrida_id)
    except Exception as exc:  # noqa: BLE001
        estado.emitir("error", str(exc))
        _fin(5, False)


def _cargar_generaciones() -> dict:
    path = RAIZ / "resultados" / "demo3" / "generaciones.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _guardar_generaciones(data: dict) -> None:
    path = RAIZ / "resultados" / "demo3" / "generaciones.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporal = path.with_suffix(".tmp")
    temporal.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporal.replace(path)


def _api_key_referencia_demo3(opciones: dict) -> str:
    clave = str(opciones.get("api_key") or "").strip()
    if clave:
        return clave
    proveedor = str(opciones.get("proveedor") or "anthropic").strip().lower()
    if proveedor == "openai":
        return os.environ.get("OPENAI_API_KEY", "").strip()
    return os.environ.get("ANTHROPIC_API_KEY", "").strip()


def _demo3_local(estado, generaciones: dict) -> dict:
    from demo3_comparacion.correr import mensaje_de, preguntar_ollama

    pendientes = [t for t in TAREAS if not (generaciones.get(t["id"], {}).get("local") or {}).get("texto")]
    locales_previos = len(TAREAS) - len(pendientes)
    estado.emitir(
        "paso",
        f"Mitad local (Ollama · {MODELO_LOCAL}): {len(pendientes)} tareas por correr, "
        f"{locales_previos} ya guardadas en generaciones.json.",
    )
    if not pendientes:
        for tarea in TAREAS:
            seg = (generaciones.get(tarea["id"], {}).get("local") or {}).get("segundos")
            estado.emitir(
                "tarea",
                f"{tarea['id']} local (reutilizada{f', {seg} s' if seg is not None else ''})",
                {"id": tarea["id"], "columna": "local", "reutilizada": True, "segundos": seg},
            )
    else:
        estado.emitir("paso", "Llamando a Ollama tarea por tarea (puede tardar varios minutos).")
        for tarea in pendientes:
            actual = generaciones.get(tarea["id"], {})
            estado.emitir("paso", f"Tarea {tarea['id']} (local)…", {"id": tarea["id"], "fase": "local"})
            try:
                texto, segundos = preguntar_ollama(MODELO_LOCAL, mensaje_de(tarea))
            except Exception as exc:  # noqa: BLE001
                detalle = _mensaje_excepcion(exc)
                estado.emitir(
                    "error",
                    f"Falló la tarea {tarea['id']} (local): {detalle}",
                    {"id": tarea["id"], "fase": "local", "detalle": detalle},
                )
                raise RuntimeError(f"Tarea {tarea['id']} (local): {detalle}") from exc
            if not texto.strip():
                estado.emitir(
                    "error",
                    f"Tarea {tarea['id']}: Ollama respondió vacío.",
                    {"id": tarea["id"], "fase": "local"},
                )
                raise RuntimeError(f"Tarea {tarea['id']}: respuesta local vacía")
            actual["local"] = {
                "texto": texto,
                "segundos": segundos,
                "costo_usd": 0.0,
                "modelo": MODELO_LOCAL,
            }
            generaciones[tarea["id"]] = actual
            _guardar_generaciones(generaciones)
            estado.emitir(
                "tarea",
                f"{tarea['id']} local {segundos} s",
                {"id": tarea["id"], "segundos": segundos, "columna": "local"},
            )
            locales_parcial, refs_parcial = _contar_demo3(generaciones)
            estado.emitir(
                "progreso",
                f"Local {locales_parcial}/40 · referencia {refs_parcial}/40",
                {"local": locales_parcial, "referencia": refs_parcial},
            )
    locales, refs = _contar_demo3(generaciones)
    estado.emitir(
        "progreso",
        f"Local {locales}/40 · referencia {refs}/40",
        {"local": locales, "referencia": refs},
    )
    return generaciones


def _contar_demo3(generaciones: dict) -> tuple[int, int]:
    locales = sum(1 for g in generaciones.values() if g.get("local", {}).get("texto"))
    refs = sum(
        1 for g in generaciones.values() if g.get("local", {}).get("texto") and g.get("referencia", {}).get("texto")
    )
    return locales, refs


def _correr_demo3_completo(opciones: dict | None = None) -> None:
    if not _inicio(3):
        return
    estado = BUS.de(3)
    opciones = opciones or {}
    from demo3_comparacion.correr import correr_referencia

    try:
        generaciones = _cargar_generaciones()
        locales_ini, refs_ini = _contar_demo3(generaciones)
        estado.emitir(
            "progreso",
            f"Estado guardado: local {locales_ini}/40 · referencia {refs_ini}/40",
            {"local": locales_ini, "referencia": refs_ini},
        )
        generaciones = _demo3_local(estado, generaciones)
        tiempos = [
            float(g["local"]["segundos"])
            for g in generaciones.values()
            if g.get("local", {}).get("segundos") is not None
        ]
        en_caliente = tiempos[1:] if len(tiempos) > 1 else tiempos
        api_key = _api_key_referencia_demo3(opciones)
        proveedor = str(opciones.get("proveedor") or "anthropic").strip().lower()
        if proveedor not in ("anthropic", "openai"):
            proveedor = "anthropic"
        modelo_ref = (
            str(opciones.get("modelo_referencia") or "").strip()
            or ("claude-haiku-4-5" if proveedor == "anthropic" else "gpt-4o-mini")
        )
        refs_hechas = sum(
            1 for g in generaciones.values() if g.get("local", {}).get("texto") and g.get("referencia", {}).get("texto")
        )
        if api_key:
            pendientes_ref = len(TAREAS) - refs_hechas
            estado.emitir(
                "paso",
                f"Mitad comercial ({proveedor} · {modelo_ref}). "
                f"{pendientes_ref} tareas por llamar a la API · {refs_hechas} ya guardadas.",
            )
            locales_actuales = sum(1 for g in generaciones.values() if g.get("local", {}).get("texto"))
            if locales_actuales < len(TAREAS):
                raise RuntimeError(
                    f"Faltan respuestas locales ({locales_actuales}/{len(TAREAS)}). "
                    "Completa la mitad local antes de la referencia."
                )
            try:
                meta = correr_referencia(
                    proveedor,
                    modelo_ref,
                    api_key,
                    modelo_local=MODELO_LOCAL,
                    emitir=lambda tipo, mensaje, datos=None: estado.emitir(tipo, mensaje, datos),
                )
            except Exception as exc:  # noqa: BLE001
                detalle = _mensaje_excepcion(exc)
                estado.emitir(
                    "error",
                    f"Referencia comercial falló: {detalle}",
                    {"fase": "referencia", "detalle": detalle, "proveedor": proveedor},
                )
                raise RuntimeError(detalle) from exc
            generaciones = _cargar_generaciones()
            corrida_id = asegurar_informe_demo3(meta, generaciones)
            if meta.get("ciego"):
                estado.emitir(
                    "informe",
                    "40/40 con las dos respuestas. Paquete ciego listo en resultados/demo3/ciego.json. "
                    "Siguiente paso: dos personas en /calificar.",
                )
            else:
                estado.emitir(
                    "informe",
                    f"Referencia {meta.get('con_las_dos_respuestas', 0)}/40. Revisa tareas pendientes.",
                )
            _fin(3, True, corrida_id)
            return
        if refs_hechas >= len(TAREAS):
            estado.emitir(
                "aviso",
                "Las 40 respuestas comerciales ya están en generaciones.json. "
                "No hace falta API key para repetir. Falta calificación ciega si aún no la hiciste.",
            )
        meta = {
            "tareas": len(TAREAS),
            "con_respuesta_local": sum(
                1 for g in generaciones.values() if g.get("local", {}).get("texto")
            ),
            "con_las_dos_respuestas": sum(
                1
                for g in generaciones.values()
                if g.get("local", {}).get("texto") and g.get("referencia", {}).get("texto")
            ),
            "modelo_local": MODELO_LOCAL,
            "falta": "Falta referencia comercial y dos calificaciones a ciegas.",
        }
        (RAIZ / "resultados" / "demo3" / "estado.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        corrida_id = asegurar_informe_demo3(meta, generaciones)
        estado.emitir(
            "aviso",
            "No hay API key de referencia comercial (formulario ni variables de entorno). "
            "Solo se corrió la mitad local.",
        )
        if en_caliente:
            estado.emitir(
                "informe",
                f"Mitad local lista. Promedio en caliente {statistics.fmean(en_caliente):.2f} s. "
                "Pega la API key abajo y vuelve a correr para la referencia.",
            )
        else:
            estado.emitir("informe", "Mitad local lista. Falta API key para la referencia comercial.")
        _fin(3, True, corrida_id)
    except Exception as exc:  # noqa: BLE001
        detalle = _mensaje_excepcion(exc)
        estado.emitir("error", detalle, {"detalle": detalle, "tipo": exc.__class__.__name__})
        corrida_id = registrar_fallo_demo3(detalle)
        _fin(3, False, corrida_id, mensaje_error=detalle)
    finally:
        opciones.pop("api_key", None)


def _correr_demo4() -> None:
    if not _inicio(4):
        return
    estado = BUS.de(4)
    try:
        estado.emitir("paso", "Whisper transcribe los audios del corpus que aún no tienen transcripción.")
        transcribir_faltantes(CORPUS_DEMO4 / "costeno", CORPUS_DEMO4 / "palenquero")
        informe = medir_demo4()
        for v in informe["variedades"]:
            estado.emitir(
                "wer",
                f"{v['variedad'].capitalize()}: {v['frases']} frases, WER {v['wer_porcentaje']} %",
                {"clave": v["clave"], "frases": v["frases"], "wer_porcentaje": v["wer_porcentaje"]},
            )
        for texto in informe["advertencias"]:
            estado.emitir("paso", "Muestra corta. " + texto + ".")
        corrida_id = persistir_informe(4, informe)
        from interfaz.notas import escribir_nota

        escribir_nota(4, {**informe, "corrida_id": corrida_id})
        if informe["variedades"]:
            estado.emitir(
                "informe", "WER calculado para " + ", ".join(v["variedad"] for v in informe["variedades"])
            )
        else:
            estado.emitir("informe", "Sin pares completos. El informe lista lo que falta.")
        _fin(4, True, corrida_id)
    except Exception as exc:  # noqa: BLE001
        estado.emitir("error", str(exc))
        _fin(4, False)


def _correr_demo2() -> None:
    """Arma el informe con las consultas por voz de los teléfonos.

    Si todavía no hay sesión de voz, hace un ensayo por texto para comprobar que el
    servidor responde a tres consultas a la vez. El ensayo no cuenta para el criterio
    y no se guarda como corrida.
    """
    if not _inicio(2):
        return
    estado = BUS.de(2)
    from interfaz.demo2_informe import construir_informe_demo2

    try:
        estado.emitir("paso", "Se leen las consultas por voz de la última sesión con los teléfonos.")
        informe = construir_informe_demo2()
        if informe and informe.get("consultas_voz"):
            for indice, usuario in enumerate(informe.get("por_usuario") or [], 1):
                estado.emitir(
                    "turno",
                    f"Usuario {indice} ({usuario['usuario']}): {usuario['consultas']} consultas, "
                    f"{usuario['promedio_s']} s en promedio",
                    {"usuario": indice, "segundos": usuario["promedio_s"]},
                )
            for texto in informe.get("faltantes") or []:
                estado.emitir("paso", texto)
            corrida_id = asegurar_informe_demo2(informe)
            estado.emitir("informe", informe.get("resumen_ejecutivo", "Informe calculado."))
            _fin(2, True, corrida_id)
            return

        from concurrent.futures import ThreadPoolExecutor

        from voz.carga import FRASES, una

        usuarios = 3
        estado.emitir(
            "paso",
            f"Aún no hay consultas por voz. Ensayo con {usuarios} consultas de texto a la vez "
            "(no cuenta para el criterio).",
        )
        trabajos = [(i, FRASES[i % len(FRASES)]) for i in range(usuarios)]
        with ThreadPoolExecutor(max_workers=usuarios) as pool:
            resultados = list(pool.map(lambda item: una("http://127.0.0.1:8765", item[0], item[1]), trabajos))
        tiempos = [item["segundos"] for item in resultados]
        for i, item in enumerate(resultados):
            estado.emitir(
                "turno",
                f"Usuario {i + 1}: {item['segundos']} s (ensayo por texto)",
                {"usuario": i + 1, "segundos": item["segundos"]},
            )
        estado.emitir(
            "informe",
            f"Ensayo por texto: promedio {round(statistics.fmean(tiempos), 3)} s. El servidor responde. "
            "Falta la sesión por voz desde los teléfonos, con el router sin internet.",
        )
        _fin(2, True)
    except Exception as exc:  # noqa: BLE001
        estado.emitir("error", str(exc))
        _fin(2, False)
