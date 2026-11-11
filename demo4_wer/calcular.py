"""Línea base de WER. Sin audio no inventa una cifra."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from demo4_wer.wer import pares_de_carpeta, pares_demo1, tabla, wer_corpus
from equipo import describir_equipo, texto_equipo

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "resultados" / "demo4"


def transcribir_faltantes(*carpetas: Path) -> None:
    from voz.motor import Motor

    pendientes = []
    for carpeta in carpetas:
        if not carpeta.exists():
            continue
        for audio in sorted(carpeta.iterdir()):
            if audio.suffix.lower() not in {".wav", ".webm", ".mp3", ".m4a", ".flac"}:
                continue
            referencia = audio.with_suffix(".txt")
            hipotesis = carpeta / f"{audio.stem}.hip.txt"
            if referencia.exists() and not hipotesis.exists():
                pendientes.append((audio, hipotesis))
    if not pendientes:
        return
    motor = Motor()
    motor.cargar(piper=False)
    for audio, hipotesis in pendientes:
        texto, segundos = motor.transcribir(audio, idioma=None)
        hipotesis.write_text(texto + "\n", encoding="utf-8")
        print(f"{audio.name}: {segundos} s", flush=True)


def variedad_desde_pares(nombre: str, pares: list[tuple]) -> dict | None:
    if not pares:
        return None
    if len(pares[0]) == 4:
        referencias = [item[2] for item in pares]
        hipotesis = [item[3] for item in pares]
    else:
        raise ValueError("a esta variedad todavía le falta la transcripción del sistema")
    medicion = wer_corpus(referencias, hipotesis)
    return {
        "variedad": nombre,
        "frases": medicion["frases"],
        "wer_porcentaje": medicion["wer_porcentaje"],
        "detalle": medicion,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Calcula el WER del demo 4.")
    parser.add_argument("--demo1", type=Path, default=RAIZ / "resultados" / "demo1" / "filas.json")
    parser.add_argument("--palenquero", type=Path, default=RAIZ / "demo4_wer" / "corpus" / "palenquero")
    parser.add_argument("--costeno-extra", type=Path, default=RAIZ / "demo4_wer" / "corpus" / "costeno")
    parser.add_argument(
        "--transcribir",
        action="store_true",
        help="Pasa Whisper, sin forzar idioma, sobre los audios que todavía no tienen .hip.txt.",
    )
    args = parser.parse_args()
    if args.transcribir:
        transcribir_faltantes(args.costeno_extra, args.palenquero)

    variedades = []
    costeno = pares_demo1(args.demo1)
    extra = pares_de_carpeta(args.costeno_extra)
    # El corpus en carpeta trae la referencia. La hipótesis tiene que estar en un .hip.txt gemelo.
    hipotesis_extra = []
    for stem, _audio, referencia in extra:
        hip = (args.costeno_extra / f"{stem}.hip.txt")
        if hip.exists():
            hipotesis_extra.append((stem, _audio, referencia, hip.read_text(encoding="utf-8")))
    costeno.extend(hipotesis_extra)
    if costeno:
        variedades.append(variedad_desde_pares("español costeño", costeno))

    palenquero_refs = pares_de_carpeta(args.palenquero)
    palenquero = []
    for stem, audio, referencia in palenquero_refs:
        hip = args.palenquero / f"{stem}.hip.txt"
        if hip.exists():
            palenquero.append((stem, audio, referencia, hip.read_text(encoding="utf-8")))
    if palenquero:
        variedades.append(variedad_desde_pares("palenquero", palenquero))

    informe = {
        "demo": 4,
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "equipo": describir_equipo(),
        "modelo": "Pendiente de transcribir con Whisper sin ajustar. Este comando calcula el WER; no transcribe solo.",
        **tabla([item for item in variedades if item]),
        "pendiente": [],
    }
    if not any(item["variedad"] == "español costeño" for item in informe["variedades"]):
        informe["pendiente"].append("español costeño: faltan las frases del demo 1, con transcripción correcta y transcripción del sistema")
    if not any(item["variedad"] == "palenquero" for item in informe["variedades"]):
        informe["pendiente"].append(
            "palenquero: faltan 30 a 50 pares audio + transcripción correcta, de grabación pública o de una persona hablante designada por la Fundación Chano y Chalole, con consentimiento y aval"
        )
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "informe.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(texto_equipo(informe["equipo"]))
    if informe["variedades"]:
        for item in informe["variedades"]:
            print(f"{item['variedad']}: {item['frases']} frases, WER {item['wer_porcentaje']} %")
    else:
        print("Sin frases todavía. No se calculó un WER.")
    for pendiente in informe["pendiente"]:
        print("Pendiente:", pendiente)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
