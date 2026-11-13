"""Informe completo del demo 1: modelos, WER, tiempos y flujo de punta a punta."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import jiwer

from demo4_wer.wer import _variedad_demo1, wer_corpus
from equipo import describir_equipo
from interfaz.catalogo import DEMOS
from interfaz.informes import _ruta_historial_escritura, ruta_video_corrida
from interfaz.rutas_resultados import carpeta_demo, carpeta_escritura
from medicion import normalizar
from voz.frases import FRASES
from voz.motor import MODELO_LOCAL, VOZ_ASISTENTE_ONNX, WHISPER_REPO

RAIZ = Path(__file__).resolve().parents[1]
GRABACIONES = RAIZ / "grabaciones"

# Lo que pide la especificación: tres o cuatro personas, diez frases cada una.
HABLANTES_PROTOCOLO = 3
FRASES_POR_HABLANTE = len(FRASES)


def _errores_de_palabras(referencia: str, hipotesis: str) -> list[dict]:
    """Qué palabras cambió, omitió o agregó el reconocimiento, según la alineación de jiwer."""
    ref = normalizar(referencia or "")
    hyp = normalizar(hipotesis or "")
    if not ref or not hyp:
        return []
    salida = jiwer.process_words(ref, hyp)
    palabras_ref = salida.references[0]
    palabras_hyp = salida.hypotheses[0]
    errores: list[dict] = []
    for tramo in salida.alignments[0]:
        if tramo.type == "equal":
            continue
        errores.append(
            {
                "tipo": {"substitute": "sustitucion", "delete": "omision", "insert": "insercion"}[tramo.type],
                "referencia": " ".join(palabras_ref[tramo.ref_start_idx : tramo.ref_end_idx]),
                "sistema": " ".join(palabras_hyp[tramo.hyp_start_idx : tramo.hyp_end_idx]),
            }
        )
    return errores


def _ruta_relativa(ruta: str) -> str:
    """El informe se publica: no lleva la ruta absoluta del computador de quien midió."""
    if not ruta:
        return ""
    camino = Path(ruta)
    if not camino.is_absolute():
        return ruta
    try:
        return str(camino.resolve().relative_to(RAIZ))
    except ValueError:
        return camino.name


def _cargar_turnos() -> dict[str, dict]:
    path = carpeta_demo(1) / "turnos.jsonl"
    if not path.is_file():
        return {}
    por_id: dict[str, dict] = {}
    for linea in path.read_text(encoding="utf-8").splitlines():
        if not linea.strip():
            continue
        fila = json.loads(linea)
        if int(fila.get("demo", 1)) == 1 and fila.get("id"):
            por_id[str(fila["id"])] = fila
    return por_id


def _etiqueta_whisper() -> str:
    repo = WHISPER_REPO.lower()
    if "small" in repo:
        return f"Whisper small (MLX, {WHISPER_REPO})"
    if "medium" in repo:
        return f"Whisper medium (MLX, {WHISPER_REPO})"
    if "large" in repo:
        return f"Whisper large (MLX, {WHISPER_REPO})"
    return WHISPER_REPO


def _etiqueta_piper() -> str:
    nombre = VOZ_ASISTENTE_ONNX.name
    if "ald" in nombre.lower():
        return f"Piper {nombre} (español México, voz masculina medium)"
    return f"Piper {nombre}"


def _modelos() -> dict:
    return {
        "whisper_repo": WHISPER_REPO,
        "whisper": _etiqueta_whisper(),
        "ollama": MODELO_LOCAL,
        "piper_asistente": _etiqueta_piper(),
        "piper_archivo": VOZ_ASISTENTE_ONNX.name,
    }


def _wer_fila(referencia: str, hipotesis: str) -> float | None:
    ref = (referencia or "").strip()
    hyp = (hipotesis or "").strip()
    if not ref or not hyp:
        return None
    return round(jiwer.wer(normalizar(ref), normalizar(hyp)) * 100, 2)


def _wer_por_persona(filas: list[dict]) -> list[dict]:
    grupos: dict[str, list[dict]] = defaultdict(list)
    for fila in filas:
        grupos[fila.get("persona") or "Sin nombre"].append(fila)
    salida: list[dict] = []
    for persona, items in sorted(grupos.items()):
        refs = [f["transcripcion_correcta"] for f in items if f.get("transcripcion_correcta")]
        hyps = [f["transcripcion_sistema"] for f in items if f.get("transcripcion_sistema")]
        if len(refs) != len(hyps) or not refs:
            continue
        bloque = wer_corpus(refs, hyps)
        salida.append(
            {
                "persona": persona,
                "frases": bloque["frases"],
                "wer_porcentaje": bloque["wer_porcentaje"],
                "sustituciones": bloque["sustituciones"],
                "eliminaciones": bloque["eliminaciones"],
                "inserciones": bloque["inserciones"],
            }
        )
    return salida


def _sincronizar_marcado_correcta(filas: list[dict]) -> None:
    from medicion import coincide

    for fila in filas:
        ref = fila.get("transcripcion_correcta") or ""
        hyp = fila.get("transcripcion_sistema") or ""
        ok = coincide(ref, hyp)
        fila["correcta_automatica"] = "si" if ok else "no"
        if fila.get("correcta") not in ("si", "no"):
            fila["correcta"] = fila["correcta_automatica"]


def _observaciones_respuestas_llm(tabla: list[dict]) -> list[dict]:
    hallazgos: list[dict] = []
    for fila in tabla:
        respuesta = fila.get("respuesta_asistente") or ""
        texto = respuesta.lower()
        if "cédula de residencia" in texto or "cedula de residencia" in texto:
            hallazgos.append(
                {
                    "id": fila.get("id"),
                    "tipo": "alucinacion",
                    "guion": fila.get("guion"),
                    "respuesta": respuesta,
                    "observacion": (
                        "El asistente pidió «cédula de residencia»; el ciudadano hablaba de un certificado "
                        "de residencia. Requisito inventado."
                    ),
                }
            )
        if "avenida principal" in texto:
            hallazgos.append(
                {
                    "id": fila.get("id"),
                    "tipo": "alucinacion",
                    "guion": fila.get("guion"),
                    "respuesta": respuesta,
                    "observacion": (
                        "Inventó que la oficina del predial «está en la avenida principal» sin dato en la petición."
                    ),
                }
            )
    return hallazgos


def _audio_url(identificador: str) -> str | None:
    for extension in (".webm", ".m4a", ".wav"):
        if (GRABACIONES / f"{identificador}{extension}").is_file():
            return f"/api/demos/1/grabacion/{identificador}"
    return None


def construir_informe_demo1(extra: dict | None = None) -> dict | None:
    filas_path = carpeta_demo(1) / "filas.json"
    if not filas_path.is_file():
        return None
    filas_raw = json.loads(filas_path.read_text(encoding="utf-8"))
    if not filas_raw:
        return None
    _sincronizar_marcado_correcta(filas_raw)
    for fila in filas_raw:
        if fila.get("audio"):
            fila["audio"] = _ruta_relativa(str(fila["audio"]))
    filas_path.write_text(json.dumps(filas_raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    turnos = _cargar_turnos()
    meta = DEMOS[1]
    modelos = _modelos()

    # Este demo es de español costeño. Las frases en palenquero que se graben en la misma
    # pantalla alimentan el demo 4 y no entran en estas cifras.
    filas_palenquero = sum(1 for f in filas_raw if _variedad_demo1(f) == "palenquero")
    filas_costeno = [f for f in filas_raw if _variedad_demo1(f) == "costeno"]
    if not filas_costeno:
        return None

    tabla: list[dict] = []
    referencias: list[str] = []
    hipotesis: list[str] = []
    for fila in filas_costeno:
        identificador = str(fila.get("id") or "")
        turno = turnos.get(identificador, {})
        ref = (fila.get("transcripcion_correcta") or "").strip()
        hyp = (fila.get("transcripcion_sistema") or "").strip()
        if ref and hyp:
            referencias.append(ref)
            hipotesis.append(hyp)
        fila_out = {
            **fila,
            "audio": _ruta_relativa(str(fila.get("audio") or "")),
            "audio_entrada_url": _audio_url(identificador),
            "respuesta_asistente": turno.get("respuesta") or "",
            "asr_s": turno.get("asr_s"),
            "llm_s": turno.get("llm_s"),
            "tts_s": turno.get("tts_s"),
            "segundos_total": turno.get("segundos"),
            "ts": turno.get("ts"),
            "wer_porcentaje": _wer_fila(ref, hyp),
            "errores_palabras": _errores_de_palabras(ref, hyp),
            "flujo_completo": bool(turno.get("respuesta") and turno.get("asr_s") is not None),
        }
        tabla.append(fila_out)

    errores = sum(1 for f in filas_costeno if f.get("correcta") == "no")
    aciertos = sum(1 for f in filas_costeno if f.get("correcta") == "si")
    wer_global = wer_corpus(referencias, hipotesis) if referencias else None
    wer_personas = _wer_por_persona(filas_costeno)

    por_hablante: dict[str, int] = defaultdict(int)
    for fila in filas_costeno:
        por_hablante[fila.get("persona") or "Sin nombre"] += 1
    cobertura = {
        "hablantes": len(por_hablante),
        "hablantes_protocolo": HABLANTES_PROTOCOLO,
        "frases": len(filas_costeno),
        "frases_por_hablante_protocolo": FRASES_POR_HABLANTE,
        "por_hablante": [{"persona": persona, "frases": n} for persona, n in sorted(por_hablante.items())],
        "completa": len(por_hablante) >= HABLANTES_PROTOCOLO
        and all(n >= FRASES_POR_HABLANTE for n in por_hablante.values()),
    }

    tiempos = [t for t in tabla if t.get("asr_s") is not None]
    promedios_etapas = {}
    if tiempos:
        promedios_etapas = {
            "asr_promedio_s": round(sum(t["asr_s"] for t in tiempos) / len(tiempos), 3),
            "llm_promedio_s": round(sum(t["llm_s"] for t in tiempos) / len(tiempos), 3),
            "tts_promedio_s": round(sum(t["tts_s"] for t in tiempos) / len(tiempos), 3),
            "total_promedio_s": round(sum(t["segundos_total"] for t in tiempos) / len(tiempos), 3),
            "total_maximo_s": round(max(t["segundos_total"] for t in tiempos), 3),
            "primera_total_s": round(tiempos[0]["segundos_total"], 3),
        }
        if len(tiempos) > 1:
            resto = tiempos[1:]
            promedios_etapas["resto_promedio_s"] = round(sum(t["segundos_total"] for t in resto) / len(resto), 3)

    corrida_id = (extra or {}).get("corrida_id")
    video_corrida = None
    if corrida_id and ruta_video_corrida(1, corrida_id).is_file():
        video_corrida = f"/api/demos/1/historial/{corrida_id}.webm"

    observaciones_llm = _observaciones_respuestas_llm(tabla)
    flujo_ok = all(f.get("flujo_completo") for f in tabla) if tabla else False
    resumen = (
        f"{len(tabla)} frases medidas con {cobertura['hablantes']} hablante(s): "
        f"{aciertos} transcritas bien y {errores} con error de reconocimiento. "
    )
    if wer_global:
        resumen += f"WER del corpus {wer_global['wer_porcentaje']} %. "
    if promedios_etapas:
        resumen += (
            f"Tiempos promedio: escuchar {promedios_etapas['asr_promedio_s']} s, "
            f"entender/responder {promedios_etapas['llm_promedio_s']} s, hablar {promedios_etapas['tts_promedio_s']} s."
        )

    informe: dict = {
        "demo": 1,
        "titulo": meta["titulo"],
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "responsable": meta.get("responsable"),
        "equipo": describir_equipo(),
        "modelos": modelos,
        "resumen_ejecutivo": resumen.strip(),
        "filas": len(tabla),
        "aciertos_marcados": aciertos,
        "errores_marcados": errores,
        "criterio_flujo": flujo_ok and len(tabla) > 0,
        "criterio_video_error_real": errores >= 1,
        "criterio_cumplido": flujo_ok and errores >= 1 and len(tabla) > 0,
        "wer_corpus": wer_global,
        "wer_por_persona": wer_personas,
        "tiempos_promedio": promedios_etapas,
        "cobertura": cobertura,
        "filas_palenquero": filas_palenquero,
        "tabla": tabla,
        "video_corrida": video_corrida,
        "definicion_wer": "WER por frase y por hablante con jiwer; texto en minúsculas y sin puntuación.",
        "nota_referencias": (
            "La referencia humana es lo dicho (guion revisado), no la transcripción del ASR. "
            "Se corrigieron dos referencias que habían copiado el texto del reconocimiento."
        ),
        "observaciones_llm": observaciones_llm,
        "implicacion_alucinaciones": (
            "El modelo local inventó requisitos y ubicaciones sin base documental. "
            "Eso motiva conectar el asistente a la información oficial de cada entidad (RAG o integración)."
        ),
    }
    if extra:
        informe.update({k: v for k, v in extra.items() if v is not None})
    return informe


def escribir_nota_tecnica_demo1(informe: dict) -> None:
    from interfaz.notas import escribir_nota

    escribir_nota(1, informe)


def guardar_informe_demo1(informe: dict, *, historial: bool = False) -> None:
    from interfaz.informes import persistir_informe

    escribir_nota_tecnica_demo1(informe)
    if historial:
        persistir_informe(1, informe)
        return
    destino = carpeta_escritura(1) / "informe.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cid = informe.get("corrida_id")
    if cid:
        snap = _ruta_historial_escritura(1) / f"{cid}.json"
        snap.parent.mkdir(parents=True, exist_ok=True)
        snap.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
