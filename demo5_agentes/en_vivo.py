"""Corrida de laboratorio del demo 5: dos agentes, bloqueo, auditoría y 11 pruebas."""

from __future__ import annotations

import csv
import json
import shutil
import unittest
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

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
        "responsable": "Anuar Harb",
        "datos": "ficticios",
        # El prototipo no abre ninguna conexión: solo lee y escribe archivos del equipo.
        "usa_red": False,
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
    # La nota y la página salen del mismo documento que el PDF (interfaz/notas.py).
    from interfaz.informe_export import html_imprimible
    from interfaz.notas import escribir_nota

    (SALIDA / "informe.html").write_text(html_imprimible(5, informe, autonomo=True), encoding="utf-8")
    escribir_nota(5, informe)
    return informe


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
