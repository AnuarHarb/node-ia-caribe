"""Arma la página para ver los resultados ya medidos."""

from __future__ import annotations

import html
import json
from pathlib import Path

from demo3_comparacion.tareas import TAREAS

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "resultados" / "ver.html"


def e(valor: object) -> str:
    return html.escape(str(valor))


def main() -> None:
    informe = json.loads((RAIZ / "resultados" / "demo5" / "informe.json").read_text(encoding="utf-8"))
    generaciones = json.loads((RAIZ / "resultados" / "demo3" / "generaciones.json").read_text(encoding="utf-8"))
    pruebas = "\n".join(
        f"<tr><td><code>{e(fila['prueba'])}</code></td><td>{e(fila['esperado'])}</td><td>{e(fila['obtenido'])}</td></tr>"
        for fila in informe["filas"]
    )
    tareas = []
    for tarea in TAREAS:
        local = generaciones.get(tarea["id"], {}).get("local", {})
        tareas.append(
            f"""<article id="{e(tarea['id'])}">
          <h3>{e(tarea['id'])} · {e(tarea['tipo'].replace('_', ' '))}</h3>
          <p>{e(tarea['entidad'])} · {e(local.get('segundos', '—'))} s</p>
          <h4>Entrada</h4>
          <p>{e(tarea['entrada'])}</p>
          <h4>Respuesta local</h4>
          <p class="respuesta">{e(local.get('texto') or 'Sin respuesta')}</p>
        </article>"""
        )
    def si_no(valor: bool) -> str:
        return "sí" if valor else "no"

    estado = "cumplido" if informe["criterio_cumplido"] else "pendiente"
    pagina = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Resultados · Nodo IA Caribe</title>
  <style>
    :root {{ color-scheme: light; }}
    body {{ font-family: Palatino, "Iowan Old Style", Georgia, serif; margin: 0 auto; max-width: 52rem; padding: 1.5rem 1rem 4rem; line-height: 1.45; color: #1c1c1c; }}
    nav a {{ margin-right: 1rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #ccc; text-align: left; vertical-align: top; padding: 0.4rem; }}
    article {{ border-top: 1px solid #ddd; padding: 1rem 0; }}
    .respuesta {{ white-space: pre-wrap; background: #f6f4ef; padding: 0.8rem 1rem; }}
    code {{ font-family: ui-monospace, monospace; font-size: 0.85em; }}
  </style>
</head>
<body>
  <header>
    <p>Nodo IA Caribe · laboratorio</p>
    <h1>Resultados medidos</h1>
    <p>Apple M2 Pro, 16 GB. Modelo local qwen2.5:3b. La referencia comercial y las dos calificaciones humanas siguen pendientes.</p>
  </header>
  <nav aria-label="Secciones">
    <a href="#demo5">Demo 5</a>
    <a href="#demo3">Demo 3</a>
    <a href="demo5/informe.html">Informe completo del demo 5</a>
  </nav>
  <main>
    <section id="demo5">
      <h2>Demo 5 · Agentes aislados</h2>
      <p>Criterio {e(estado)}. Pruebas {e(informe['pruebas_pasadas'])} de {e(informe['pruebas_total'])}. Acceso cruzado bloqueado: {e(si_no(informe['bloqueo']['bloqueado']))}. Auditoría íntegra: {e(si_no(informe['auditoria_integra']))}.</p>
      <table>
        <caption>Las 11 pruebas</caption>
        <thead><tr><th>Prueba</th><th>Esperado</th><th>Obtenido</th></tr></thead>
        <tbody>
          {pruebas}
        </tbody>
      </table>
    </section>
    <section id="demo3">
      <h2>Demo 3 · Respuestas del modelo local</h2>
      <p>Cuarenta tareas. La primera tardó 56,05 s con el modelo en frío. Las otras 39 promediaron 0,98 s. Aquí solo está el camino local.</p>
      {''.join(tareas)}
    </section>
  </main>
</body>
</html>
"""
    SALIDA.write_text(pagina, encoding="utf-8")
    print(SALIDA)


if __name__ == "__main__":
    main()
