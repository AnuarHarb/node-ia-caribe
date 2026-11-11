"""Corrida de laboratorio del demo 5: dos agentes, bloqueo, auditoría y 11 pruebas."""

from __future__ import annotations

import csv
import html
import json
import shutil
import unittest
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import os

from demo5_agentes.entidades import ALCALDIA, GOBERNACION, RUTA_SECRETO_GOBERNACION
from demo5_agentes.nodo import AccesoDenegado, Nodo
from demo5_agentes.test_aislamiento import Aislamiento, SECRETO
from equipo import describir_equipo, texto_equipo

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "resultados" / "demo5"


def correr_pruebas() -> list[dict]:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Aislamiento)
    filas = []
    for prueba in suite:
        resultado = unittest.TestResult()
        prueba.run(resultado)
        nombre = prueba.id().split(".")[-1]
        esperado = prueba.shortDescription() or ""
        if resultado.wasSuccessful():
            obtenido = "pasó"
        else:
            detalle = resultado.failures + resultado.errors
            mensaje = detalle[0][1].strip().splitlines()[-1] if detalle else "falló"
            obtenido = "falló: " + mensaje
        filas.append({"prueba": nombre, "esperado": esperado, "obtenido": obtenido})
    return filas


def corrida_visible(
    entorno: Path,
    emitir: Callable[[str, str, dict | None], None] | None = None,
) -> dict:
    def _emit(tipo: str, mensaje: str, datos: dict | None = None) -> None:
        if emitir:
            emitir(tipo, mensaje, datos)

    if entorno.exists():
        shutil.rmtree(entorno)
    nodo = Nodo(entorno)
    alcaldia = nodo.abrir(ALCALDIA)
    gobernacion = nodo.abrir(GOBERNACION)
    _emit("paso", "Se abren dos cajas: alcaldía (Santa Marta) y gobernación (Atlántico).", {"fase": "inicio"})
    alcaldia.escribir(
        "pqrs/turno-1042.txt",
        "Radicado ficticio 1042. Petición de certificado de residencia. Barrio El Campito. Sin anexos.",
    )
    _emit(
        "caja",
        "Alcaldía escribe pqrs/turno-1042.txt",
        {"entidad": ALCALDIA, "accion": "escribir", "ruta": "pqrs/turno-1042.txt"},
    )
    gobernacion.escribir(
        "educacion/cupos-mahates.txt",
        SECRETO + " Lista ficticia de cupos escolares. No sale de esta entidad.",
    )
    _emit(
        "caja",
        "Gobernación escribe educacion/cupos-mahates.txt",
        {"entidad": GOBERNACION, "accion": "escribir", "ruta": "educacion/cupos-mahates.txt"},
    )
    alcaldia.escribir("pqrs/nota-de-trabajo.txt", "La alcaldía resume el turno 1042. Falta el recibo.")
    _emit(
        "caja",
        "Alcaldía escribe pqrs/nota-de-trabajo.txt",
        {"entidad": ALCALDIA, "accion": "escribir", "ruta": "pqrs/nota-de-trabajo.txt"},
    )
    gobernacion.escribir(
        "educacion/nota-de-trabajo.txt",
        "La gobernación revisa cupos ficticios de Mahates. Falta el grado.",
    )
    _emit(
        "caja",
        "Gobernación escribe educacion/nota-de-trabajo.txt",
        {"entidad": GOBERNACION, "accion": "escribir", "ruta": "educacion/nota-de-trabajo.txt"},
    )
    ruta_ajena = RUTA_SECRETO_GOBERNACION
    try:
        alcaldia.leer(ruta_ajena)
        bloqueo = {"bloqueado": False, "motivo": "", "ruta": ruta_ajena}
    except AccesoDenegado as exc:
        bloqueo = {"bloqueado": True, "motivo": exc.motivo, "ruta": exc.ruta}
    _emit(
        "bloqueo",
        "La alcaldía no puede leer el archivo de la gobernación.",
        bloqueo,
    )
    eventos = nodo.auditoria.eventos()
    for ev in eventos:
        _emit(
            "auditoria",
            f"Registro #{ev.get('n')}: {ev.get('resultado')} ({ev.get('accion')})",
            ev,
        )
    return {
        "bloqueo": bloqueo,
        "auditoria_integra": nodo.auditoria.integra(),
        "eventos": eventos,
    }


def guardar(filas: list[dict], visible: dict, equipo: dict) -> dict:
    SALIDA.mkdir(parents=True, exist_ok=True)
    pasa = sum(1 for fila in filas if fila["obtenido"] == "pasó")
    informe = {
        "demo": 5,
        "titulo": "Agentes aislados por entidad",
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "equipo": equipo,
        "datos": "ficticios",
        "internet": False,
        "pruebas_pasadas": pasa,
        "pruebas_total": len(filas),
        "criterio": "El acceso cruzado queda bloqueado y las 11 pruebas pasan.",
        "criterio_cumplido": visible["bloqueo"]["bloqueado"] and pasa == len(filas) and visible["auditoria_integra"],
        "bloqueo": visible["bloqueo"],
        "auditoria_integra": visible["auditoria_integra"],
        "filas": filas,
        "eventos": visible["eventos"],
    }
    (SALIDA / "informe.json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with (SALIDA / "pruebas.csv").open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=["prueba", "esperado", "obtenido"])
        escritor.writeheader()
        escritor.writerows(filas)
    (SALIDA / "informe.html").write_text(_html(informe), encoding="utf-8")
    (RAIZ / "notas").mkdir(exist_ok=True)
    (RAIZ / "notas" / "Demo-5_Agentes-aislados-por-entidad.md").write_text(
        _nota(informe),
        encoding="utf-8",
    )
    return informe


def _html(informe: dict) -> str:
    def e(valor: object) -> str:
        return html.escape(str(valor))

    filas = "\n".join(
        "<tr><td><code>{p}</code></td><td>{esp}</td><td>{obt}</td></tr>".format(
            p=e(fila["prueba"]),
            esp=e(fila["esperado"]),
            obt=e(fila["obtenido"]),
        )
        for fila in informe["filas"]
    )
    eventos = "\n".join(
        "<tr><td>{n}</td><td>{ent}</td><td>{acc}</td><td>{ruta}</td><td>{res}</td><td>{mot}</td></tr>".format(
            n=e(evento["n"]),
            ent=e(evento["entidad"]),
            acc=e(evento["accion"]),
            ruta=e(evento["ruta"]),
            res=e(evento["resultado"]),
            mot=e(evento["motivo"]),
        )
        for evento in informe["eventos"]
    )
    estado = "cumplido" if informe["criterio_cumplido"] else "no cumplido"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Demo 5 · Agentes aislados por entidad</title>
  <style>
    body {{ font-family: Palatino, "Iowan Old Style", serif; max-width: 54rem; margin: 2rem auto; padding: 0 1rem; color: #1c1c1c; line-height: 1.45; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border-bottom: 1px solid #ccc; text-align: left; vertical-align: top; padding: 0.4rem 0.5rem; }}
    code {{ font-family: ui-monospace, monospace; font-size: 0.9em; }}
    .estado {{ font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <p>Nodo IA Caribe · evidencia de laboratorio TRL 3</p>
    <h1>Agentes aislados por entidad</h1>
    <p>Fecha: {e(informe["fecha"])}<br>Equipo: {e(texto_equipo(informe["equipo"]))}</p>
    <p class="estado">Criterio {e(estado)}. Pruebas {e(informe["pruebas_pasadas"])} de {e(informe["pruebas_total"])}. Acceso cruzado bloqueado: {e(informe["bloqueo"]["bloqueado"])}. Auditoría íntegra: {e(informe["auditoria_integra"])}.</p>
  </header>
  <main>
    <section>
      <h2>Pruebas</h2>
      <table>
        <caption>Resultado de las 11 pruebas automatizadas</caption>
        <thead><tr><th>Prueba</th><th>Resultado esperado</th><th>Resultado obtenido</th></tr></thead>
        <tbody>
          {filas}
        </tbody>
      </table>
    </section>
    <section>
      <h2>Registro de auditoría de la corrida visible</h2>
      <p>La alcaldía intentó leer <code>{e(informe["bloqueo"]["ruta"])}</code>. Motivo: {e(informe["bloqueo"]["motivo"])}.</p>
      <table>
        <caption>Eventos, en orden, con cadena de hashes verificada</caption>
        <thead><tr><th>#</th><th>Entidad</th><th>Acción</th><th>Ruta</th><th>Resultado</th><th>Motivo</th></tr></thead>
        <tbody>
          {eventos}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


def _nota(informe: dict) -> str:
    filas = "\n".join(
        f"| {fila['prueba']} | {fila['esperado']} | {fila['obtenido']} |"
        for fila in informe["filas"]
    )
    criterio = "Sí" if informe["criterio_cumplido"] else "No"
    return f"""# Nota técnica · Agentes aislados por entidad

Evidencia del punto de partida (TRL 3). Proyecto Nodo IA Caribe.

| Campo | Contenido |
| --- | --- |
| Fecha de la prueba | {informe["fecha"]} |
| Responsable | Anuar Harb |
| Enlace al video | `entregables/VIDEO-LABORATORIO.md` y capturas `.webm` en `resultados/demo5/historial/` |
| Enlace al repositorio o a los datos | {os.environ.get("NODO_REPO_URL", "Repositorio local · carpetas `demo5_agentes` y `resultados/demo5`")} |

## 1. Objetivo

Que la arquitectura de agentes aislados por entidad ya existe y está probada, en entorno simulado y con datos ficticios.

## 2. Montaje

| Componente | Detalle |
| --- | --- |
| Equipo | {texto_equipo(informe["equipo"])} |
| Modelos y versiones | No usa modelo de lenguaje. El prototipo es la mediación de archivos y el registro de auditoría en `demo5_agentes/nodo.py`. |
| Software | Python {informe["equipo"].get("python", "")}, pruebas `unittest` de la biblioteca estándar. |
| Conexión a internet durante la prueba | No. |

Dos entidades ficticias: `{ALCALDIA}` y `{GOBERNACION}`. Cada una tiene una caja de archivos. Toda lectura, escritura y listado pasa por el agente. Si la ruta resuelta sale de la caja, la operación se niega y se anota.

## 3. Procedimiento

1. Se crea un entorno nuevo con las dos cajas y archivos ficticios de un trámite y de unos cupos escolares.
2. Los dos agentes escriben, cada uno en su caja, una nota de trabajo.
3. El agente de la alcaldía intenta leer `{RUTA_SECRETO_GOBERNACION}`.
4. Se muestra el registro de auditoría y se verifica la cadena de hashes.
5. Se corren las 11 pruebas automatizadas, cada una en un directorio temporal propio.
6. Se guardan `resultados/demo5/pruebas.csv`, `informe.json` e `informe.html`.

## 4. Resultados

Criterio cumplido: {criterio}. Acceso cruzado bloqueado: {informe["bloqueo"]["bloqueado"]} ({informe["bloqueo"]["motivo"]}). Auditoría íntegra: {informe["auditoria_integra"]}. Pruebas: {informe["pruebas_pasadas"]} de {informe["pruebas_total"]}.

| Prueba | Resultado esperado | Resultado obtenido |
| --- | --- | --- |
{filas}

## 5. Limitaciones

La prueba demuestra el mecanismo en un solo computador y con datos ficticios. La mediación está en las herramientas del agente: quien ya controla el proceso de Python puede saltársela. No usa usuarios distintos del sistema operativo, ni red, ni entidades reales. No es el nodo del borde ni el enrutador soberano. Sirve como prueba de concepto de la arquitectura (TRL 3). El proyecto, en las fases siguientes, tiene que sostener el mismo aislamiento con entidades reales y con un registro que no dependa de un solo proceso.

## Guion del video

Se ven las dos cajas, el intento de lectura cruzada bloqueado, la tabla de auditoría y las 11 pruebas en pasado. Comando: `python -m demo5_agentes.en_vivo`.
"""


def main() -> int:
    equipo = describir_equipo()
    visible = corrida_visible(SALIDA / "entorno")
    filas = correr_pruebas()
    informe = guardar(filas, visible, equipo)
    print(f"Equipo: {texto_equipo(equipo)}")
    print(
        "Intento de lectura cruzada:",
        "BLOQUEADO" if informe["bloqueo"]["bloqueado"] else "NO BLOQUEADO",
        informe["bloqueo"]["motivo"],
    )
    print("Auditoría íntegra:" , "sí" if informe["auditoria_integra"] else "no")
    print()
    print(f"{'Prueba':<44} {'Obtenido'}")
    for fila in filas:
        print(f"{fila['prueba']:<44} {fila['obtenido']}")
    print()
    print(
        f"{informe['pruebas_pasadas']} de {informe['pruebas_total']} pasaron. "
        f"Criterio {'cumplido' if informe['criterio_cumplido'] else 'NO cumplido'}."
    )
    print(f"Informe: {SALIDA / 'informe.html'}")
    return 0 if informe["criterio_cumplido"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
