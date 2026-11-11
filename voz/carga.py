"""Mide tiempos con varias consultas a la vez contra el servidor ya encendido.

La cifra oficial del demo 2 sale de consultas por voz, con el router desconectado
de internet. Una corrida de solo texto queda marcada como parcial.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import httpx

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "resultados" / "demo2"
FRASES = [
    "¿A qué horas atienden hoy en la secretaría de hacienda?",
    "Necesito un turno para el Sisbén.",
    "¿Dónde queda la oficina del predial?",
    "¿Hasta qué hora reciben el pago del impuesto?",
]


def una(base: str, indice: int, texto: str) -> dict:
    inicio = time.perf_counter()
    respuesta = httpx.post(
        f"{base}/api/turno",
        json={"demo": 2, "persona": f"usuario-{indice + 1}", "texto": texto, "guion": texto},
        timeout=180,
    )
    reloj = round(time.perf_counter() - inicio, 3)
    respuesta.raise_for_status()
    cuerpo = respuesta.json()
    cuerpo.pop("audio_b64", None)
    cuerpo["reloj_cliente_s"] = reloj
    return cuerpo


def main() -> int:
    parser = argparse.ArgumentParser(description="Carga simultánea del demo 2.")
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    parser.add_argument("--usuarios", type=int, default=3)
    parser.add_argument("--cada-uno", type=int, default=1)
    args = parser.parse_args()
    trabajos = [
        (indice, FRASES[(indice) % len(FRASES)])
        for _ in range(args.cada_uno)
        for indice in range(args.usuarios)
    ]
    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.usuarios) as pool:
        resultados = list(pool.map(lambda item: una(args.url, item[0], item[1]), trabajos))
    pared = round(time.perf_counter() - inicio, 3)
    tiempos = [item["segundos"] for item in resultados]
    red = httpx.get(f"{args.url}/api/red", timeout=5).json()
    informe = {
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "entrada": "texto",
        "advertencia": "Esta corrida no usa voz. Sirve para ver la cola del modelo. El criterio del demo 2 se mide con las consultas por voz y el router desconectado.",
        "usuarios_simultaneos": args.usuarios,
        "consultas": len(resultados),
        "tiempo_promedio_s": round(statistics.fmean(tiempos), 3),
        "tiempo_maximo_s": round(max(tiempos), 3),
        "pared_s": pared,
        "internet": red.get("internet"),
        "consumo_w": None,
        "consultas_detalle": resultados,
    }
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "carga.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"{informe['usuarios_simultaneos']} usuarios, promedio {informe['tiempo_promedio_s']} s, "
        f"máximo {informe['tiempo_maximo_s']} s, internet {informe['internet']}"
    )
    print("Parcial: entrada de texto, no de voz.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
