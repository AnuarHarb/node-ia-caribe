"""Informe completo del demo 3: comparación, paquete ciego y calificación."""

from __future__ import annotations

import json
import statistics
from datetime import datetime
from pathlib import Path

from demo3_comparacion.tareas import TAREAS
from equipo import describir_equipo, texto_equipo
from interfaz.catalogo import DEMOS

RAIZ = Path(__file__).resolve().parents[1]
DEMO3 = RAIZ / "resultados" / "demo3"
NOTA = RAIZ / "notas" / "Demo-3_IA-local-frente-a-referencia-externa.md"


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
        "kappa": metricas.get("kappa"),
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
    NOTA.parent.mkdir(parents=True, exist_ok=True)
    c = informe.get("comparacion") or {}
    p = informe.get("paquete_ciego") or {}
    rl = (informe.get("rendimiento") or {}).get("local") or {}
    rr = (informe.get("rendimiento") or {}).get("referencia") or {}
    cal = p.get("calificacion") or {}

    lineas = [
        "# Nota técnica · IA local frente a una referencia externa",
        "",
        "Evidencia TRL 3 · Nodo IA Caribe.",
        "",
        "| Campo | Contenido |",
        "| --- | --- |",
        f"| Fecha de la corrida (40+40) | {informe.get('fecha_corrida', informe.get('fecha', '—'))} |",
        f"| Fecha de calificación ciega | {informe.get('fecha_calificacion', '—')} |",
        f"| Responsable | {informe.get('responsable', 'Anuar Harb')} |",
        f"| Equipo | {texto_equipo(informe.get('equipo') or {})} |",
        "",
        "## 1. Resumen",
        "",
        informe.get("resumen_ejecutivo", ""),
        "",
        "## 2. Comparación de sistemas",
        "",
        f"- Tareas del protocolo: **{c.get('tareas_total', 40)}**",
        f"- Respuestas modelo local ({c.get('modelo_local', '—')}): **{c.get('respuestas_local', 0)}/{c.get('tareas_total', 40)}**",
        f"- Respuestas referencia ({c.get('proveedor_referencia', '—')} · {c.get('modelo_referencia', '—')}): **{c.get('respuestas_referencia', 0)}/{c.get('tareas_total', 40)}**",
        "",
        "### Tiempos de respuesta (segundos, medidos)",
        "",
        "| Camino | Primera tarea | Promedio en caliente | Promedio todas | Máximo en caliente |",
        "| --- | --- | --- | --- | --- |",
        f"| Local | {rl.get('primera_s', '—')} | {rl.get('promedio_caliente_s', '—')} | {rl.get('promedio_todas_s', '—')} | {rl.get('maximo_caliente_s', '—')} |",
        f"| Referencia | — | {rr.get('promedio_caliente_s', '—')} | {rr.get('promedio_todas_s', '—')} | {rr.get('maximo_caliente_s', '—')} |",
        "",
        "**Costo local:** 0 USD por consulta (inferencia en el nodo). No incluye energía ni amortización del equipo. "
        "El costo de la referencia comercial no se consolida aquí sin tarifa confirmada del día.",
        "",
        "## 3. Paquete ciego",
        "",
    ]
    if p.get("listo"):
        lineas += [
            f"- **Generado:** sí ({p.get('tareas_en_paquete')} tareas).",
            f"- **Identificador (hash):** `{p.get('hash', '')}`",
            f"- **Archivo para calificadores:** `{p.get('archivo')}` (sin identificar qué respuesta es local o comercial).",
            f"- **Clave de desblindaje (no entregar a calificadores):** `{p.get('clave_archivo')}`",
            f"- {p.get('aviso', '')}",
            "",
            "Calificación: [http://127.0.0.1:8765/calificar](http://127.0.0.1:8765/calificar) o interfaz Demo 3 → *Calificar paquete ciego*.",
            "",
        ]
    else:
        lineas += ["- **Generado:** no. Correr el experimento hasta 40+40 respuestas.", ""]

    lineas += ["## 4. Estado del protocolo", "", "| Paso | Medido | Cumple |", "| --- | --- | --- |"]
    for fila in informe.get("protocolo_checklist") or []:
        lineas.append(f"| {fila.get('item', '')} | {fila.get('medido', '')} | {'Sí' if fila.get('cumple') else 'No'} |")
    lineas += [
        "",
        "## 5. Calificación humana y métricas",
        "",
        cal.get("descripcion", "Pendiente."),
        "",
    ]
    if cal.get("estado") == "calculado":
        cp = cal.get("calidad_promedio") or {}
        lineas += [
            f"- Evaluadores: **{', '.join(cal.get('calificadores') or [])}**",
            f"- Calidad promedio **local:** {cp.get('local')}",
            f"- Calidad promedio **referencia:** {cp.get('referencia')}",
            f"- Tareas comparables: {cal.get('porcentaje_comparables')} %",
            f"- κ Cohen promedio (acuerdo entre evaluadores): **{cal.get('kappa_cohen_promedio')}**",
            "",
        ]
        if cal.get("limitacion_evaluadores"):
            lineas += [f"- *Limitación:* {cal['limitacion_evaluadores']}", ""]

    lineas += [
        "## 6. Definiciones",
        "",
        "- **Calidad de una respuesta:** promedio de exactitud, completitud, tono y utilidad (1–5).",
        "- **Calidad de un camino:** promedio de las dos calificaciones humanas por tarea.",
        "- **Tarea comparable:** diferencia absoluta ≤ 1 punto entre caminos.",
        "- **Kappa de Cohen:** acuerdo entre calificadores (sin ponderar); kappa cuadrático aparte.",
        "",
        "## 7. Limitaciones",
        "",
        "Tareas y radicados ficticios. Modelo local pequeño (nodo borde). No se exige que gane lo local; se valida el método. "
        "Las entradas incluyen el texto de trabajo: se mide aplicación de la instrucción, no memoria legal.",
        "",
    ]
    if informe.get("limitacion_calificadores"):
        lineas.insert(-2, informe["limitacion_calificadores"])
        lineas.insert(-2, "")
    NOTA.write_text("\n".join(lineas), encoding="utf-8")


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
