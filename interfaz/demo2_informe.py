"""Informe del demo 2 (IA completa sin internet) a partir de los turnos de voz medidos.

El criterio oficial tiene tres partes y las tres se miden, no se declaran:
tres o más usuarios a la vez, respuesta de voz en menos de 10 s en promedio y sin internet.
Si falta alguna, el informe queda como parcial y dice cuál.
"""

from __future__ import annotations

import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path

from equipo import describir_equipo
from interfaz.catalogo import DEMOS

RAIZ = Path(__file__).resolve().parents[1]
DEMO2 = RAIZ / "resultados" / "demo2"
TURNOS = DEMO2 / "turnos.jsonl"
CONSUMO = DEMO2 / "consumo.json"

USUARIOS_MINIMOS = 3
SEGUNDOS_MAXIMOS = 10.0
CONSULTAS_POR_USUARIO = 10
# Dos turnos separados por más de este tiempo se consideran sesiones distintas.
PAUSA_ENTRE_SESIONES = timedelta(minutes=20)


def _leer_turnos() -> list[dict]:
    if not TURNOS.is_file():
        return []
    filas = []
    for linea in TURNOS.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea:
            continue
        try:
            filas.append(json.loads(linea))
        except json.JSONDecodeError:
            continue
    return filas


def _fecha(texto: str | None) -> datetime | None:
    if not texto:
        return None
    try:
        return datetime.fromisoformat(texto)
    except ValueError:
        return None


def _intervalo(fila: dict) -> tuple[datetime, datetime] | None:
    fin = _fecha(fila.get("ts_fin") or fila.get("ts"))
    if fin is None:
        return None
    inicio = _fecha(fila.get("ts_inicio"))
    if inicio is None:
        inicio = fin - timedelta(seconds=float(fila.get("segundos") or 0))
    return inicio, fin


def _ultima_sesion(filas: list[dict]) -> list[dict]:
    """Los turnos de la sesión más reciente, en orden."""
    con_fecha = [(intervalo, fila) for fila in filas if (intervalo := _intervalo(fila))]
    con_fecha.sort(key=lambda item: item[0][1])
    sesion: list[dict] = []
    anterior: datetime | None = None
    for (inicio, fin), fila in con_fecha:
        if anterior is not None and inicio - anterior > PAUSA_ENTRE_SESIONES:
            sesion = []
        sesion.append(fila)
        anterior = fin
    return sesion


def _pico_simultaneo(filas: list[dict]) -> int:
    """Máximo de personas distintas con una consulta en curso en el mismo instante."""
    marcas: list[tuple[datetime, int, str]] = []
    for fila in filas:
        intervalo = _intervalo(fila)
        if not intervalo:
            continue
        persona = str(fila.get("persona") or "sin-nombre")
        marcas.append((intervalo[0], 1, persona))
        marcas.append((intervalo[1], -1, persona))
    # En un empate de reloj, primero se cierran las consultas que terminan.
    marcas.sort(key=lambda item: (item[0], item[1]))
    activos: dict[str, int] = {}
    pico = 0
    for _momento, cambio, persona in marcas:
        activos[persona] = activos.get(persona, 0) + cambio
        if activos[persona] <= 0:
            activos.pop(persona, None)
        pico = max(pico, len(activos))
    return pico


def _consumo() -> dict | None:
    if not CONSUMO.is_file():
        return None
    try:
        datos = json.loads(CONSUMO.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    reposo = datos.get("reposo_w")
    carga = datos.get("carga_w")
    if not isinstance(reposo, (int, float)) and not isinstance(carga, (int, float)):
        return None
    return {
        "reposo_w": reposo if isinstance(reposo, (int, float)) else None,
        "carga_w": carga if isinstance(carga, (int, float)) else None,
        "instrumento": str(datos.get("instrumento") or "").strip(),
        "fecha": str(datos.get("fecha") or datos.get("ts") or "").strip(),
    }


def guardar_consumo(cuerpo: dict) -> dict:
    """Guarda la lectura del medidor de consumo. Los vatios los lee una persona; no se estiman."""

    def vatios(clave: str) -> float | None:
        valor = cuerpo.get(clave)
        if valor in (None, ""):
            return None
        numero = float(str(valor).replace(",", "."))
        if not 0 < numero < 5000:
            raise ValueError("el consumo en vatios debe estar entre 0 y 5000")
        return round(numero, 1)

    reposo, carga = vatios("reposo_w"), vatios("carga_w")
    if reposo is None and carga is None:
        raise ValueError("falta al menos una lectura de consumo")
    datos = {
        "reposo_w": reposo,
        "carga_w": carga,
        "instrumento": str(cuerpo.get("instrumento") or "").strip()[:120],
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    DEMO2.mkdir(parents=True, exist_ok=True)
    CONSUMO.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return datos


def _modelos() -> dict:
    from interfaz.demo1_informe import _modelos as modelos_de_voz

    return modelos_de_voz()


def construir_informe_demo2(extra: dict | None = None) -> dict | None:
    filas = _leer_turnos()
    if not filas:
        return None
    meta = DEMOS[2]
    voz = [fila for fila in filas if fila.get("entrada") == "voz" and fila.get("segundos")]
    sesion = _ultima_sesion(voz)
    texto = [fila for fila in filas if fila.get("entrada") != "voz"]

    informe: dict = {
        "demo": 2,
        "titulo": meta["titulo"],
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "responsable": meta.get("responsable"),
        "equipo": describir_equipo(),
        "modelos": _modelos(),
        "usuarios_minimos": USUARIOS_MINIMOS,
        "segundos_maximos": SEGUNDOS_MAXIMOS,
        "consultas_por_usuario_protocolo": CONSULTAS_POR_USUARIO,
        "consultas_texto": len(texto),
        "consumo": _consumo(),
    }

    if not sesion:
        tiempos_texto = [float(fila["segundos"]) for fila in texto if fila.get("segundos")]
        informe.update(
            {
                "entrada": "texto",
                "consultas": len(texto),
                "consultas_voz": 0,
                "usuarios": 0,
                "usuarios_simultaneos": 0,
                "tiempo_promedio_s": round(statistics.fmean(tiempos_texto), 3) if tiempos_texto else None,
                "tiempo_maximo_s": round(max(tiempos_texto), 3) if tiempos_texto else None,
                "sin_internet": None,
                "criterios": {"usuarios": False, "tiempo": None, "sin_internet": None},
                "parcial": True,
                "faltantes": [
                    "Todavía no hay consultas por voz desde los teléfonos. Lo registrado es una "
                    "verificación por texto, que no cuenta para el criterio.",
                ],
                "por_usuario": [],
                "resumen_ejecutivo": (
                    f"Sin medición por voz todavía. Solo hay {len(texto)} consulta(s) de verificación por texto."
                ),
            }
        )
        if extra:
            informe.update({k: v for k, v in extra.items() if v is not None})
        return informe

    tiempos = [float(fila["segundos"]) for fila in sesion]
    personas: dict[str, list[float]] = {}
    for fila in sesion:
        personas.setdefault(str(fila.get("persona") or "sin-nombre"), []).append(float(fila["segundos"]))
    por_usuario = [
        {
            "usuario": persona,
            "consultas": len(valores),
            "promedio_s": round(statistics.fmean(valores), 3),
            "maximo_s": round(max(valores), 3),
        }
        for persona, valores in sorted(personas.items())
    ]
    pico = _pico_simultaneo(sesion)
    promedio = statistics.fmean(tiempos)

    estados_red = [fila.get("internet") for fila in sesion]
    if any(estado is True for estado in estados_red):
        sin_internet: bool | None = False
    elif all(estado is False for estado in estados_red):
        sin_internet = True
    else:
        sin_internet = None  # turnos anteriores a que se registrara la red

    criterios = {
        "usuarios": pico >= USUARIOS_MINIMOS,
        "tiempo": promedio < SEGUNDOS_MAXIMOS,
        "sin_internet": sin_internet,
    }
    faltantes: list[str] = []
    if not criterios["usuarios"]:
        faltantes.append(
            f"Se midieron {pico} usuario(s) a la vez; el criterio pide al menos {USUARIOS_MINIMOS}."
        )
    if not criterios["tiempo"]:
        faltantes.append(
            f"El promedio fue de {promedio:.2f} s; el criterio pide menos de {SEGUNDOS_MAXIMOS:.0f} s."
        )
    if sin_internet is False:
        con_red = sum(1 for estado in estados_red if estado is True)
        faltantes.append(
            f"El equipo tenía salida a internet en {con_red} de {len(sesion)} consultas. "
            "Hay que desconectar el router de internet y repetir."
        )
    elif sin_internet is None:
        faltantes.append("No quedó registrado si el equipo tenía internet durante la sesión. Hay que repetirla.")
    cortos = [item["usuario"] for item in por_usuario if item["consultas"] < CONSULTAS_POR_USUARIO]
    cobertura_completa = not cortos and len(por_usuario) >= USUARIOS_MINIMOS

    def promedio_de(clave: str) -> float | None:
        valores = [float(fila[clave]) for fila in sesion if isinstance(fila.get(clave), (int, float))]
        return round(statistics.fmean(valores), 3) if valores else None

    intervalos = [intervalo for fila in sesion if (intervalo := _intervalo(fila))]
    cumple = all(valor is True for valor in criterios.values())
    informe.update(
        {
            # La fecha del informe es la de la medición, no la del momento en que se abre.
            "fecha": max(item[1] for item in intervalos).isoformat(timespec="seconds"),
            "entrada": "voz",
            "consultas": len(sesion),
            "consultas_voz": len(sesion),
            "usuarios": len(por_usuario),
            "usuarios_simultaneos": pico,
            "tiempo_promedio_s": round(promedio, 3),
            "tiempo_maximo_s": round(max(tiempos), 3),
            "tiempo_mediana_s": round(statistics.median(tiempos), 3),
            "etapas_promedio": {
                "asr_s": promedio_de("asr_s"),
                "llm_s": promedio_de("llm_s"),
                "tts_s": promedio_de("tts_s"),
            },
            "sesion_inicio": min(item[0] for item in intervalos).isoformat(timespec="seconds"),
            "sesion_fin": max(item[1] for item in intervalos).isoformat(timespec="seconds"),
            "por_usuario": por_usuario,
            "sin_internet": sin_internet,
            "criterios": criterios,
            "criterio_10s": criterios["tiempo"],
            "cobertura_completa": cobertura_completa,
            "usuarios_con_menos_consultas": cortos,
            "faltantes": faltantes,
            "parcial": not cumple,
        }
    )
    # criterio_cumplido solo se escribe cuando las tres partes están medidas y cumplen.
    if cumple:
        informe["criterio_cumplido"] = True
    red = {True: "sin internet", False: "con internet", None: "red sin registrar"}[sin_internet]
    informe["resumen_ejecutivo"] = (
        f"{len(sesion)} consultas por voz de {len(por_usuario)} usuario(s), hasta {pico} a la vez, {red}. "
        f"Tiempo de respuesta promedio {promedio:.2f} s y máximo {max(tiempos):.2f} s."
    )
    if extra:
        informe.update({k: v for k, v in extra.items() if v is not None})
    return informe
