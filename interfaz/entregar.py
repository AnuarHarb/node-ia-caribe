"""Arma el paquete de entrega: las cinco notas técnicas en PDF, un ZIP con todas y el resumen.

Uso:  python -m interfaz.entregar

No mide nada. Lee el informe vigente de cada demo, regenera su nota (PDF y Markdown)
y revisa lo que pide la especificación: dos a tres páginas por nota, ZIP de 10 MB o
menos y enlace al video. Al final dice qué falta para poder entregar.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

from interfaz import enlaces
from interfaz.catalogo import DEMOS
from interfaz.documento import ETIQUETA_ESTADO, a_pdf, caracteres_sin_glifo, texto_plano
from interfaz.informe_export import PAGINAS_MAXIMAS, PAGINAS_MINIMAS, nombre_pdf
from interfaz.informes import cargar
from interfaz.notas import documento, escribir_nota

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "entregables" / "notas"
ZIP = RAIZ / "entregables" / "Nodo-IA-Caribe_Notas-tecnicas.zip"
RESUMEN = RAIZ / "entregables" / "RESUMEN-PARA-DOCUMENTO-TECNICO.md"
ZIP_MAXIMO_MB = 10
# El video del demo 4 es opcional según la especificación.
VIDEO_OPCIONAL = {4}


def revisar() -> dict:
    """Estado de cada nota frente a lo que pide la especificación. No escribe nada."""
    filas: list[dict] = []
    pendientes: list[str] = []
    for demo_id in sorted(DEMOS):
        doc = documento(demo_id, cargar(demo_id))
        datos, paginas = a_pdf(doc)
        estado = doc["estado"]["clase"]
        video = enlaces.video(demo_id)
        filas.append(
            {
                "demo": demo_id,
                "titulo": DEMOS[demo_id]["titulo"],
                "estado": estado,
                "etiqueta": ETIQUETA_ESTADO[estado],
                "resumen": texto_plano(doc["estado"]["texto"]),
                "pregunta": doc["pregunta"],
                "respuesta": texto_plano(doc["respuesta"]),
                "justifica": doc["justifica"],
                "paginas": paginas,
                "kb": round(len(datos) / 1024),
                "video": video,
                "video_opcional": demo_id in VIDEO_OPCIONAL,
                "archivo": str((SALIDA / nombre_pdf(demo_id)).relative_to(RAIZ)),
                "pdf": datos,
            }
        )
        if estado != "ok":
            pendientes.append(f"Demo {demo_id}: {ETIQUETA_ESTADO[estado].lower()}. {texto_plano(doc['estado']['texto'])}")
        if not PAGINAS_MINIMAS <= paginas <= PAGINAS_MAXIMAS:
            pendientes.append(
                f"Demo {demo_id}: la nota tiene {paginas} páginas; la especificación pide de "
                f"{PAGINAS_MINIMAS} a {PAGINAS_MAXIMAS}."
            )
        if not video and demo_id not in VIDEO_OPCIONAL:
            pendientes.append(
                f"Demo {demo_id}: falta el enlace al video (2 a 3 minutos, no listado) en entregables/enlaces.json."
            )
        raros = caracteres_sin_glifo(doc)
        if raros:
            pendientes.append(
                f"Demo {demo_id}: el PDF no puede dibujar estos caracteres: {' '.join(raros)}. Revisa las transcripciones."
            )
    return {"notas": filas, "pendientes": pendientes}


def tabla_viabilidad(notas: list[dict], respuesta: str = "Respuesta medida") -> list[str]:
    """Una fila por demo: la pregunta del proyecto, la respuesta de su nota y qué sostiene."""
    lineas = [
        f"| Demo | Pregunta | {respuesta} | Qué sostiene |",
        "| --- | --- | --- | --- |",
    ]
    for fila in notas:
        celdas = [f"{fila['demo']}. {fila['titulo']}", fila["pregunta"], fila["respuesta"], fila["justifica"]]
        lineas.append("| " + " | ".join(celda.replace("|", "\\|") for celda in celdas) + " |")
    return lineas


def resumen_markdown(revision: dict) -> str:
    """Texto corto por demo para pegar en el documento técnico (antecedentes y punto de partida del TRL)."""
    lineas = [
        "# Resultados de los demos para el documento técnico",
        "",
        "Texto para la sección de antecedentes y punto de partida del TRL. Lo genera "
        "`python -m interfaz.entregar` con las mismas cifras de las notas técnicas; no se edita a mano.",
        "",
        "## Viabilidad: qué pregunta responde cada demo",
        "",
        "Los demos sostienen el punto de partida en TRL 3: la idea funciona en laboratorio, se sabe dónde falla "
        "y cuánto falta. Cada respuesta es la misma que abre la nota técnica del demo.",
        "",
        *tabla_viabilidad(revision["notas"]),
        "",
    ]
    for fila in revision["notas"]:
        if fila["video"]:
            video = fila["video"]
        elif fila["video_opcional"]:
            video = "opcional en este demo; no se ha subido"
        else:
            video = "pendiente"
        lineas += [
            f"## Demo {fila['demo']}. {fila['titulo']}",
            "",
            f"**{fila['etiqueta']}.** {fila['resumen']}",
            "",
            f"- Nota técnica: `{Path(fila['archivo']).name}` ({fila['paginas']} páginas)",
            f"- Video: {video}",
            f"- Código y datos: {enlaces.repositorio()}",
            "",
        ]
    if revision["pendientes"]:
        lineas += ["## Falta antes de radicar", ""]
        lineas += [f"- {texto}" for texto in revision["pendientes"]]
        lineas.append("")
    return "\n".join(lineas)


def armar() -> dict:
    """Escribe los cinco PDF, las notas en Markdown, el resumen y el ZIP."""
    SALIDA.mkdir(parents=True, exist_ok=True)
    revision = revisar()
    for fila in revision["notas"]:
        demo_id = fila["demo"]
        (RAIZ / fila["archivo"]).write_bytes(fila["pdf"])
        carpeta = RAIZ / "resultados" / f"demo{demo_id}"
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / "informe.pdf").write_bytes(fila["pdf"])
        escribir_nota(demo_id, cargar(demo_id))
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as paquete:
        for fila in revision["notas"]:
            paquete.write(RAIZ / fila["archivo"], arcname=Path(fila["archivo"]).name)
    zip_mb = ZIP.stat().st_size / (1024 * 1024)
    if zip_mb > ZIP_MAXIMO_MB:
        revision["pendientes"].append(f"El ZIP pesa {zip_mb:.1f} MB; el máximo es {ZIP_MAXIMO_MB} MB.")
    RESUMEN.write_text(resumen_markdown(revision), encoding="utf-8")
    return {**revision, "zip": str(ZIP.relative_to(RAIZ)), "zip_mb": zip_mb}


def main() -> int:
    resultado = armar()
    print(f"{'Demo':<42} {'Estado':<22} {'Páginas':>7} {'KB':>5}  Video")
    for fila in resultado["notas"]:
        nombre = f"{fila['demo']}. {fila['titulo']}"
        print(
            f"{nombre:<42} {fila['etiqueta']:<22} {fila['paginas']:>7} {fila['kb']:>5}  "
            f"{'sí' if fila['video'] else 'opcional' if fila['video_opcional'] else 'FALTA'}"
        )
    print(f"\nNotas en PDF: {SALIDA.relative_to(RAIZ)}/")
    print(f"ZIP: {resultado['zip']} ({resultado['zip_mb'] * 1024:.0f} KB de {ZIP_MAXIMO_MB} MB permitidos)")
    print(f"Resumen para el documento técnico: {RESUMEN.relative_to(RAIZ)}")
    if resultado["pendientes"]:
        print("\nFalta antes de entregar:")
        for texto in resultado["pendientes"]:
            print(f"  - {texto}")
        return 1
    print("\nNada pendiente: las cinco notas cumplen el criterio y tienen su video.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
