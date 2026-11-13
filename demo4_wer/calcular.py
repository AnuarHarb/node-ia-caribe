"""Línea base de WER. Sin audio no inventa una cifra.

`medir()` arma el informe y lo usan por igual la interfaz y la terminal, para que las
dos den exactamente el mismo número.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from demo4_wer.wer import pares_de_carpeta, pares_demo1, tabla, wer_corpus
from equipo import describir_equipo, texto_equipo

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "resultados" / "demo4"
DEMO1_FILAS = RAIZ / "resultados" / "demo1" / "filas.json"
CORPUS = RAIZ / "demo4_wer" / "corpus"

# La especificación pide entre 30 y 50 frases por variedad.
FRASES_MINIMAS = 30
FRASES_MAXIMAS = 50

# (clave, nombre visible, carpeta del corpus)
VARIEDADES = (
    ("costeno", "español costeño", "costeno"),
    ("palenquero", "palenquero", "palenquero"),
)

# Las dos variedades se transcriben con la misma configuración que usa el asistente del
# demo 1: Whisper con el idioma fijado en español. Whisper no tiene palenquero entre sus
# idiomas. Para dejar que detecte el idioma solo: DEMO4_IDIOMA_WHISPER=auto.
IDIOMA_WHISPER = os.environ.get("DEMO4_IDIOMA_WHISPER", "es").strip().lower()


def idioma_whisper() -> str | None:
    return None if IDIOMA_WHISPER in ("", "auto", "none") else IDIOMA_WHISPER


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
        texto, segundos = motor.transcribir(audio, idioma=idioma_whisper())
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
    for fila, par in zip(medicion["por_frase"], pares):
        fila["id"] = str(par[0])
    return {
        "variedad": nombre,
        "frases": medicion["frases"],
        "wer_porcentaje": medicion["wer_porcentaje"],
        "detalle": medicion,
    }


def _modelo_whisper() -> str:
    from voz.motor import WHISPER_REPO

    return WHISPER_REPO


def medir(
    demo1: Path = DEMO1_FILAS,
    carpetas: dict[str, Path] | None = None,
) -> dict:
    """Calcula el WER de cada variedad con lo que haya. No transcribe ni escribe archivos."""
    carpetas = carpetas or {}
    variedades: list[dict] = []
    pendiente: list[str] = []
    advertencias: list[str] = []
    for clave, nombre, subcarpeta in VARIEDADES:
        carpeta = carpetas.get(clave) or CORPUS / subcarpeta
        de_demo1 = pares_demo1(demo1, variedad=clave)
        de_carpeta: list[tuple] = []
        sin_transcribir = sin_audio = 0
        for stem, audio, referencia in pares_de_carpeta(carpeta):
            hip = carpeta / f"{stem}.hip.txt"
            if hip.exists():
                de_carpeta.append((stem, audio, referencia, hip.read_text(encoding="utf-8")))
            elif audio:
                sin_transcribir += 1
            else:
                sin_audio += 1
        medida = variedad_desde_pares(nombre, de_demo1 + de_carpeta)
        if sin_transcribir:
            pendiente.append(
                f"{nombre}: {sin_transcribir} frase(s) del corpus sin transcribir todavía; "
                "al correr el experimento Whisper las transcribe"
            )
        if sin_audio:
            pendiente.append(f"{nombre}: {sin_audio} transcripción(es) correcta(s) sin su audio en el corpus")
        if not medida:
            if clave == "palenquero":
                pendiente.append(
                    "palenquero: faltan frases. Grábalas en el demo 1 con la variedad «palenquero» "
                    "o súbelas en «Armar el corpus» (grabación pública o hablante designado por la "
                    "Fundación Chano y Chalole, con consentimiento y aval)"
                )
            else:
                pendiente.append(
                    "español costeño: faltan frases del demo 1 con transcripción correcta y del sistema"
                )
            continue
        medida["clave"] = clave
        medida["origen"] = {"demo1": len(de_demo1), "carpeta": len(de_carpeta)}
        medida["muestra_suficiente"] = medida["frases"] >= FRASES_MINIMAS
        if not medida["muestra_suficiente"]:
            advertencias.append(
                f"{nombre}: {medida['frases']} frases medidas; el protocolo pide entre "
                f"{FRASES_MINIMAS} y {FRASES_MAXIMAS}"
            )
        variedades.append(medida)

    medidas = {item["clave"] for item in variedades}
    cifra_por_variedad = all(clave in medidas for clave, _, _ in VARIEDADES)
    informe = {
        "demo": 4,
        "titulo": "Línea base del error (WER)",
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "responsable": "Anuar Harb",
        "equipo": describir_equipo(),
        "modelo": f"{_modelo_whisper()}, sin ajustar",
        "idioma_whisper": idioma_whisper() or "auto",
        "frases_minimas_protocolo": FRASES_MINIMAS,
        "frases_maximas_protocolo": FRASES_MAXIMAS,
        **tabla(variedades),
        "pendiente": pendiente,
        "advertencias": advertencias,
    }
    # La prueba por escrito (traducción) se mide aparte y aquí solo se adjunta. No cambia el criterio.
    from demo4_wer.traduccion import leer_publico

    traduccion = leer_publico()
    if traduccion:
        informe["traduccion"] = traduccion
    # Solo se marca el criterio cuando hay una cifra por cada variedad y con la muestra del
    # protocolo. Si falta algo, el informe queda como evidencia parcial, no como hipótesis fallida.
    if cifra_por_variedad and not pendiente and all(item["muestra_suficiente"] for item in variedades):
        informe["criterio_cumplido"] = True
    return informe


def main() -> int:
    parser = argparse.ArgumentParser(description="Calcula el WER del demo 4.")
    parser.add_argument("--demo1", type=Path, default=DEMO1_FILAS)
    parser.add_argument("--palenquero", type=Path, default=CORPUS / "palenquero")
    parser.add_argument("--costeno-extra", type=Path, default=CORPUS / "costeno")
    parser.add_argument(
        "--transcribir",
        action="store_true",
        help="Pasa Whisper sobre los audios del corpus que todavía no tienen .hip.txt.",
    )
    args = parser.parse_args()
    if args.transcribir:
        transcribir_faltantes(args.costeno_extra, args.palenquero)

    informe = medir(args.demo1, {"costeno": args.costeno_extra, "palenquero": args.palenquero})
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "informe.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(texto_equipo(informe["equipo"]))
    if informe["variedades"]:
        for item in informe["variedades"]:
            print(f"{item['variedad']}: {item['frases']} frases, WER {item['wer_porcentaje']} %")
    else:
        print("Sin frases todavía. No se calculó un WER.")
    for texto in informe["advertencias"]:
        print("Advertencia:", texto)
    for texto in informe["pendiente"]:
        print("Pendiente:", texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
