"""Línea base por escrito: ¿los modelos de hoy traducen entre español y palenquero?

Es la misma pregunta del demo 4, sin audio. Cada modelo traduce estrofas de poemas
publicados en las dos lenguas y su salida se compara con la traducción humana del libro.

Los poemas tienen autor: viven en `demo4_wer/corpus/poemas/`, que no se sube al
repositorio. Lo que sí se publica (`resultados/demo4/traduccion.json`) son las cifras y
un ejemplo de dos versos.

Uso:
    python -m demo4_wer.traduccion                          # solo el modelo local
    ANTHROPIC_API_KEY=... python -m demo4_wer.traduccion --referencia anthropic
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from collections import Counter
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import httpx

from equipo import describir_equipo
from medicion import normalizar

RAIZ = Path(__file__).resolve().parents[1]
CARPETA = RAIZ / "demo4_wer" / "corpus" / "poemas"
POEMAS = CARPETA / "poemas.json"
SALIDAS = CARPETA / "salidas.json"
PUBLICO = RAIZ / "resultados" / "demo4" / "traduccion.json"
OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
MODELO_LOCAL = os.environ.get("MODELO_LOCAL", "qwen2.5:3b")
MODELOS_REFERENCIA = {"anthropic": "claude-haiku-4-5", "openai": "gpt-4o-mini"}

SISTEMA = (
    "Eres traductor. Traduces entre el español y la lengua palenquera, el criollo de San Basilio "
    "de Palenque (Colombia). Devuelve solo la traducción, con los mismos saltos de línea, sin notas "
    "ni explicaciones."
)
# (clave, campo de origen, campo de destino, nombre del origen, nombre del destino)
DIRECCIONES = (
    ("es-pal", "espanol", "palenquero", "español", "palenquero"),
    ("pal-es", "palenquero", "espanol", "palenquero", "español"),
)
PEDIDO = {
    "es-pal": "Traduce del español a la lengua palenquera:",
    "pal-es": "Traduce de la lengua palenquera al español:",
}


# --- Métrica -----------------------------------------------------------------------


def limpio(texto: str) -> str:
    """Minúsculas y sin puntuación, como en el WER. La puntuación se cambia por espacio."""
    return normalizar(re.sub(r"[^\w\s]", " ", texto or ""))


def chrf(hipotesis: list[str], referencias: list[str]) -> float:
    """chrF del conjunto (0 a 100): parecido de secuencias de letras con la traducción humana."""
    from sacrebleu.metrics import CHRF

    return round(CHRF().corpus_score([limpio(h) for h in hipotesis], [[limpio(r) for r in referencias]]).score, 2)


def firma_chrf() -> str:
    import sacrebleu
    from sacrebleu.metrics import CHRF

    metrica = CHRF()
    metrica.corpus_score(["a"], [["a"]])
    return f"sacrebleu {sacrebleu.__version__}, {metrica.get_signature()}"


def palabras_acertadas(hipotesis: list[str], referencias: list[str]) -> float:
    """Porcentaje de las palabras de la traducción humana que el sistema también escribió."""
    aciertos = total = 0
    for hip, ref in zip(hipotesis, referencias):
        en_ref = Counter(limpio(ref).split())
        en_hip = Counter(limpio(hip).split())
        aciertos += sum((en_ref & en_hip).values())
        total += sum(en_ref.values())
    return round(100 * aciertos / total, 2) if total else 0.0


def _medida(hipotesis: list[str], referencias: list[str]) -> dict:
    return {"chrf": chrf(hipotesis, referencias), "palabras_pct": palabras_acertadas(hipotesis, referencias)}


# --- Corpus y salidas --------------------------------------------------------------


def cargar_corpus(path: Path = POEMAS) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _leer(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _guardar(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporal = path.with_suffix(".tmp")
    temporal.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporal.replace(path)


def leer_publico(path: Path | None = None) -> dict | None:
    if path is not None:
        return _leer(path) or None
    from interfaz.rutas_resultados import traduccion_publica

    ruta = traduccion_publica()
    return _leer(ruta) if ruta else None


def _texto(unidad: dict, campo: str) -> str:
    return "\n".join(unidad.get(campo) or [])


def _primeros_versos(texto: str, cuantos: int) -> list[str]:
    return [linea.strip() for linea in texto.splitlines() if linea.strip()][:cuantos]


# --- Medición ----------------------------------------------------------------------


def medir(corpus: dict, salidas: dict) -> dict:
    """Cifras publicables. No lleva los poemas: solo métricas y el ejemplo de pocos versos."""
    unidades = corpus.get("unidades") or []
    fuente = corpus.get("fuente") or {}
    meta_sistemas = salidas.get("_sistemas") or {}
    direcciones = []
    for clave, campo_origen, campo_destino, origen, destino in DIRECCIONES:
        referencias = [_texto(u, campo_destino) for u in unidades]
        fuentes = [_texto(u, campo_origen) for u in unidades]
        de_direccion = salidas.get(clave) or {}
        fila = {
            "clave": clave,
            "origen": origen,
            "destino": destino,
            "palabras_referencia": sum(len(limpio(r).split()) for r in referencias),
            # Control: dejar el texto de origen sin tocar. Un modelo que no lo supera no aporta la lengua.
            "control": _medida(fuentes, referencias),
        }
        por_unidad = [{"id": u["id"], "control_chrf": chrf([f], [r])} for u, f, r in zip(unidades, fuentes, referencias)]
        for sistema in ("local", "referencia"):
            textos = [((de_direccion.get(u["id"]) or {}).get(sistema) or {}).get("texto") for u in unidades]
            hechas = sum(1 for t in textos if t)
            if not unidades or hechas < len(unidades):
                fila[sistema] = None
                continue
            tiempos = [de_direccion[u["id"]][sistema].get("segundos") for u in unidades]
            tiempos = [t for t in tiempos if isinstance(t, (int, float))]
            fila[sistema] = {
                **_medida(textos, referencias),
                # De lo que escribió el sistema, cuánto son palabras que ya venían en el texto de origen.
                "copiadas_pct": palabras_acertadas(fuentes, textos),
                "segundos_promedio": round(sum(tiempos) / len(tiempos), 2) if tiempos else None,
            }
            for item, texto, ref in zip(por_unidad, textos, referencias):
                item[f"{sistema}_chrf"] = chrf([texto], [ref])
        fila["por_unidad"] = por_unidad
        direcciones.append(fila)

    ejemplos = []
    marca = corpus.get("ejemplo") or {}
    unidad = next((u for u in unidades if u["id"] == marca.get("id")), None)
    versos = max(1, min(int(marca.get("versos") or 2), 2))
    if unidad:
        for clave, campo_origen, campo_destino, origen, destino in DIRECCIONES:
            de_unidad = (salidas.get(clave) or {}).get(unidad["id"]) or {}
            ejemplos.append(
                {
                    "direccion": clave,
                    "poema": unidad.get(f"poema_{campo_origen}"),
                    "paginas": unidad.get("paginas"),
                    "origen": (unidad.get(campo_origen) or [])[:versos],
                    "humana": (unidad.get(campo_destino) or [])[:versos],
                    "local": _primeros_versos((de_unidad.get("local") or {}).get("texto") or "", versos),
                    "referencia": _primeros_versos((de_unidad.get("referencia") or {}).get("texto") or "", versos),
                }
            )
    return {
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "equipo": describir_equipo(),
        "fuente": {
            "titulo": fuente.get("titulo"),
            "autores": fuente.get("autores") or [],
            "editorial": fuente.get("editorial") or None,
            "anio": fuente.get("anio") or None,
            "permiso": fuente.get("permiso") or None,
            "origen_del_texto": fuente.get("origen_del_texto"),
        },
        "por_verificar": corpus.get("por_verificar") or None,
        "poemas": len({u.get("poema_palenquero") for u in unidades}),
        "estrofas": len(unidades),
        "versos": {
            "palenquero": sum(len(u.get("palenquero") or []) for u in unidades),
            "espanol": sum(len(u.get("espanol") or []) for u in unidades),
        },
        "metrica": firma_chrf(),
        "instruccion": SISTEMA,
        "sistemas": {
            "local": meta_sistemas.get("local"),
            "referencia": meta_sistemas.get("referencia"),
        },
        "direcciones": direcciones,
        "ejemplos": ejemplos,
    }


# --- Llamadas a los modelos --------------------------------------------------------


def _pedido(clave: str, texto: str) -> str:
    return f"{PEDIDO[clave]}\n\n{texto}"


def version_ollama(modelo: str) -> str | None:
    try:
        etiquetas = httpx.get(f"{OLLAMA}/api/tags", timeout=10).json().get("models") or []
    except (httpx.HTTPError, ValueError):
        return None
    return next((str(m.get("digest", ""))[:12] or None for m in etiquetas if m.get("name") == modelo), None)


def preguntar_ollama(modelo: str, usuario: str) -> str:
    respuesta = httpx.post(
        f"{OLLAMA}/api/chat",
        json={
            "model": modelo,
            "stream": False,
            "messages": [{"role": "system", "content": SISTEMA}, {"role": "user", "content": usuario}],
            "options": {"temperature": 0, "seed": 7, "num_predict": 400},
        },
        timeout=180,
    )
    respuesta.raise_for_status()
    return ((respuesta.json().get("message") or {}).get("content") or "").strip()


def preguntar_anthropic(modelo: str, usuario: str, clave: str) -> str:
    respuesta = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": clave, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={
            "model": modelo,
            "max_tokens": 1024,
            "temperature": 0,
            "system": SISTEMA,
            "messages": [{"role": "user", "content": usuario}],
        },
        timeout=180,
    )
    respuesta.raise_for_status()
    bloques = respuesta.json().get("content") or []
    return next((bloque.get("text", "") for bloque in bloques if bloque.get("type") == "text"), "").strip()


def preguntar_openai(modelo: str, usuario: str, clave: str) -> str:
    respuesta = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {clave}"},
        json={
            "model": modelo,
            "temperature": 0,
            "messages": [{"role": "system", "content": SISTEMA}, {"role": "user", "content": usuario}],
        },
        timeout=180,
    )
    respuesta.raise_for_status()
    return respuesta.json()["choices"][0]["message"]["content"].strip()


def traducir(
    corpus: dict,
    salidas: dict,
    sistema: str,
    preguntar: Callable[[str], str],
    *,
    de_nuevo: bool = False,
    guardar: Callable[[dict], None] | None = None,
    avisar: Callable[[str], None] | None = None,
) -> int:
    """Traduce lo que falte en las dos direcciones. Guarda tras cada estrofa para poder retomar."""
    nuevas = 0
    for clave, campo_origen, *_ in DIRECCIONES:
        de_direccion = salidas.setdefault(clave, {})
        for unidad in corpus.get("unidades") or []:
            actual = de_direccion.setdefault(unidad["id"], {})
            if (actual.get(sistema) or {}).get("texto") and not de_nuevo:
                continue
            inicio = time.perf_counter()
            texto = preguntar(_pedido(clave, _texto(unidad, campo_origen)))
            actual[sistema] = {"texto": texto, "segundos": round(time.perf_counter() - inicio, 3)}
            nuevas += 1
            if guardar:
                guardar(salidas)
            if avisar:
                avisar(f"{clave} {unidad['id']} {sistema} {actual[sistema]['segundos']} s")
    return nuevas


def main() -> int:
    parser = argparse.ArgumentParser(description="Mide la traducción español–palenquero del demo 4.")
    parser.add_argument("--modelo-local", default=MODELO_LOCAL)
    parser.add_argument("--sin-local", action="store_true")
    parser.add_argument("--referencia", choices=("anthropic", "openai"))
    parser.add_argument("--modelo-referencia")
    parser.add_argument("--de-nuevo", action="store_true", help="Vuelve a traducir aunque ya haya salida guardada.")
    args = parser.parse_args()

    corpus = cargar_corpus()
    if not corpus:
        print(f"No está el corpus de poemas en {POEMAS.relative_to(RAIZ)}. No se midió nada.")
        return 1
    salidas = _leer(SALIDAS)
    meta = salidas.setdefault("_sistemas", {})

    def guardar(datos: dict) -> None:
        _guardar(SALIDAS, datos)

    def avisar(texto: str) -> None:
        print(texto, flush=True)

    if not args.sin_local:
        meta["local"] = {"modelo": args.modelo_local, "motor": "Ollama", "version": version_ollama(args.modelo_local)}
        traducir(corpus, salidas, "local", lambda u: preguntar_ollama(args.modelo_local, u), de_nuevo=args.de_nuevo, guardar=guardar, avisar=avisar)
    if args.referencia:
        variable = "ANTHROPIC_API_KEY" if args.referencia == "anthropic" else "OPENAI_API_KEY"
        clave = os.environ.get(variable, "").strip()
        if not clave:
            print(f"Falta la clave en la variable {variable}. No se guarda en disco: pásala al correr.")
            return 1
        modelo = args.modelo_referencia or MODELOS_REFERENCIA[args.referencia]
        llamar = preguntar_anthropic if args.referencia == "anthropic" else preguntar_openai
        meta["referencia"] = {"modelo": modelo, "proveedor": args.referencia}
        traducir(corpus, salidas, "referencia", lambda u: llamar(modelo, u, clave), de_nuevo=args.de_nuevo, guardar=guardar, avisar=avisar)
    guardar(salidas)

    publico = medir(corpus, salidas)
    _guardar(PUBLICO, publico)
    for fila in publico["direcciones"]:
        partes = [f"sin traducir chrF {fila['control']['chrf']}"]
        for sistema in ("local", "referencia"):
            if fila[sistema]:
                partes.append(f"{sistema} chrF {fila[sistema]['chrf']} ({fila[sistema]['palabras_pct']} % de palabras)")
        print(f"{fila['origen']} → {fila['destino']}: " + "; ".join(partes))

    # El informe del demo 4 lleva estas cifras junto al WER.
    from demo4_wer.calcular import SALIDA, medir as medir_wer

    _guardar(SALIDA / "informe.json", medir_wer())
    print(f"Cifras publicables: {PUBLICO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
