"""Arma el paquete ciego y la clave para poder desblindar después."""

from __future__ import annotations

import hashlib
import json
import random

from demo3_comparacion.tareas import TAREAS

SISTEMA = (
    "Eres un asistente de apoyo a una entidad pública del Caribe colombiano. "
    "Esta es una prueba de laboratorio con datos ficticios. "
    "Responde en español claro. No inventes datos que no estén en la entrada. "
    "Si falta un dato, dilo. Sigue al pie de la letra el formato que pide la instrucción."
)


def mensaje_de(tarea: dict) -> str:
    return f"{tarea['instruccion']}\n\nEntrada:\n{tarea['entrada']}"


def _canon(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def construir_paquete(respuestas: dict[str, dict], semilla: int, modelo_local: str, modelo_referencia: str) -> tuple[dict, dict]:
    tareas_ciegas = []
    asignacion = {}
    for tarea in TAREAS:
        par = respuestas[tarea["id"]]
        rng = random.Random(f"{semilla}:{tarea['id']}")
        if rng.random() < 0.5:
            mapa = {"A": "local", "B": "referencia"}
        else:
            mapa = {"A": "referencia", "B": "local"}
        textos = {"local": par["local"], "referencia": par["referencia"]}
        tareas_ciegas.append(
            {
                "id": tarea["id"],
                "tipo": tarea["tipo"],
                "instruccion": tarea["instruccion"],
                "entrada": tarea["entrada"],
                "respuesta_a": textos[mapa["A"]],
                "respuesta_b": textos[mapa["B"]],
            }
        )
        asignacion[tarea["id"]] = mapa
    paquete = hashlib.sha256(_canon(tareas_ciegas).encode("utf-8")).hexdigest()
    ciego = {
        "paquete": paquete,
        "aviso": "Las respuestas están marcadas como A y B. No se indica qué sistema escribió cada una.",
        "tareas": tareas_ciegas,
    }
    clave = {
        "paquete": paquete,
        "semilla": semilla,
        "modelo_local": modelo_local,
        "modelo_referencia": modelo_referencia,
        "asignacion": asignacion,
    }
    return ciego, clave
