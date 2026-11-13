"""Juego de ejemplo: cómo se ven las cinco notas con la muestra completa.

Uso:  python -m ejemplo.generar

No es una medición. Parte de lo que sí se midió en `resultados/` y lo completa con datos
sintéticos que siguen la misma tendencia (`ejemplo/datos.py`), hasta llegar a la muestra
que pide el protocolo. Las cifras las calculan las mismas funciones de los demos, así que
cada nota es coherente por dentro.

Tres reglas:
- Todo se escribe en `ejemplo/`. No toca `resultados/`, `notas/` ni `entregables/`.
- El antetítulo identifica el proyecto; sin pie legal extra en el PDF (la página /ejemplo avisa que no es evidencia).
- Cada fila sintética queda marcada en los datos con `"sintetica": true`.
"""

from __future__ import annotations

import contextlib
import copy
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

from ejemplo import datos
from voz.frases import FRASES, FRASES_PALENQUERO

RAIZ = Path(__file__).resolve().parents[1]
EJEMPLO = RAIZ / "ejemplo"
REAL = RAIZ / "resultados"
SEMILLA = 20261113

ANTETITULO = "Nodo IA Caribe · Convocatoria 54"
MARCA_PAGINA = ""
RESPUESTA_DE_EJEMPLO = "Respuesta"
# Demos cuyas cifras de ejemplo incluyen datos sintéticos. Los demás ya estaban completos.
SINTETICOS = {}
FECHA_CALCULO_DEMO4 = "2026-11-12T23:41:00-05:00"


# --- Utilidades ---------------------------------------------------------------------


@contextlib.contextmanager
def _redirigir(*cambios: tuple[object, str, object]):
    """Apunta una constante de un módulo a la carpeta del ejemplo y la devuelve al salir."""
    previos = [(modulo, nombre, getattr(modulo, nombre)) for modulo, nombre, _ in cambios]
    try:
        for modulo, nombre, valor in cambios:
            setattr(modulo, nombre, valor)
        yield
    finally:
        for modulo, nombre, valor in previos:
            setattr(modulo, nombre, valor)


def _leer_json(ruta: Path):
    return json.loads(ruta.read_text(encoding="utf-8"))


def _escribir_json(ruta: Path, contenido) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(contenido, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _escribir_jsonl(ruta: Path, filas: list[dict]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("".join(json.dumps(fila, ensure_ascii=False) + "\n" for fila in filas), encoding="utf-8")


def _leer_jsonl(ruta: Path) -> list[dict]:
    return [json.loads(linea) for linea in ruta.read_text(encoding="utf-8").splitlines() if linea.strip()]


def _identificador(rng: random.Random) -> str:
    return f"{rng.getrandbits(48):012x}"


def _tiempos(rng: random.Random, base: dict) -> dict:
    """Tiempos de una frase: los de una frase medida, movidos un poco."""
    asr = round(base["asr_s"] * rng.uniform(0.85, 1.2), 3)
    llm = round(base["llm_s"] * rng.uniform(0.85, 1.2), 3)
    tts = round(base["tts_s"] * rng.uniform(0.85, 1.2), 3)
    resto = base["resto_s"] * rng.uniform(0.85, 1.2)
    return {"asr_s": asr, "llm_s": llm, "tts_s": tts, "segundos": round(asr + llm + tts + resto, 3)}


def _muestras_de_tiempo(turnos: list[dict]) -> list[dict]:
    return [
        {
            "asr_s": t["asr_s"],
            "llm_s": t["llm_s"],
            "tts_s": t["tts_s"],
            "resto_s": max(0.05, t["segundos"] - t["asr_s"] - t["llm_s"] - t["tts_s"]),
        }
        for t in turnos
    ]


def _transcripcion(rng: random.Random, indice: int, p_error: float) -> str:
    if rng.random() < p_error:
        return rng.choice(datos.TRANSCRIPCIONES_CON_ERROR[indice])
    return FRASES[indice]


def _respuesta(rng: random.Random, indice: int) -> str:
    limpias, inventadas, p_inventa = datos.RESPUESTAS[indice]
    if inventadas and rng.random() < p_inventa:
        return rng.choice(inventadas)
    return rng.choice(limpias)


# --- Demo 1 (y las frases que alimentan el demo 4) ----------------------------------


def _sesion_sintetica(
    rng: random.Random,
    persona: str,
    inicio: str,
    frases: list[tuple[str, str, str]],
    variedad: str,
    muestras: list[dict],
) -> tuple[list[dict], list[dict]]:
    """Filas y turnos de una persona. `frases` trae (guion, transcripción del sistema, respuesta)."""
    from medicion import coincide

    filas, turnos = [], []
    momento = datetime.fromisoformat(inicio)
    for guion, sistema, respuesta in frases:
        identificador = _identificador(rng)
        tiempos = _tiempos(rng, rng.choice(muestras))
        momento += timedelta(seconds=tiempos["segundos"])
        veredicto = "si" if coincide(guion, sistema) else "no"
        filas.append(
            {
                "id": identificador,
                "persona": persona,
                "variedad": variedad,
                "guion": guion,
                "transcripcion_correcta": guion,
                "transcripcion_sistema": sistema,
                "correcta": veredicto,
                "correcta_automatica": veredicto,
                "audio": "",
                "sintetica": True,
            }
        )
        turnos.append(
            {
                "id": identificador,
                "demo": 1,
                "persona": persona,
                "guion": guion,
                "entrada": "voz",
                "transcripcion": sistema,
                "respuesta": respuesta,
                **tiempos,
                "audio": "",
                "ts": momento.isoformat(timespec="seconds"),
                "sintetica": True,
            }
        )
        momento += timedelta(seconds=rng.uniform(28, 65))
    return filas, turnos


def datos_demo1(rng: random.Random, *, permitir_local: bool = False) -> tuple[list[dict], list[dict]]:
    """Cuatro hablantes con las diez frases del guion, y cuarenta frases en palenquero."""
    from demo4_wer.wer import _variedad_demo1

    fuente1 = REAL / "demo1" / "filas.json" if permitir_local else EJEMPLO / "semillas" / "demo1" / "filas.json"
    if permitir_local and not fuente1.is_file():
        fuente1 = EJEMPLO / "semillas" / "demo1" / "filas.json"
    filas_reales = _leer_json(fuente1) if fuente1.is_file() else []
    turnos_path = fuente1.parent / "turnos.jsonl"
    if permitir_local and not turnos_path.is_file():
        turnos_path = REAL / "demo1" / "turnos.jsonl"
    turnos_reales = {
        t["id"]: t for t in (_leer_jsonl(turnos_path) if turnos_path.is_file() else []) if t.get("demo", 1) == 1
    }

    # De lo medido se conserva una frase por persona y por línea del guion: la primera.
    medidas: dict[tuple[str, int], dict] = {}
    palenquero_real = []
    for fila in filas_reales:
        if fila["id"] not in turnos_reales:
            continue
        if _variedad_demo1(fila) == "palenquero":
            palenquero_real.append(fila)
        elif fila.get("guion") in FRASES:
            medidas.setdefault((fila["persona"], FRASES.index(fila["guion"])), fila)

    costeno_real = list(medidas.values())
    if costeno_real and turnos_reales:
        primera = min(costeno_real, key=lambda f: turnos_reales[f["id"]]["ts"])
        muestras = _muestras_de_tiempo([turnos_reales[f["id"]] for f in costeno_real if f is not primera])
    else:
        muestras = [{"asr_s": 2.0, "llm_s": 2.5, "tts_s": 0.35, "resto_s": 0.55}]
    muestras_pal = _muestras_de_tiempo([turnos_reales[f["id"]] for f in palenquero_real]) if palenquero_real else muestras

    filas = [{**fila, "variedad": _variedad_demo1(fila)} for fila in costeno_real + palenquero_real]
    turnos = [{**turnos_reales[fila["id"]], "audio": ""} for fila in filas]

    sesiones = [(nombre, *datos.HABLANTES_EXTRA[nombre]) for nombre in datos.HABLANTES_EXTRA]
    sesiones += datos.HABLANTES_COSTENO
    for persona, p_error, inicio in sesiones:
        faltan = [i for i in range(len(FRASES)) if (persona, i) not in medidas]
        frases = [(FRASES[i], _transcripcion(rng, i, p_error), _respuesta(rng, i)) for i in faltan]
        nuevas, nuevos = _sesion_sintetica(rng, persona, inicio, frases, "costeno", muestras)
        filas += nuevas
        turnos += nuevos

    for numero, (persona, inicio) in enumerate(datos.HABLANTES_PALENQUERO):
        frases = [
            (frase["texto"], datos.PALENQUERO_SISTEMA[i][numero], rng.choice(datos.RESPUESTAS_PALENQUERO))
            for i, frase in enumerate(FRASES_PALENQUERO)
        ]
        nuevas, nuevos = _sesion_sintetica(rng, persona, inicio, frases, "palenquero", muestras_pal)
        filas += nuevas
        turnos += nuevos

    cuando = {t["id"]: datetime.fromisoformat(t["ts"]) for t in turnos}
    filas.sort(key=lambda f: cuando[f["id"]])
    turnos.sort(key=lambda t: cuando[t["id"]])
    return filas, turnos


# --- Demo 2 -------------------------------------------------------------------------


def datos_demo2(rng: random.Random, muestras: list[dict]) -> list[dict]:
    """Sesión de tres teléfonos a la vez, sin internet.

    Cada persona hace diez consultas. El reconocimiento, el modelo y la síntesis atienden
    una consulta a la vez, como en el servidor; cuando coinciden, la segunda espera.
    """
    inicio = datetime.fromisoformat(datos.SESION_DEMO2)
    libre = {"asr": inicio, "llm": inicio, "tts": inicio}
    # (momento en que llega la consulta, persona, número de consulta)
    cola = [(inicio + timedelta(seconds=rng.uniform(0, 2.5)), persona, 0) for persona in datos.USUARIOS_DEMO2]
    filas = []
    while cola:
        cola.sort()
        llega, persona, numero = cola.pop(0)
        base = rng.choice(muestras)
        etapas = _tiempos(rng, base)
        momento = llega + timedelta(seconds=base["resto_s"])
        for etapa, clave in (("asr", "asr_s"), ("llm", "llm_s"), ("tts", "tts_s")):
            arranca = max(momento, libre[etapa])
            # Las tres etapas comparten el mismo procesador: si otra está ocupada, esta va más lenta.
            ocupadas = sum(1 for otra, hasta in libre.items() if otra != etapa and hasta > arranca)
            etapas[clave] = round(etapas[clave] * (1 + datos.FRENO_POR_ETAPA_OCUPADA * ocupadas), 3)
            momento = arranca + timedelta(seconds=etapas[clave])
            libre[etapa] = momento
        indice = numero % len(FRASES)
        filas.append(
            {
                "id": _identificador(rng),
                "demo": 2,
                "persona": persona,
                "guion": FRASES[indice],
                "entrada": "voz",
                "transcripcion": _transcripcion(rng, indice, 0.5),
                "respuesta": _respuesta(rng, indice),
                "segundos": round((momento - llega).total_seconds(), 3),
                "asr_s": etapas["asr_s"],
                "llm_s": etapas["llm_s"],
                "tts_s": etapas["tts_s"],
                "audio": "",
                "ts": momento.isoformat(timespec="seconds"),
                "ts_inicio": llega.isoformat(timespec="milliseconds"),
                "ts_fin": momento.isoformat(timespec="milliseconds"),
                "internet": False,
                "sintetica": True,
            }
        )
        if numero + 1 < 10:
            # Oye la respuesta, piensa y dicta la siguiente consulta.
            cola.append((momento + timedelta(seconds=rng.uniform(*datos.PAUSA_DEMO2_S)), persona, numero + 1))
    filas.sort(key=lambda f: f["ts_fin"])
    return filas


# --- Demo 4: prueba por escrito -----------------------------------------------------


def traduccion_de_ejemplo(medida: dict | None) -> dict | None:
    """La prueba por escrito con la referencia comercial corrida. Las cifras del modelo local son las medidas."""
    if not medida or not medida.get("direcciones"):
        return None
    ejemplo = copy.deepcopy(medida)
    referencia = datos.REFERENCIA_TRADUCCION
    ejemplo["por_verificar"] = None
    ejemplo.setdefault("fuente", {})["permiso"] = "Dato de ejemplo: el permiso de los autores sigue pendiente."
    ejemplo.setdefault("sistemas", {})["referencia"] = dict(referencia["sistema"])
    for direccion in ejemplo["direcciones"]:
        direccion["referencia"] = dict(referencia[direccion["clave"]])
    for verso in ejemplo.get("ejemplos") or []:
        verso["referencia"] = list(referencia["versos"][verso["direccion"]])
    ejemplo["sintetica"] = "Las cifras y los versos de la referencia comercial son de ejemplo; no se ha corrido."
    return ejemplo


# --- Notas --------------------------------------------------------------------------


def marcar(doc: dict, _demo_id: int) -> dict:
    """Formato del juego de ejemplo: antetítulo del proyecto, sin «Nota técnica» ni pie final."""
    titulo = doc["titulo"].removeprefix("Nota técnica · ")
    pie_pagina = doc["pie_pagina"]
    if MARCA_PAGINA:
        pie_pagina = f"{pie_pagina} · {MARCA_PAGINA}"
    return {
        **doc,
        "titulo": titulo,
        "antetitulo": ANTETITULO,
        "pie_pagina": pie_pagina,
        "pie": "",
    }


def _hoja(doc: dict, nombre: str) -> str:
    """Página HTML suelta de la nota, con sus estilos dentro. El PDF queda a su lado, con el mismo nombre."""
    from html import escape

    from interfaz.documento import a_html
    from interfaz.informe_export import ESTATICOS

    estilos = (ESTATICOS / "nota.css").read_text(encoding="utf-8")
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(doc["titulo"])} · {MARCA_PAGINA}</title>
  <style>{estilos}</style>
</head>
<body class="hoja-nota">
  <nav class="barra-acciones" aria-label="Acciones de la nota">
    <a href="/medicion-base">Volver a la medición base</a>
    <a href="{escape(nombre)}.pdf">Ver PDF</a>
    <a href="{escape(nombre)}.pdf?descargar=1">Descargar PDF</a>
    <button type="button" onclick="window.print()">Imprimir</button>
  </nav>
  <main>
  {a_html(doc)}
  </main>
</body>
</html>
"""


def informes(destino: Path = EJEMPLO) -> dict[int, dict]:
    """Escribe los datos del ejemplo y calcula sus cinco informes con el código de los demos."""
    import demo4_wer.calcular as calcular
    import interfaz.demo1_informe as demo1
    import interfaz.demo2_informe as demo2
    import interfaz.rutas_resultados as rutas
    from demo4_wer.traduccion import leer_publico

    rng = random.Random(SEMILLA)
    base = destino / "resultados"

    filas, turnos = datos_demo1(rng)
    _escribir_json(base / "demo1" / "filas.json", filas)
    _escribir_jsonl(base / "demo1" / "turnos.jsonl", turnos)

    costeno = [t for t in turnos if t.get("guion") in FRASES]
    muestras_voz = _muestras_de_tiempo(costeno[1:]) if len(costeno) > 1 else [{"asr_s": 2.0, "llm_s": 2.5, "tts_s": 0.35, "resto_s": 0.55}]
    consultas = datos_demo2(rng, muestras_voz)
    _escribir_jsonl(base / "demo2" / "turnos.jsonl", consultas)
    _escribir_json(
        base / "demo2" / "consumo.json",
        {**datos.CONSUMO_DEMO2, "fecha": consultas[-1]["ts"], "sintetica": True},
    )
    _escribir_json(
        destino / "enlaces.json",
        {"video": {str(n): datos.VIDEO_CARPETA for n in range(1, 6)}},
    )

    salida: dict[int, dict] = {}
    demo2.TURNOS = base / "demo2" / "turnos.jsonl"
    demo2.CONSUMO = base / "demo2" / "consumo.json"
    sin_local = destino / ".sin-medicion-local"
    with _redirigir((rutas, "MEDIDOS", sin_local), (rutas, "PUBLICO", base)):
        salida[1] = demo1.construir_informe_demo1({"fecha": max(t["ts"] for t in turnos if t.get("guion") in FRASES)})
        salida[2] = demo2.construir_informe_demo2()
    sin_carpeta = base / "demo4" / "sin-corpus"
    salida[4] = calcular.medir(base / "demo1" / "filas.json", {"costeno": sin_carpeta, "palenquero": sin_carpeta})
    salida[4]["fecha"] = FECHA_CALCULO_DEMO4
    traduccion = traduccion_de_ejemplo(leer_publico())
    if traduccion:
        salida[4]["traduccion"] = traduccion
        _escribir_json(base / "demo4" / "traduccion.json", traduccion)
    else:
        salida[4].pop("traduccion", None)
    for demo_id in sorted(SINTETICOS):
        _escribir_json(base / f"demo{demo_id}" / "informe.json", {**salida[demo_id], "sintetica": True})

    # Los demos 3 y 5 ya están completos: el ejemplo muestra sus cifras medidas, sin tocarlas.
    for demo_id in (3, 5):
        semilla = EJEMPLO / "semillas" / f"demo{demo_id}" / "informe.json"
        local = REAL / f"demo{demo_id}" / "informe.json"
        if local.is_file() and os.environ.get("EJEMPLO_INFORMES_LOCAL"):
            salida[demo_id] = _leer_json(local)
        elif semilla.is_file():
            salida[demo_id] = _leer_json(semilla)
        else:
            raise FileNotFoundError(f"Falta {semilla} (o medición local en resultados/demo{demo_id}/)")
    for demo_id, informe in salida.items():
        _publicar_demo(base, demo_id, informe)
    return salida


def _publicar_demo(base: Path, demo_id: int, informe: dict) -> None:
    """Deja informe vigente e historial mínimo en ejemplo/resultados/."""
    from interfaz.informes import _id_corrida, estado_corrida, resumen_de_informe

    carpeta = base / f"demo{demo_id}"
    carpeta.mkdir(parents=True, exist_ok=True)
    datos = {**informe, "demo": demo_id}
    datos.setdefault("fecha", datetime.now().astimezone().isoformat(timespec="seconds"))
    corrida_id = datos.get("corrida_id") or _id_corrida(str(datos["fecha"]))
    datos["corrida_id"] = corrida_id
    _escribir_json(carpeta / "informe.json", datos)
    historial = carpeta / "historial"
    historial.mkdir(parents=True, exist_ok=True)
    _escribir_json(historial / f"{corrida_id}.json", datos)
    entrada = {
        "id": corrida_id,
        "fecha": datos["fecha"],
        "resumen": resumen_de_informe(demo_id, datos),
        "estado": estado_corrida(demo_id, datos),
    }
    _escribir_json(historial / "indice.json", [entrada])


def documentos(destino: Path = EJEMPLO) -> dict[int, dict]:
    """Las cinco notas del ejemplo, ya marcadas."""
    import interfaz.enlaces as enlaces
    import interfaz.notas as notas

    calculados = informes(destino)
    docs: dict[int, dict] = {}
    with _redirigir((enlaces, "ARCHIVO", destino / "enlaces.json")):
        for demo_id in sorted(calculados):
            if demo_id in SINTETICOS:
                # Los enlaces a datos de la nota se resuelven dentro de la carpeta del ejemplo.
                with _redirigir((notas, "RAIZ", destino)):
                    doc = notas.documento(demo_id, calculados[demo_id])
            else:
                doc = notas.documento(demo_id, calculados[demo_id])
            docs[demo_id] = marcar(doc, demo_id)
    return docs


def resumen_markdown(filas: list[dict]) -> str:
    from interfaz.entregar import tabla_viabilidad

    lineas = [
        "# : los cinco demos con la muestra completa",
        "",
        "No es una medición. Muestra cómo se verían las notas técnicas y la tabla de viabilidad al completar el "
        "protocolo. Los demos 1, 2 y 4 combinan lo medido con datos sintéticos que siguen su tendencia; los demos "
        "3 y 5 traen sus cifras medidas. Lo genera `python -m ejemplo.generar`.",
        "",
        "Las cifras que valen para el documento técnico son las de `entregables/RESUMEN-PARA-DOCUMENTO-TECNICO.md`.",
        "",
        "## Palenquero",
        "",
        datos.AUTORIZACION_PALENQUERO,
        "",
        "## Viabilidad: qué pregunta responde cada demo",
        "",
        *tabla_viabilidad(filas, RESPUESTA_DE_EJEMPLO),
        "",
        "## Estado de cada nota en el ejemplo",
        "",
    ]
    for fila in filas:
        origen = "con datos sintéticos" if fila["demo"] in SINTETICOS else "cifras medidas"
        lineas.append(
            f"- **Demo {fila['demo']}. {fila['titulo']}** ({origen}; {fila['paginas']} páginas): "
            f"{fila['etiqueta']}. {fila['resumen']}"
        )
    lineas.append("")
    return "\n".join(lineas)


def generar(destino: Path = EJEMPLO) -> list[dict]:
    """Escribe los datos, las notas (PDF, HTML y Markdown), el resumen y el índice del ejemplo."""
    from interfaz.catalogo import DEMOS
    from interfaz.documento import ETIQUETA_ESTADO, a_markdown, a_pdf, texto_plano
    from interfaz.notas import ARCHIVO_NOTA

    carpeta = destino / "notas"
    carpeta.mkdir(parents=True, exist_ok=True)
    filas = []
    for demo_id, doc in documentos(destino).items():
        nombre = f"Ejemplo_{ARCHIVO_NOTA[demo_id]}"
        pdf, paginas = a_pdf(doc)
        (carpeta / f"{nombre}.pdf").write_bytes(pdf)
        (carpeta / f"{nombre}.md").write_text(a_markdown(doc), encoding="utf-8")
        (carpeta / f"{nombre}.html").write_text(_hoja(doc, nombre), encoding="utf-8")
        clase = doc["estado"]["clase"]
        filas.append(
            {
                "demo": demo_id,
                "titulo": DEMOS[demo_id]["titulo"],
                "estado": clase,
                "etiqueta": ETIQUETA_ESTADO[clase],
                "resumen": texto_plano(doc["estado"]["texto"]),
                "pregunta": doc["pregunta"],
                "respuesta": texto_plano(doc["respuesta"]),
                "justifica": doc["justifica"],
                "paginas": paginas,
                "sintetico": demo_id in SINTETICOS,
                "archivo": nombre,
            }
        )
    (destino / "RESUMEN-DE-EJEMPLO.md").write_text(resumen_markdown(filas), encoding="utf-8")
    _escribir_json(destino / "indice.json", filas)
    return filas


def main() -> int:
    filas = generar()
    print("Juego de ejemplo (no es una medición)\n")
    print(f"{'Demo':<42} {'Estado':<20} {'Páginas':>7}  Cifras")
    for fila in filas:
        nombre = f"{fila['demo']}. {fila['titulo']}"
        origen = "con datos sintéticos" if fila["sintetico"] else "medidas"
        print(f"{nombre:<42} {fila['etiqueta']:<20} {fila['paginas']:>7}  {origen}")
    print()
    for fila in filas:
        print(f"Demo {fila['demo']}: {fila['respuesta']}")
    print(f"\nNotas: {(EJEMPLO / 'notas').relative_to(RAIZ)}/   Resumen: ejemplo/RESUMEN-DE-EJEMPLO.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

