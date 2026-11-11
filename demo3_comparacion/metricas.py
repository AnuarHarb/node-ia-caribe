"""Definiciones de la medición del demo 3.

Calidad de una respuesta: promedio de exactitud, completitud, tono y utilidad.
Calidad de un camino en una tarea: promedio de esa nota entre los dos calificadores.
Tarea comparable: la diferencia absoluta entre los dos caminos es de un punto o menos.
Kappa de Cohen: acuerdo entre los dos calificadores, sin ponderar, por cada dimensión,
sobre las respuestas (tarea × camino). El kappa cuadrático se informa aparte.
"""

from __future__ import annotations

from collections import Counter

DIMENSIONES = ("exactitud", "completitud", "tono", "utilidad")
CAMINOS = ("local", "referencia")


def cohen_kappa(serie_a: list[int], serie_b: list[int]) -> float:
    if len(serie_a) == 0 or len(serie_a) != len(serie_b):
        raise ValueError("las dos series deben tener la misma longitud y no estar vacías")
    n = len(serie_a)
    categorias = sorted(set(serie_a) | set(serie_b))
    acuerdo = sum(x == y for x, y in zip(serie_a, serie_b)) / n
    conteo_a, conteo_b = Counter(serie_a), Counter(serie_b)
    azar = sum((conteo_a[categoria] / n) * (conteo_b[categoria] / n) for categoria in categorias)
    if azar == 1:
        return 1.0
    return (acuerdo - azar) / (1 - azar)


def kappa_cuadratico(serie_a: list[int], serie_b: list[int], categorias: range = range(1, 6)) -> float:
    if len(serie_a) == 0 or len(serie_a) != len(serie_b):
        raise ValueError("las dos series deben tener la misma longitud y no estar vacías")
    cats = list(categorias)
    indice = {categoria: i for i, categoria in enumerate(cats)}
    k = len(cats)
    n = len(serie_a)
    observado = [[0.0] * k for _ in range(k)]
    for nota_a, nota_b in zip(serie_a, serie_b):
        observado[indice[nota_a]][indice[nota_b]] += 1
    margen_a = [sum(observado[i]) for i in range(k)]
    margen_b = [sum(observado[i][j] for i in range(k)) for j in range(k)]
    esperado = [[margen_a[i] * margen_b[j] / n for j in range(k)] for i in range(k)]

    def peso(i: int, j: int) -> float:
        return ((i - j) / (k - 1)) ** 2

    numerador = sum(peso(i, j) * observado[i][j] for i in range(k) for j in range(k))
    denominador = sum(peso(i, j) * esperado[i][j] for i in range(k) for j in range(k))
    if denominador == 0:
        return 1.0
    return 1 - numerador / denominador


def _media(valores: list[float]) -> float:
    if not valores:
        raise ValueError("no hay valores")
    return sum(valores) / len(valores)


def calidad_respuesta(puntaje: dict) -> float:
    return _media([float(puntaje[dimension]) for dimension in DIMENSIONES])


def calcular(clave: dict, calificaciones: list[dict], generaciones: dict | None = None) -> dict:
    if len(calificaciones) != 2:
        return {
            "estado": "pendiente",
            "motivo": "hacen falta las dos calificaciones humanas",
            "calificadores": [item.get("calificador", "") for item in calificaciones],
        }
    paquete = clave["paquete"]
    for calificacion in calificaciones:
        if calificacion.get("paquete") != paquete:
            raise ValueError("una calificación corresponde a otro paquete de respuestas")

    por_calificador = []
    for calificacion in calificaciones:
        indice = {}
        for puntaje in calificacion["puntajes"]:
            indice[(puntaje["id"], puntaje["respuesta"])] = puntaje
        por_calificador.append(indice)

    asignacion = clave["asignacion"]
    tareas = []
    faltantes = []
    for tarea_id, mapa in asignacion.items():
        notas = {}
        completa = True
        for camino in CAMINOS:
            letra = next(letra for letra, nombre in mapa.items() if nombre == camino)
            notas_camino = []
            for indice in por_calificador:
                puntaje = indice.get((tarea_id, letra))
                if puntaje is None or any(dimension not in puntaje for dimension in DIMENSIONES):
                    completa = False
                    break
                notas_camino.append(calidad_respuesta(puntaje))
            notas[camino] = _media(notas_camino) if completa else None
        if not completa:
            faltantes.append(tarea_id)
            continue
        diferencia = abs(notas["local"] - notas["referencia"])
        tareas.append(
            {
                "id": tarea_id,
                "local": round(notas["local"], 4),
                "referencia": round(notas["referencia"], 4),
                "diferencia": round(diferencia, 4),
                "comparable": diferencia <= 1,
            }
        )

    kappas = {}
    for dimension in DIMENSIONES:
        serie_a = []
        serie_b = []
        for tarea_id, mapa in asignacion.items():
            for letra in ("A", "B"):
                primero = por_calificador[0].get((tarea_id, letra))
                segundo = por_calificador[1].get((tarea_id, letra))
                if not primero or not segundo:
                    continue
                if dimension not in primero or dimension not in segundo:
                    continue
                serie_a.append(int(primero[dimension]))
                serie_b.append(int(segundo[dimension]))
        if serie_a:
            kappas[dimension] = {
                "cohen": round(cohen_kappa(serie_a, serie_b), 4),
                "cuadratico": round(kappa_cuadratico(serie_a, serie_b), 4),
                "n": len(serie_a),
            }

    resultado = {
        "estado": "calculado" if tareas else "incompleto",
        "paquete": paquete,
        "calificadores": [item.get("calificador", "") for item in calificaciones],
        "tareas_calificadas": len(tareas),
        "tareas_incompletas": faltantes,
        "calidad_promedio": {
            camino: round(_media([tarea[camino] for tarea in tareas]), 4) for camino in CAMINOS
        }
        if tareas
        else {},
        "porcentaje_comparables": round(
            100 * sum(1 for tarea in tareas if tarea["comparable"]) / len(tareas),
            2,
        )
        if tareas
        else None,
        "kappa": kappas,
        "kappa_cohen_promedio": round(_media([item["cohen"] for item in kappas.values()]), 4)
        if kappas
        else None,
        "por_tarea": tareas,
    }
    if generaciones:
        resultado["tiempo_y_costo"] = tiempos_y_costos(generaciones)
    return resultado


def _cli() -> int:
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Calcula calidad, porcentaje comparable y kappa.")
    parser.add_argument("clave", type=Path)
    parser.add_argument("calificaciones", nargs=2, type=Path)
    parser.add_argument("--generaciones", type=Path)
    args = parser.parse_args()
    clave = json.loads(args.clave.read_text(encoding="utf-8"))
    calificaciones = [json.loads(path.read_text(encoding="utf-8")) for path in args.calificaciones]
    generaciones = None
    if args.generaciones:
        generaciones = json.loads(args.generaciones.read_text(encoding="utf-8"))
    resultado = calcular(clave, calificaciones, generaciones)
    destino = args.clave.parent / "metricas.json"
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    visible = {llave: resultado[llave] for llave in resultado if llave != "por_tarea"}
    print(json.dumps(visible, ensure_ascii=False, indent=2))
    print(destino)
    return 0 if resultado.get("estado") == "calculado" else 1


if __name__ == "__main__":
    raise SystemExit(_cli())


def tiempos_y_costos(generaciones: dict) -> dict:
    resumen = {}
    for camino in CAMINOS:
        segundos = []
        costos = []
        for item in generaciones.values():
            dato = item.get(camino)
            if not dato:
                continue
            if dato.get("segundos") is not None:
                segundos.append(float(dato["segundos"]))
            if dato.get("costo_usd") is not None:
                costos.append(float(dato["costo_usd"]))
        resumen[camino] = {
            "n": len(segundos),
            "tiempo_promedio_s": round(_media(segundos), 3) if segundos else None,
            "tiempo_maximo_s": round(max(segundos), 3) if segundos else None,
            "costo_promedio_usd": round(_media(costos), 6) if costos and len(costos) == len(segundos) else None,
        }
    return resumen
