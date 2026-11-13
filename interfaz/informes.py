"""Lee y resume los informes en resultados/demoN/."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def ruta_informe(demo_id: int) -> Path:
    return RAIZ / "resultados" / f"demo{demo_id}" / "informe.json"


def cargar(demo_id: int) -> dict | None:
    if demo_id == 1:
        from interfaz.demo1_informe import construir_informe_demo1, guardar_informe_demo1

        path = ruta_informe(1)
        extra: dict = {}
        if path.is_file():
            previo = json.loads(path.read_text(encoding="utf-8"))
            extra["corrida_id"] = previo.get("corrida_id")
            extra["fecha"] = previo.get("fecha")
        informe = construir_informe_demo1(extra or None)
        if informe:
            guardar_informe_demo1(informe, historial=False)
            cid = informe.get("corrida_id")
            if cid:
                snap = _ruta_historial(1) / f"{cid}.json"
                if snap.is_file():
                    snap.write_text(
                        json.dumps(informe, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
        return informe
    if demo_id == 3:
        from interfaz.demo3_informe import construir_informe_demo3, guardar_informe_demo3

        path = ruta_informe(3)
        extra: dict = {}
        if path.is_file():
            previo = json.loads(path.read_text(encoding="utf-8"))
            extra["corrida_id"] = previo.get("corrida_id")
            extra["fecha"] = previo.get("fecha")
            extra["ultima_corrida_error"] = previo.get("ultima_corrida_error")
        informe = construir_informe_demo3(extra or None)
        if informe:
            guardar_informe_demo3(informe, historial=False)
            cid = informe.get("corrida_id")
            if cid:
                snap = _ruta_historial(3) / f"{cid}.json"
                if snap.is_file():
                    snap.write_text(
                        json.dumps(informe, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
        return informe
    if demo_id == 2:
        # Siempre se recalcula desde los turnos medidos: un informe viejo de carga por
        # texto no puede tapar (ni reemplazar) la sesión de voz.
        from interfaz.demo2_informe import construir_informe_demo2

        path = ruta_informe(2)
        extra = {}
        if path.is_file():
            previo = json.loads(path.read_text(encoding="utf-8"))
            if "criterios" in previo:
                extra["corrida_id"] = previo.get("corrida_id")
        return construir_informe_demo2(extra or None)
    path = ruta_informe(demo_id)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return construir_desde_fuentes(demo_id)


def construir_desde_fuentes(demo_id: int) -> dict | None:
    if demo_id == 3:
        from interfaz.demo3_informe import construir_informe_demo3

        return construir_informe_demo3()
    if demo_id == 1:
        from interfaz.demo1_informe import construir_informe_demo1

        return construir_informe_demo1()
    if demo_id == 2:
        from interfaz.demo2_informe import construir_informe_demo2

        return construir_informe_demo2()
    return None


def _id_corrida(fecha: str) -> str:
    seguro = fecha.replace(":", "-").replace("+", "_")
    return seguro[:25] if seguro else datetime.now().astimezone().isoformat(timespec="seconds").replace(":", "-")


def _ruta_historial(demo_id: int) -> Path:
    return RAIZ / "resultados" / f"demo{demo_id}" / "historial"


def _ruta_indice(demo_id: int) -> Path:
    return _ruta_historial(demo_id) / "indice.json"


def estado_corrida(demo_id: int, informe: dict) -> str:
    if informe.get("criterio_cumplido") is True:
        return "ok"
    if demo_id == 2:
        # El criterio tiene tres partes (usuarios a la vez, tiempo y sin internet). Solo
        # está cumplido con las tres medidas; un promedio bajo por sí solo no alcanza.
        if not informe.get("consultas_voz") or informe.get("entrada") == "texto":
            return "parcial" if "criterios" not in informe else "pendiente"
        criterios = informe.get("criterios") or {}
        if criterios.get("tiempo") is False or informe.get("criterio_10s") is False:
            return "falla"
        return "parcial"
    if demo_id == 3:
        if informe.get("ultima_corrida_error"):
            return "falla"
        if informe.get("criterio_metodo_armado"):
            return "ok" if informe.get("comparacion_completa") else "parcial"
        if informe.get("criterio_cumplido") is False:
            return "falla"
        if informe.get("comparacion_completa"):
            return "ok"
        refs = int(informe.get("tareas_referencia") or informe.get("con_las_dos_respuestas") or 0)
        locales = int(informe.get("tareas_local") or 0)
        if locales >= 40 and refs < 40:
            return "parcial"
        if locales > 0:
            return "parcial"
        return "pendiente"
    if informe.get("parcial") or informe.get("pendiente") or informe.get("pendiente_calificacion"):
        return "parcial"
    if demo_id == 1 and informe.get("filas", 0) > 0:
        return "ok" if informe.get("criterio_video_error_real") else "parcial"
    if demo_id == 4 and (informe.get("variedades") or []):
        # Hay cifra, pero no con la muestra del protocolo en las dos variedades.
        return "parcial"
    if demo_id == 5 and informe:
        return "falla" if informe.get("criterio_cumplido") is False else "parcial"
    return "pendiente"


def estado_hipotesis_portada(demo_id: int) -> dict[str, str]:
    """Estado visible en la portada: ok, falla, parcial o pendiente."""
    informe = cargar(demo_id)
    if not informe:
        return {"estado": "pendiente", "etiqueta": "Por ejecutar", "detalle": "Aún no hay corrida guardada"}

    if informe.get("criterio_cumplido") is True:
        return {"estado": "ok", "etiqueta": "Hipótesis cumplida", "detalle": resumen_de_informe(demo_id, informe)}
    if demo_id == 3 and informe.get("criterio_metodo_armado") and not informe.get("criterio_calificacion_completa"):
        cal = (informe.get("paquete_ciego") or {}).get("calificacion") or {}
        det = resumen_de_informe(demo_id, informe)
        if cal.get("estado") == "parcial":
            det += f" · {cal.get('descripcion', 'falta segunda calificación')}"
        else:
            det += " · calificar en /calificar"
        return {"estado": "ok", "etiqueta": "Comparación lista", "detalle": det}
    if informe.get("criterio_cumplido") is False:
        return {"estado": "falla", "etiqueta": "Hipótesis no cumplida", "detalle": resumen_de_informe(demo_id, informe)}

    est = estado_corrida(demo_id, informe)
    detalle = resumen_de_informe(demo_id, informe)
    etiquetas = {
        "ok": "Hipótesis cumplida",
        "falla": "Hipótesis no cumplida",
        "parcial": "En progreso",
        "pendiente": "Por ejecutar",
    }
    if demo_id == 3 and informe.get("ultima_corrida_error"):
        detalle = f"Última corrida falló: {informe['ultima_corrida_error']}"
    elif demo_id == 3 and informe.get("comparacion_completa"):
        etiquetas["ok"] = "Comparación lista"
        if not detalle.startswith("40"):
            detalle = resumen_de_informe(demo_id, informe) + " · calificar en /calificar"
    elif demo_id == 3 and int(informe.get("tareas_local") or 0) >= 40:
        etiquetas["parcial"] = "Falta referencia comercial"
    return {"estado": est, "etiqueta": etiquetas.get(est, "Por ejecutar"), "detalle": detalle}


def resumen_de_informe(demo_id: int, informe: dict) -> str:
    if demo_id == 5:
        if informe.get("criterio_cumplido"):
            return f"{informe['pruebas_pasadas']}/{informe['pruebas_total']} pruebas · criterio cumplido"
        return f"{informe.get('pruebas_pasadas', 0)}/{informe.get('pruebas_total', 11)} · sin criterio"
    if demo_id == 3:
        n = informe.get("tareas_local") or 0
        t = informe.get("tiempo_promedio_caliente_s")
        base = f"{n} tareas locales"
        if informe.get("comparacion_completa"):
            base += " · ciego listo"
        cal = (informe.get("paquete_ciego") or {}).get("calificacion") or {}
        if cal.get("estado") == "calculado":
            cp = cal.get("calidad_promedio") or {}
            base += f" · calidad {_dos(cp.get('local'))} local frente a {_dos(cp.get('referencia'))}"
            if cal.get("porcentaje_comparables") is not None:
                base += f" · {cal['porcentaje_comparables']:g} % comparables"
        elif cal.get("estado") == "parcial":
            base += " · 1/2 calificaciones"
        return f"{base} · {t} s prom." if t else base
    if demo_id == 1:
        wer = (informe.get("wer_corpus") or {}).get("wer_porcentaje")
        base = f"{informe.get('filas', 0)} frases · {informe.get('errores_marcados', 0)} con error"
        return f"{base} · WER {wer} %" if wer is not None else base
    if demo_id == 2:
        return _resumen_demo2(informe)
    if demo_id == 4:
        return _resumen_demo4(informe)
    return "Corrida registrada"


def _dos(valor: object) -> str:
    return f"{valor:.2f}" if isinstance(valor, (int, float)) else "—"


def _resumen_demo2(informe: dict) -> str:
    t = informe.get("tiempo_promedio_s")
    if not informe.get("consultas_voz") or informe.get("entrada") == "texto":
        return "Falta la medición por voz con el router sin internet"
    red = {True: "sin internet", False: "con internet", None: "red sin registrar"}[informe.get("sin_internet")]
    a_la_vez = informe.get("usuarios_simultaneos")
    partes = [f"{informe.get('consultas_voz')} consultas por voz"]
    if a_la_vez is not None:
        partes.append(f"{a_la_vez} a la vez")
    partes.append(f"{t} s prom.")
    partes.append(red)
    return " · ".join(partes)


def _resumen_demo4(informe: dict) -> str:
    variedades = informe.get("variedades") or []
    if not variedades:
        return "Faltan audios y transcripciones"
    partes = [f"{v['variedad']} WER {v['wer_porcentaje']} % ({v.get('frases', 0)} frases)" for v in variedades]
    medidas = {v.get("clave") or v.get("variedad") for v in variedades}
    if not ({"palenquero"} & medidas):
        partes.append("falta palenquero")
    return " · ".join(partes)


def ruta_video_corrida(demo_id: int, corrida_id: str) -> Path:
    return _ruta_historial(demo_id) / f"{corrida_id}.webm"


def persistir_informe(demo_id: int, datos: dict) -> str:
    datos = dict(datos)
    datos["demo"] = demo_id
    datos.setdefault("fecha", datetime.now().astimezone().isoformat(timespec="seconds"))
    corrida_id = datos.get("corrida_id") or _id_corrida(str(datos["fecha"]))
    datos["corrida_id"] = corrida_id
    destino = ruta_informe(demo_id)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(".tmp")
    temporal.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporal.replace(destino)
    carpeta = _ruta_historial(demo_id)
    carpeta.mkdir(parents=True, exist_ok=True)
    snap = carpeta / f"{corrida_id}.json"
    snap.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    entrada = {
        "id": corrida_id,
        "fecha": datos["fecha"],
        "resumen": resumen_de_informe(demo_id, datos),
        "estado": estado_corrida(demo_id, datos),
    }
    indice: list[dict] = []
    if _ruta_indice(demo_id).exists():
        indice = json.loads(_ruta_indice(demo_id).read_text(encoding="utf-8"))
    indice = [item for item in indice if item.get("id") != corrida_id]
    indice.insert(0, entrada)
    indice = indice[:50]
    _ruta_indice(demo_id).write_text(json.dumps(indice, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if demo_id == 3 and datos.get("comparacion_completa"):
        ciego_src = RAIZ / "resultados" / "demo3" / "ciego.json"
        if ciego_src.is_file():
            shutil.copy2(ciego_src, carpeta / f"{corrida_id}.ciego.json")
    return corrida_id


def guardar_video_corrida(demo_id: int, corrida_id: str, datos: bytes) -> None:
    if demo_id not in range(1, 6) or not corrida_id or not datos:
        raise ValueError("corrida o video inválido")
    destino = ruta_video_corrida(demo_id, corrida_id)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(".part")
    temporal.write_bytes(datos)
    temporal.replace(destino)
    entrada_video = {"video": True}
    if not _ruta_indice(demo_id).exists():
        return
    indice = json.loads(_ruta_indice(demo_id).read_text(encoding="utf-8"))
    for item in indice:
        if item.get("id") == corrida_id:
            item.update(entrada_video)
            break
    _ruta_indice(demo_id).write_text(json.dumps(indice, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _sembrar_historial_si_falta(demo_id: int) -> None:
    if _ruta_indice(demo_id).exists():
        return
    actual = cargar(demo_id)
    if demo_id == 2 and actual and not actual.get("consultas_voz"):
        return  # sin sesión de voz no hay corrida que guardar en el historial
    if actual and actual.get("fecha"):
        persistir_informe(demo_id, actual)


def listar_historial(demo_id: int) -> list[dict]:
    _sembrar_historial_si_falta(demo_id)
    if not _ruta_indice(demo_id).exists():
        return []
    indice = json.loads(_ruta_indice(demo_id).read_text(encoding="utf-8"))
    for item in indice:
        cid = item.get("id")
        if cid:
            item["video"] = ruta_video_corrida(demo_id, cid).is_file()
            snap = cargar_corrida(demo_id, cid)
            if snap:
                item["estado"] = estado_corrida(demo_id, snap)
                item["resumen"] = resumen_de_informe(demo_id, snap)
    return indice


def cargar_corrida(demo_id: int, corrida_id: str) -> dict | None:
    path = _ruta_historial(demo_id) / f"{corrida_id}.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    actual = cargar(demo_id)
    if actual and actual.get("corrida_id") == corrida_id:
        return actual
    return None


def resumen_tarjeta(demo_id: int) -> str:
    informe = cargar(demo_id)
    if not informe:
        return "Pendiente de la primera corrida"
    if demo_id == 5:
        if informe.get("criterio_cumplido"):
            return f"{informe['pruebas_pasadas']}/{informe['pruebas_total']} pruebas · criterio cumplido"
        return "Corrida sin cumplir criterio"
    if demo_id == 3:
        n = informe.get("tareas_local") or informe.get("con_respuesta_local")
        if n:
            t = informe.get("tiempo_promedio_caliente_s") or informe.get("tiempo_promedio_s")
            base = f"{n} tareas locales"
            return f"{base} · {t} s prom." if t else base
        return "Sin respuestas locales"
    if demo_id == 1:
        return resumen_de_informe(1, informe)
    if demo_id == 2:
        return _resumen_demo2(informe)
    if demo_id == 4:
        return _resumen_demo4(informe)
    return "Informe disponible"


def asegurar_informe_demo1(filas: list[dict]) -> str:
    from interfaz.demo1_informe import construir_informe_demo1

    informe = construir_informe_demo1({"fecha": datetime.now().astimezone().isoformat(timespec="seconds")})
    if not informe:
        informe = {
            "demo": 1,
            "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
            "filas": len(filas),
            "tabla": filas,
        }
    else:
        informe["fecha"] = datetime.now().astimezone().isoformat(timespec="seconds")
    return persistir_informe(1, informe)


def asegurar_informe_demo2(datos: dict) -> str:
    from interfaz.notas import escribir_nota

    datos["demo"] = 2
    datos.setdefault("fecha", datetime.now().astimezone().isoformat(timespec="seconds"))
    corrida_id = persistir_informe(2, datos)
    escribir_nota(2, {**datos, "corrida_id": corrida_id})
    return corrida_id


def registrar_fallo_demo3(mensaje: str) -> str | None:
    """Registra el error de la última corrida sin borrar las 40 respuestas ya guardadas."""
    from interfaz.demo3_informe import construir_informe_demo3

    extra: dict = {"ultima_corrida_error": mensaje}
    path = ruta_informe(3)
    if path.is_file():
        previo = json.loads(path.read_text(encoding="utf-8"))
        extra["corrida_id"] = previo.get("corrida_id")
    informe = construir_informe_demo3(extra)
    if not informe:
        return None
    informe["fecha"] = datetime.now().astimezone().isoformat(timespec="seconds")
    return persistir_informe(3, informe)


def asegurar_informe_demo3(meta: dict, generaciones: dict) -> str:
    from interfaz.demo3_informe import construir_informe_demo3, escribir_nota_tecnica_demo3

    informe = construir_informe_demo3(
        {
            "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
            "ultima_corrida_error": None,
        }
    )
    if not informe:
        refs = sum(
            1
            for item in generaciones.values()
            if item.get("local", {}).get("texto") and item.get("referencia", {}).get("texto")
        )
        informe = {
            "demo": 3,
            "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
            "tareas_referencia": refs,
            "comparacion_completa": meta.get("ciego") is not None,
        }
    escribir_nota_tecnica_demo3(informe)
    return persistir_informe(3, informe)
