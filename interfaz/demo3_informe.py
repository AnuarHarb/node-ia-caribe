"""Informe completo del demo 3: comparación, paquete ciego y calificación."""

from __future__ import annotations

import json
import statistics
from datetime import datetime
from pathlib import Path

from demo3_comparacion.tareas import TAREAS
from equipo import describir_equipo
from interfaz.catalogo import DEMOS

RAIZ = Path(__file__).resolve().parents[1]
DEMO3 = RAIZ / "resultados" / "demo3"


def _cargar_json(path: Path) -> dict | list | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _estadisticas_camino(generaciones: dict, camino: str) -> dict:
    segundos: list[float] = []
    for item in generaciones.values():
        bloque = item.get(camino) or {}
        if bloque.get("segundos") is not None:
            segundos.append(float(bloque["segundos"]))
    if not segundos:
        return {"n": 0}
    en_caliente = segundos[1:] if len(segundos) > 1 else segundos
    return {
        "n": len(segundos),
        "primera_s": round(segundos[0], 3) if segundos else None,
        "promedio_caliente_s": round(statistics.fmean(en_caliente), 3) if en_caliente else None,
        "promedio_todas_s": round(statistics.fmean(segundos), 3),
        "maximo_caliente_s": round(max(en_caliente), 3) if en_caliente else None,
        "costo_usd": 0.0 if camino == "local" else None,
    }


NOMBRE_TIPO = {
    "resumir_peticion": "Resumir una petición ciudadana",
    "redactar_respuesta": "Redactar una respuesta",
    "clasificar_solicitud": "Clasificar una solicitud",
    "extraer_datos": "Extraer datos de un documento",
    "consulta_normativa": "Responder una consulta normativa",
}
DIMENSIONES = ("exactitud", "completitud", "tono", "utilidad")
TARIFA = RAIZ / "demo3_comparacion" / "tarifa_referencia.json"


def interpretar_kappa(valor: float | None) -> str:
    """Escala de Landis y Koch (1977)."""
    if valor is None:
        return "sin dato"
    if valor < 0:
        return "pobre"
    if valor <= 0.20:
        return "leve"
    if valor <= 0.40:
        return "aceptable"
    if valor <= 0.60:
        return "moderado"
    if valor <= 0.80:
        return "considerable"
    return "casi perfecto"


def _analisis_calificacion(metricas: dict) -> dict | None:
    """Quién gana, por tipo de tarea y por dimensión. Solo con las dos calificaciones cerradas."""
    if metricas.get("estado") != "calculado":
        return None
    por_tarea = metricas.get("por_tarea") or []
    if not por_tarea:
        return None
    tipo_de = {tarea["id"]: tarea.get("tipo", "") for tarea in TAREAS}

    def ganador(item: dict) -> str:
        if item["local"] > item["referencia"]:
            return "local"
        if item["referencia"] > item["local"]:
            return "referencia"
        return "empate"

    gana = {"local": 0, "empate": 0, "referencia": 0}
    for item in por_tarea:
        gana[ganador(item)] += 1

    por_tipo = []
    for tipo, nombre in NOMBRE_TIPO.items():
        grupo = [item for item in por_tarea if tipo_de.get(item["id"]) == tipo]
        if not grupo:
            continue
        por_tipo.append(
            {
                "tipo": tipo,
                "nombre": nombre,
                "tareas": len(grupo),
                "local": round(statistics.fmean(item["local"] for item in grupo), 2),
                "referencia": round(statistics.fmean(item["referencia"] for item in grupo), 2),
                "comparables": sum(1 for item in grupo if item["comparable"]),
                "gana_local": sum(1 for item in grupo if ganador(item) == "local"),
                "gana_referencia": sum(1 for item in grupo if ganador(item) == "referencia"),
            }
        )

    no_comparables = [
        {
            "id": item["id"],
            "tipo": NOMBRE_TIPO.get(tipo_de.get(item["id"], ""), tipo_de.get(item["id"], "")),
            "local": item["local"],
            "referencia": item["referencia"],
            "diferencia": item["diferencia"],
            "gana": ganador(item),
        }
        for item in por_tarea
        if not item["comparable"]
    ]

    dimensiones = _dimensiones_y_acuerdo(metricas)
    return {
        "gana": gana,
        "por_tipo": por_tipo,
        "no_comparables": no_comparables,
        "dimensiones": dimensiones,
    }


def _dimensiones_y_acuerdo(metricas: dict) -> list[dict]:
    """Nota media por dimensión y camino, y cuánto coinciden los dos calificadores."""
    from interfaz.demo3_calificacion import CAL_DIR

    clave = _cargar_json(DEMO3 / "clave.json") or {}
    asignacion = clave.get("asignacion") or {}
    archivos = metricas.get("archivos_usados") or []
    calificaciones = [_cargar_json(CAL_DIR / nombre) for nombre in archivos]
    if len(calificaciones) != 2 or not all(isinstance(item, dict) for item in calificaciones) or not asignacion:
        return []
    indices = [
        {(puntaje["id"], puntaje["respuesta"]): puntaje for puntaje in item.get("puntajes") or []}
        for item in calificaciones
    ]
    kappas = metricas.get("kappa") or {}
    salida = []
    for dimension in DIMENSIONES:
        notas: dict[str, list[int]] = {"local": [], "referencia": []}
        pares = iguales = cercanos = 0
        cincos = 0
        for tarea_id, mapa in asignacion.items():
            for letra, camino in mapa.items():
                uno = indices[0].get((tarea_id, letra))
                dos = indices[1].get((tarea_id, letra))
                if not uno or not dos or dimension not in uno or dimension not in dos:
                    continue
                a, b_ = int(uno[dimension]), int(dos[dimension])
                notas[camino] += [a, b_]
                pares += 1
                iguales += a == b_
                cercanos += abs(a - b_) <= 1
                cincos += (a == 5) + (b_ == 5)
        if not pares:
            continue
        kappa = kappas.get(dimension) or {}
        salida.append(
            {
                "dimension": dimension,
                "local": round(statistics.fmean(notas["local"]), 2) if notas["local"] else None,
                "referencia": round(statistics.fmean(notas["referencia"]), 2) if notas["referencia"] else None,
                "acuerdo_exacto_pct": round(100 * iguales / pares, 1),
                "acuerdo_un_punto_pct": round(100 * cercanos / pares, 1),
                "notas_en_cinco_pct": round(100 * cincos / (2 * pares), 1),
                "kappa_cohen": kappa.get("cohen"),
                "kappa_cuadratico": kappa.get("cuadratico"),
                "interpretacion": interpretar_kappa(kappa.get("cohen")),
                "respuestas": pares,
            }
        )
    return salida


def _costo(generaciones: dict) -> dict:
    """Costo por tarea. Los tokens de la referencia se miden; los dólares salen de una tarifa confirmada."""
    entrada = salida = con_tokens = 0
    for item in generaciones.values():
        uso = (item.get("referencia") or {}).get("tokens") or {}
        if not uso:
            continue
        con_tokens += 1
        entrada += int(uso.get("input_tokens") or uso.get("prompt_tokens") or 0)
        salida += int(uso.get("output_tokens") or uso.get("completion_tokens") or 0)
    referencia: dict = {
        "tareas_con_tokens": con_tokens,
        "tokens_entrada": entrada,
        "tokens_salida": salida,
        "tokens_entrada_por_tarea": round(entrada / con_tokens, 1) if con_tokens else None,
        "tokens_salida_por_tarea": round(salida / con_tokens, 1) if con_tokens else None,
        "usd_total": None,
        "usd_por_tarea": None,
        "tarifa": None,
    }
    tarifa = _cargar_json(TARIFA)
    if isinstance(tarifa, dict) and con_tokens:
        por_entrada = tarifa.get("usd_por_millon_entrada")
        por_salida = tarifa.get("usd_por_millon_salida")
        if isinstance(por_entrada, (int, float)) and isinstance(por_salida, (int, float)):
            total = (entrada * por_entrada + salida * por_salida) / 1_000_000
            referencia["usd_total"] = round(total, 6)
            referencia["usd_por_tarea"] = round(total / con_tokens, 6)
            referencia["tarifa"] = {
                "usd_por_millon_entrada": por_entrada,
                "usd_por_millon_salida": por_salida,
                "fuente": str(tarifa.get("fuente") or "").strip(),
                "fecha_consulta": str(tarifa.get("fecha_consulta") or "").strip(),
            }
    return {
        "local": {
            "usd_por_tarea": 0.0,
            "nota": "Inferencia en el propio equipo. No incluye energía ni amortización del computador.",
        },
        "referencia": referencia,
    }


def _limitacion_evaluadores(nombres: list[str]) -> str | None:
    from interfaz.demo3_calificacion import _slug

    slugs = {_slug(n) for n in nombres}
    if "anuar-harb" in slugs and "grace-torres" in slugs:
        return (
            "Evaluaron el director del proyecto (Anuar Harb) y la representante legal de FCA "
            "(Grace Torres). Aceptable en este laboratorio TRL 3; para mayor independencia, "
            "conviene un tercer evaluador ajeno a la fundación."
        )
    return None


def _bloque_calificacion() -> dict:
    from interfaz.demo3_calificacion import listar_calificaciones, sincronizar_metricas

    sincronizar_metricas()
    recibidas = listar_calificaciones()
    metricas = _cargar_json(DEMO3 / "metricas.json") or {}
    if not metricas or metricas.get("estado") not in ("calculado", "parcial", "pendiente"):
        return {
            "estado": "pendiente",
            "archivos_recibidos": len(recibidas),
            "calificadores_registrados": [r.get("calificador") for r in recibidas],
            "descripcion": "Faltan dos calificaciones humanas. Complete /calificar y use «Enviar al laboratorio».",
        }
    califs = metricas.get("calificadores") or [r.get("calificador") for r in recibidas]
    base = {
        "estado": metricas.get("estado", "desconocido"),
        "archivos_recibidos": 2 if metricas.get("estado") == "calculado" else metricas.get("archivos_recibidos", len(recibidas)),
        "calificadores_registrados": califs if metricas.get("estado") == "calculado" else [r.get("calificador") for r in recibidas],
        "calificadores": califs,
        "tareas_calificadas": metricas.get("tareas_calificadas"),
        "porcentaje_comparables": metricas.get("porcentaje_comparables"),
        "calidad_promedio": metricas.get("calidad_promedio"),
        "kappa_cohen_promedio": metricas.get("kappa_cohen_promedio"),
        "kappa_interpretacion": interpretar_kappa(metricas.get("kappa_cohen_promedio"))
        if metricas.get("kappa_cohen_promedio") is not None
        else None,
        "kappa": metricas.get("kappa"),
        "analisis": _analisis_calificacion(metricas),
        "fecha_calificacion": metricas.get("fecha_calificacion"),
        "fecha_calificacion_inicio": metricas.get("fecha_calificacion_inicio"),
        "fechas_calificacion": metricas.get("fechas_calificacion"),
        "limitacion_evaluadores": None,
    }
    if metricas.get("estado") == "parcial":
        nombres = ", ".join(califs) or "1 calificador"
        base["descripcion"] = (
            f"Recibida calificación de {nombres}. Falta la segunda persona evaluadora en el laboratorio."
        )
    elif metricas.get("estado") == "calculado":
        loc = (metricas.get("calidad_promedio") or {}).get("local")
        ref = (metricas.get("calidad_promedio") or {}).get("referencia")
        kappa = metricas.get("kappa_cohen_promedio")
        base["descripcion"] = (
            f"Calificación cerrada ({', '.join(califs)}). Calidad promedio local {loc} vs referencia {ref} "
            f"(escala 1–5). {metricas.get('porcentaje_comparables')} % comparables · "
            f"Kappa Cohen promedio entre evaluadores: {kappa}."
        )
        base["limitacion_evaluadores"] = _limitacion_evaluadores(califs)
    else:
        base["descripcion"] = metricas.get("motivo") or "Métricas incompletas."
    return base


def construir_informe_demo3(extra: dict | None = None) -> dict | None:
    gen_path = DEMO3 / "generaciones.json"
    if not gen_path.is_file():
        return None
    generaciones = _cargar_json(gen_path)
    if not isinstance(generaciones, dict):
        return None
    estado = _cargar_json(DEMO3 / "estado.json") or {}
    ciego = _cargar_json(DEMO3 / "ciego.json") or {}
    meta_demo = DEMOS[3]

    locales = sum(1 for g in generaciones.values() if g.get("local", {}).get("texto"))
    refs = sum(
        1 for g in generaciones.values() if g.get("local", {}).get("texto") and g.get("referencia", {}).get("texto")
    )
    tareas_ciego = len(ciego.get("tareas") or [])
    paquete_hash = ciego.get("paquete") or estado.get("paquete")

    rend_local = _estadisticas_camino(generaciones, "local")
    rend_ref = _estadisticas_camino(generaciones, "referencia")
    calificacion = _bloque_calificacion()

    checklist = [
        {
            "item": f"{len(TAREAS)} tareas con respuesta local (Ollama)",
            "cumple": locales >= len(TAREAS),
            "medido": f"{locales}/{len(TAREAS)}",
        },
        {
            "item": f"{len(TAREAS)} tareas con respuesta de referencia comercial",
            "cumple": refs >= len(TAREAS),
            "medido": f"{refs}/{len(TAREAS)}",
        },
        {
            "item": "Paquete ciego (A/B sin identificar sistema)",
            "cumple": tareas_ciego >= len(TAREAS) and bool(paquete_hash),
            "medido": f"{tareas_ciego} tareas · hash {str(paquete_hash or '')[:12]}…" if paquete_hash else "no generado",
        },
        {
            "item": "Dos calificaciones humanas a ciegas",
            "cumple": calificacion.get("estado") == "calculado",
            "medido": (
                f"2/2 · {', '.join(calificacion.get('calificadores') or [])}"
                if calificacion.get("estado") == "calculado"
                else (
                    f"{calificacion.get('archivos_recibidos', 0)}/2 · "
                    + (", ".join(calificacion.get("calificadores_registrados") or []) or "pendiente")
                )
            ),
        },
        {
            "item": "Métricas de comparación (Kappa Cohen, % comparables)",
            "cumple": calificacion.get("estado") == "calculado",
            "medido": (
                f"{calificacion.get('porcentaje_comparables')} % comparables · Kappa Cohen {calificacion.get('kappa_cohen_promedio')}"
                if calificacion.get("porcentaje_comparables") is not None
                and calificacion.get("kappa_cohen_promedio") is not None
                else "pendiente"
            ),
        },
    ]

    metodo_listo = all(c["cumple"] for c in checklist[:3])
    calificacion_lista = calificacion.get("estado") == "calculado"

    resumen = (
        f"Se compararon {refs} tareas con modelo local "
        f"{estado.get('modelo_local', rend_local and 'qwen2.5:3b')} "
        f"frente a {estado.get('proveedor_referencia', 'referencia')} "
        f"{estado.get('modelo_referencia', '')}. "
    )
    if paquete_hash:
        resumen += f"Paquete ciego generado ({tareas_ciego} tareas, identificador {paquete_hash[:16]}…). "
    if calificacion_lista:
        cp = calificacion.get("calidad_promedio") or {}
        resumen += (
            f"Tras calificación: calidad media local {cp.get('local')} vs referencia {cp.get('referencia')}; "
            f"Kappa Cohen {calificacion.get('kappa_cohen_promedio')}."
        )
    else:
        resumen += "Falta la calificación ciega por dos evaluadores para cerrar el veredicto de calidad."

    fecha_corrida = estado.get("actualizado") or estado.get("fecha")
    if fecha_corrida and "T" not in str(fecha_corrida):
        fecha_corrida = f"{fecha_corrida}T00:00:00"

    informe: dict = {
        "demo": 3,
        "titulo": meta_demo["titulo"],
        "fecha_corrida": fecha_corrida,
        "fecha_calificacion": calificacion.get("fecha_calificacion"),
        "fecha": fecha_corrida or datetime.now().astimezone().isoformat(timespec="seconds"),
        "equipo": describir_equipo(),
        "responsable": meta_demo.get("responsable"),
        "criterio_protocolo": meta_demo.get("criterio"),
        "resumen_ejecutivo": resumen,
        "comparacion": {
            "tareas_total": len(TAREAS),
            "respuestas_local": locales,
            "respuestas_referencia": refs,
            "pares_completos": refs,
            "modelo_local": estado.get("modelo_local"),
            "modelo_referencia": estado.get("modelo_referencia"),
            "proveedor_referencia": estado.get("proveedor_referencia"),
        },
        "rendimiento": {"local": rend_local, "referencia": rend_ref},
        "costo": _costo(generaciones),
        "tipos_de_tarea": [
            {"tipo": tipo, "nombre": nombre, "tareas": sum(1 for t in TAREAS if t.get("tipo") == tipo)}
            for tipo, nombre in NOMBRE_TIPO.items()
        ],
        "semilla_paquete": (_cargar_json(DEMO3 / "clave.json") or {}).get("semilla"),
        "paquete_ciego": {
            "listo": tareas_ciego >= len(TAREAS) and bool(paquete_hash),
            "hash": paquete_hash,
            "archivo": "resultados/demo3/ciego.json",
            "clave_archivo": "resultados/demo3/clave.json",
            "aviso": ciego.get("aviso"),
            "tareas_en_paquete": tareas_ciego,
            "actualizado": estado.get("actualizado"),
            "calificacion": calificacion,
        },
        "protocolo_checklist": checklist,
        "criterio_metodo_armado": metodo_listo,
        "criterio_calificacion_completa": calificacion_lista,
        "criterio_cumplido": metodo_listo and calificacion_lista,
        "tareas_local": locales,
        "tareas_referencia": refs,
        "con_las_dos_respuestas": refs,
        "modelo_local": estado.get("modelo_local"),
        "modelo_referencia": estado.get("modelo_referencia"),
        "proveedor_referencia": estado.get("proveedor_referencia"),
        "tiempo_promedio_todas_s": rend_local.get("promedio_todas_s"),
        "tiempo_promedio_caliente_s": rend_local.get("promedio_caliente_s"),
        "tiempo_maximo_caliente_s": rend_local.get("maximo_caliente_s"),
        "tiempo_promedio_referencia_s": rend_ref.get("promedio_todas_s"),
        "comparacion_completa": tareas_ciego >= len(TAREAS) and refs >= len(TAREAS),
        "pendiente_calificacion": None if calificacion_lista else estado.get("falta") or "Dos calificaciones a ciegas.",
        "costo_local_usd": 0,
        "costo_local_nota": (
            "0 USD por consulta (inferencia local vía Ollama). No incluye energía ni amortización del equipo."
        ),
        "limitacion_calificadores": calificacion.get("limitacion_evaluadores"),
    }
    if extra:
        informe.update({k: v for k, v in extra.items() if v is not None})
        if extra.get("fecha_corrida"):
            informe["fecha_corrida"] = extra["fecha_corrida"]
            informe["fecha"] = extra["fecha_corrida"]
        elif extra.get("fecha") and not informe.get("fecha_corrida"):
            informe["fecha_corrida"] = extra["fecha"]
            informe["fecha"] = extra["fecha"]
    if informe.get("ultima_corrida_error"):
        informe["criterio_cumplido"] = False
    return informe


def escribir_nota_tecnica_demo3(informe: dict) -> None:
    from interfaz.notas import escribir_nota

    escribir_nota(3, informe)


def sincronizar_informe_demo3(extra: dict | None = None) -> dict | None:
    informe = construir_informe_demo3(extra)
    if informe:
        escribir_nota_tecnica_demo3(informe)
    return informe


def guardar_informe_demo3(informe: dict, *, historial: bool = True) -> None:
    """Escribe informe.json y la nota; opcionalmente actualiza el snapshot de historial."""
    from interfaz.informes import _ruta_historial, persistir_informe

    escribir_nota_tecnica_demo3(informe)
    if historial:
        persistir_informe(3, informe)
        return
    destino = DEMO3 / "informe.json"
    destino.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cid = informe.get("corrida_id")
    if cid:
        snap = _ruta_historial(3) / f"{cid}.json"
        snap.parent.mkdir(parents=True, exist_ok=True)
        snap.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
