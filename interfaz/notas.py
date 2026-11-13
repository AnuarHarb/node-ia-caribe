"""Contenido de la nota técnica de cada demo, con la plantilla de la especificación.

Cada nota sigue las seis secciones que pide la Convocatoria 54: objetivo, montaje,
procedimiento, resultados, limitaciones y enlaces. Las cifras salen del informe medido
(`resultados/demoN/informe.json`); aquí no se calcula ni se estima nada nuevo.

`documento()` devuelve el modelo que pintan `interfaz/documento.py` (PDF, HTML y
Markdown), así las tres salidas dicen lo mismo.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from equipo import texto_equipo
from interfaz import enlaces
from interfaz.catalogo import DEMOS
from interfaz.documento import a_markdown, aviso, b, cod, h3, lista, p, pasos, seccion, tabla, url

RAIZ = Path(__file__).resolve().parents[1]
NOTAS = RAIZ / "notas"
ARCHIVO_NOTA = {
    1: "Demo-1_Voz-en-espanol-costeno",
    2: "Demo-2_IA-completa-sin-internet",
    3: "Demo-3_IA-local-frente-a-referencia-externa",
    4: "Demo-4_Linea-base-del-error-WER",
    5: "Demo-5_Agentes-aislados-por-entidad",
}
ANTETITULO = "Nodo IA Caribe · Convocatoria 54 · Evidencia del punto de partida (TRL 3)"
COLOMBIA = timezone(timedelta(hours=-5))
MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)  # fmt: skip
# Las tablas largas se recortan para que la nota quepa en dos o tres páginas.
MAXIMO_FILAS = 12


# --- Formato -----------------------------------------------------------------------


def _momento(texto: object) -> datetime | None:
    if not texto:
        return None
    try:
        momento = datetime.fromisoformat(str(texto).replace("Z", "+00:00"))
    except ValueError:
        return None
    # Una fecha sin zona la escribió este mismo equipo, en hora de Colombia.
    return momento.astimezone(COLOMBIA) if momento.tzinfo else momento


def fecha_larga(texto: object, con_hora: bool = True) -> str:
    momento = _momento(texto)
    if not momento:
        return "Sin fecha registrada"
    dia = f"{momento.day} de {MESES[momento.month - 1]} de {momento.year}"
    return f"{dia}, {momento:%H:%M}" if con_hora else dia


def _rango_fechas(inicio: object, fin: object) -> str:
    uno, dos = _momento(inicio), _momento(fin)
    if not uno or not dos:
        return fecha_larga(inicio or fin)
    if uno.date() == dos.date():
        return f"{fecha_larga(inicio, False)}, de {uno:%H:%M} a {dos:%H:%M}"
    return f"del {fecha_larga(inicio)} al {fecha_larga(fin)}"


def _n(valor: object, decimales: int = 2) -> str:
    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        return "—"
    return f"{valor:.{decimales}f}"


def _pct(valor: object, decimales: int = 2) -> str:
    return "—" if _n(valor, decimales) == "—" else f"{_n(valor, decimales)} %"


def _si_no(valor: object) -> str:
    if valor is True:
        return "Sí"
    if valor is False:
        return "No"
    return "Sin medir"


def _plural(cantidad: int, uno: str, varios: str) -> str:
    return f"{cantidad} {uno if cantidad == 1 else varios}"


def _recortar(filas: list, maximo: int = MAXIMO_FILAS) -> tuple[list, int]:
    return (filas, 0) if len(filas) <= maximo else (filas[:maximo], len(filas) - maximo)


# --- Partes comunes ----------------------------------------------------------------


def _ficha(demo_id: int, informe: dict, fecha: str, etiqueta_fecha: str = "Fecha de la prueba") -> list:
    video = enlaces.video(demo_id)
    if video:
        celda_video: object = url(video)
    elif demo_id == 4:
        celda_video = "Opcional en este demo. Sin enlace todavía."
    else:
        celda_video = "Pendiente: falta subir el video (no listado) y pegar el enlace."
    return [
        (etiqueta_fecha, fecha),
        ("Responsable", informe.get("responsable") or DEMOS[demo_id].get("responsable") or "Anuar Harb"),
        ("Equipo", texto_equipo(informe["equipo"]) if informe.get("equipo") else "Sin registrar"),
        ("Video", celda_video),
        ("Código y datos", url(enlaces.repositorio())),
    ]


def _seccion_enlaces(demo_id: int, codigo: list[str], datos: list[str], extra: list | None = None) -> dict:
    video = enlaces.video(demo_id)
    if video:
        linea_video: list = [b("Video: "), url(video)]
    elif demo_id == 4:
        linea_video = [b("Video: "), "opcional en este demo; no se ha subido."]
    else:
        linea_video = [
            b("Video: "),
            "pendiente. Cuando esté subido como no listado, el enlace se pega en ",
            cod("entregables/enlaces.json"),
            " y esta nota lo toma de ahí.",
        ]
    items: list = [
        linea_video,
        [b("Repositorio: "), url(enlaces.repositorio())],
        [b("Código: "), *_rutas(codigo)],
    ]
    # Solo se citan los archivos de datos que ya existen: la nota no promete lo que no hay.
    existentes = [ruta for ruta in datos if (RAIZ / ruta).exists()]
    if existentes:
        items.append([b("Datos medidos: "), *_rutas(existentes)])
    else:
        items.append([b("Datos medidos: "), "todavía no hay; se guardan al hacer la medición."])
    return seccion("6. Enlaces", lista(items + (extra or [])))


def _rutas(rutas: list[str]) -> list:
    partes: list = []
    for indice, ruta in enumerate(rutas):
        if indice:
            partes.append(", ")
        partes.append(cod(ruta))
    partes.append(".")
    return partes


def _documento(demo_id: int, estado: dict, ficha: list, secciones: list[dict], informe: dict | None) -> dict:
    meta = DEMOS[demo_id]
    origen = f"resultados/demo{demo_id}/informe.json"
    if demo_id == 2:
        # El informe del demo 2 se recalcula siempre desde los turnos guardados.
        origen = "resultados/demo2/turnos.jsonl"
    respuesta = estado.get("respuesta") or "Sin medir todavía."
    return {
        "titulo": f"Nota técnica · Demo {demo_id}. {meta['titulo']}",
        "antetitulo": ANTETITULO,
        "pie_pagina": f"Nodo IA Caribe · Demo {demo_id} · {meta['titulo']}",
        "estado": estado,
        "pregunta": meta["pregunta"],
        "respuesta": respuesta,
        "justifica": meta["justifica"],
        "ficha": [
            ("Pregunta que responde", b(meta["pregunta"])),
            ("Respuesta medida", respuesta),
            ("Qué sostiene en el proyecto", meta["justifica"]),
            *ficha,
        ],
        "secciones": secciones,
        "pie": (
            f"Nota generada el {fecha_larga(datetime.now().astimezone().isoformat())} (hora de Colombia) "
            f"a partir de {origen}. Todas las cifras son medidas; ninguna se estima ni se completa a mano."
        ),
    }


# --- Demo 1 ------------------------------------------------------------------------


def _demo1(informe: dict) -> dict:
    tabla_filas = informe.get("tabla") or []
    modelos = informe.get("modelos") or {}
    cobertura = informe.get("cobertura") or {}
    wer = informe.get("wer_corpus") or {}
    tiempos = informe.get("tiempos_promedio") or {}
    frases = int(informe.get("filas") or len(tabla_filas))
    errores = int(informe.get("errores_marcados") or 0)
    aciertos = int(informe.get("aciertos_marcados") or 0)
    hablantes = int(cobertura.get("hablantes") or len({f.get("persona") for f in tabla_filas}) or 0)
    meta_hablantes = int(cobertura.get("hablantes_protocolo") or 3)
    meta_frases = int(cobertura.get("frases_por_hablante_protocolo") or 10)
    completa = bool(cobertura.get("completa"))
    con_flujo = sum(1 for f in tabla_filas if f.get("flujo_completo"))

    muestra = (
        f"{_plural(frases, 'frase', 'frases')} de {_plural(hablantes, 'hablante', 'hablantes')}"
        if hablantes
        else _plural(frases, "frase", "frases")
    )
    if informe.get("criterio_cumplido"):
        texto = (
            f"El flujo completo (escuchar, responder y hablar) funcionó en {con_flujo} de {frases} frases "
            f"y en {errores} de ellas quedó registrado un error real de reconocimiento."
        )
        if not completa:
            texto += (
                f" La muestra es menor que la del protocolo: {muestra}, frente a {meta_hablantes} o 4 "
                f"hablantes con {meta_frases} frases cada uno."
            )
        estado = {"clase": "ok", "texto": texto}
    else:
        faltas = []
        if not informe.get("criterio_flujo"):
            faltas.append("el flujo no se completó en todas las frases")
        if not informe.get("criterio_video_error_real"):
            faltas.append("todavía no hay un error real de reconocimiento registrado")
        estado = {
            "clase": "parcial",
            "texto": f"Se midieron {muestra}, pero " + " y ".join(faltas or ["falta completar la medición"]) + ".",
        }

    if frases:
        inventos = sum(1 for o in informe.get("observaciones_llm") or [] if o.get("tipo") == "alucinacion")
        estado["respuesta"] = (
            f"{'Sí, con fallas' if con_flujo == frases else 'Solo en parte'}: el flujo se completó en {con_flujo} de "
            f"{frases} frases, en {_n(tiempos.get('total_promedio_s'))} s en promedio. {errores} de {frases} quedaron "
            f"con error de transcripción (WER {_pct(wer.get('wer_porcentaje'))})"
            + (f" y el modelo inventó datos en {_plural(inventos, 'respuesta', 'respuestas')}." if inventos else ".")
        )

    marcas = [f.get("ts") for f in tabla_filas if f.get("ts")]
    fecha = _rango_fechas(min(marcas), max(marcas)) if marcas else fecha_larga(informe.get("fecha"))

    personas = sorted({str(f.get("persona") or "Sin nombre") for f in tabla_filas})
    montaje = tabla(
        ["Componente", "Detalle"],
        [
            ["Equipo", texto_equipo(informe["equipo"]) if informe.get("equipo") else "Sin registrar"],
            [
                "Reconocimiento de voz",
                f"{modelos.get('whisper', 'Whisper')}, sin ajustar, con el idioma fijado en español.",
            ],
            [
                "Modelo de lenguaje",
                f"{modelos.get('ollama', 'modelo local')} servido con Ollama en el mismo equipo. "
                "Temperatura 0.2 y respuestas de hasta 120 tokens.",
            ],
            ["Síntesis de voz", f"{modelos.get('piper_asistente', 'Piper')}."],
            ["Interfaz", "Página web local (python -m interfaz); el audio entra por el micrófono del navegador."],
            ["Hablantes", f"{_plural(len(personas), 'persona', 'personas')} del equipo: {', '.join(personas)}."],
            [
                "Consentimiento",
                "El protocolo exige consentimiento escrito de cada hablante. La Fundación lo conserva y no se publica.",
            ],
            [
                "Internet",
                "Los tres modelos corren en el equipo y ninguno llama a un servicio externo. "
                "La prueba con la red cortada y medida es el demo 2.",
            ],
        ],
        anchos=[1, 3.4],
    )

    filas_medicion = []
    for numero, fila in enumerate(tabla_filas, 1):
        # La frase del guion no se repite aquí: casi siempre es igual a la transcripción correcta
        # y queda en los datos. Así la nota cabe en tres páginas.
        filas_medicion.append(
            [
                str(numero),
                (fila.get("transcripcion_correcta") or "").strip(),
                (fila.get("transcripcion_sistema") or "").strip(),
                "Sí" if fila.get("correcta") == "si" else "No",
                _pct(fila.get("wer_porcentaje"), 1),
            ]
        )
    filas_medicion, sobran = _recortar(filas_medicion)
    tabla_medicion = tabla(
        ["#", "Transcripción correcta (lo que se dijo)", "Transcripción del sistema", "¿Correcta?", "WER"],
        filas_medicion,
        anchos=[0.35, 4.1, 4.1, 1.25, 0.85],
        titulo="Tabla 1. Lo que se dijo y lo que escribió el sistema",
        alinear=["L", "L", "L", "L", "R"],
    )

    filas_errores = []
    nombre_tipo = {"sustitucion": "Cambió", "omision": "Omitió", "insercion": "Agregó"}
    for numero, fila in enumerate(tabla_filas, 1):
        for error in fila.get("errores_palabras") or []:
            filas_errores.append(
                [
                    str(numero),
                    nombre_tipo.get(error.get("tipo"), str(error.get("tipo"))),
                    error.get("referencia") or "(nada)",
                    error.get("sistema") or "(nada)",
                ]
            )
    filas_errores, sobran_errores = _recortar(filas_errores, 14)

    medidas = [fila for fila in tabla_filas if fila.get("asr_s") is not None]
    filas_flujo = []
    for etiqueta, campo in (
        ("Escuchar y transcribir (Whisper)", "asr_s"),
        ("Responder (modelo local)", "llm_s"),
        ("Hablar (Piper)", "tts_s"),
        ("Total de la frase", "segundos_total"),
    ):
        valores = [float(fila[campo]) for fila in medidas if fila.get(campo) is not None]
        if not valores:
            continue
        celdas = [_n(sum(valores) / len(valores)), _n(min(valores)), _n(max(valores))]
        if campo == "segundos_total":
            filas_flujo.append([b(etiqueta), *[b(c) for c in celdas]])
        else:
            filas_flujo.append([etiqueta, *celdas])

    resultados: list = [
        p(
            f"Se midieron {muestra}. El flujo de punta a punta se completó en {con_flujo} de {frases}: "
            "el sistema escuchó, respondió y habló. ",
            b(
                f"Transcribió sin error {aciertos} y se equivocó en {errores}."
                if frases
                else "Sin frases medidas."
            ),
        ),
        tabla_medicion,
    ]
    if sobran:
        resultados.append(p(f"La tabla muestra las primeras {MAXIMO_FILAS} frases; hay {sobran} más en los datos."))
    if wer:
        ediciones = int(wer.get("sustituciones", 0)) + int(wer.get("eliminaciones", 0)) + int(wer.get("inserciones", 0))
        resultados.append(
            p(
                b(f"Error de palabras (WER) del conjunto: {_pct(wer.get('wer_porcentaje'))}. "),
                f"Son {ediciones} palabras con error sobre {wer.get('palabras_referencia')} dichas: "
                f"{wer.get('sustituciones')} cambiadas, {wer.get('eliminaciones')} omitidas y "
                f"{wer.get('inserciones')} agregadas. Una frase cuenta como correcta solo si coincide entera "
                "con la transcripción correcta, después de pasar todo a minúsculas y quitar la puntuación.",
            )
        )
    if filas_errores:
        resultados.append(
            tabla(
                ["#", "Qué hizo", "Lo que se dijo", "Lo que escribió el sistema"],
                filas_errores,
                anchos=[0.35, 0.9, 3, 3],
                titulo="Tabla 2. Dónde falla el reconocimiento, palabra por palabra",
            )
        )
        if sobran_errores:
            resultados.append(p(f"Hay {sobran_errores} errores más en los datos."))
    if len(informe.get("wer_por_persona") or []) > 1:
        resultados.append(
            tabla(
                ["Hablante", "Frases", "WER"],
                [[w.get("persona"), str(w.get("frases")), _pct(w.get("wer_porcentaje"))] for w in informe["wer_por_persona"]],
                anchos=[3, 1, 1],
                titulo="WER por hablante",
                alinear=["L", "R", "R"],
            )
        )
    if filas_flujo:
        resultados.append(
            tabla(
                ["Etapa", "Promedio (s)", "Mínimo (s)", "Máximo (s)"],
                filas_flujo,
                anchos=[3.4, 1, 1, 1],
                titulo=f"Tabla 3. Cuánto tarda cada etapa del flujo ({_plural(len(medidas), 'frase', 'frases')})",
                alinear=["L", "R", "R", "R"],
            )
        )
        if tiempos.get("resto_promedio_s") is not None:
            resultados.append(
                p(
                    f"La primera frase tardó {_n(tiempos.get('primera_total_s'))} s porque los modelos se cargan "
                    f"en memoria en la primera consulta. Sin ella, el promedio es de {_n(tiempos.get('resto_promedio_s'))} s "
                    f"y el máximo registrado fue de {_n(tiempos.get('total_maximo_s'))} s. El total es algo mayor "
                    "que la suma de las tres etapas porque incluye guardar el audio y convertirlo al formato que "
                    "lee Whisper."
                )
            )
    observaciones = informe.get("observaciones_llm") or []
    if observaciones:
        resultados.append(h3("Lo que respondió el asistente"))
        resultados.append(
            p(
                f"En {_plural(len(observaciones), 'respuesta', 'respuestas')} el modelo local dio un dato que nadie "
                "le había dado. Se anota porque es un fallo real del sistema, distinto del error de reconocimiento:"
            )
        )
        veces: dict[str, int] = {}
        for o in observaciones:
            texto = o.get("observacion", "")
            veces[texto] = veces.get(texto, 0) + 1
        resultados.append(
            lista([texto if n == 1 else f"{texto} ({n} veces)" for texto, n in veces.items()])
        )

    limitaciones: list = []
    if not completa:
        limitaciones.append(
            [
                b("Muestra pequeña. "),
                f"Hay {muestra}; el protocolo pide {meta_hablantes} o 4 hablantes con {meta_frases} frases cada uno. "
                "El porcentaje de error es indicativo y puede cambiar con más voces.",
            ]
        )
    limitaciones += [
        [
            b("Habla leída. "),
            "Son frases de un guion dichas frente al computador, no conversación espontánea ni ruido de una "
            "oficina. En esas condiciones el error puede ser mayor.",
        ],
        [
            b("Una sola persona fijó la transcripción correcta. "),
            "El WER depende de esa referencia; no hubo segunda revisión.",
        ],
    ]
    if "es_MX" in str(modelos.get("piper_archivo", "")):
        limitaciones.append(
            [
                b("La voz que responde no es costeña. "),
                "Piper no tiene una voz del Caribe colombiano; se usó una voz de español de México. "
                "La síntesis funciona, pero no suena local.",
            ]
        )
    if observaciones:
        limitaciones.append(
            [
                b("El asistente no consulta fuentes oficiales. "),
                "Por eso inventó requisitos y ubicaciones. Para atender trámites reales tiene que conectarse a la "
                "información oficial de cada entidad.",
            ]
        )
    limitaciones.append(
        [
            b("Un solo equipo y un solo modelo. "),
            "Los tiempos son de este portátil y de Whisper small; con otro equipo u otro tamaño de modelo cambian.",
        ]
    )
    if informe.get("filas_palenquero"):
        limitaciones.append(
            f"Las {informe['filas_palenquero']} frases en palenquero grabadas en esta misma pantalla no entran "
            "en estas cifras; se miden en el demo 4."
        )

    secciones = [
        seccion(
            "1. Objetivo",
            p(
                "Mostrar que el reconocimiento y la síntesis de voz ya funcionan con habla costeña, y dónde fallan "
                "hoy. Justifica el objetivo específico 4 del proyecto."
            ),
            p(b("Criterio de éxito: "), "flujo de punta a punta y al menos un error real de reconocimiento registrado."),
        ),
        seccion("2. Montaje", montaje),
        seccion(
            "3. Procedimiento",
            pasos(
                [
                    f"Cada hablante dice, con su habla natural, frases cotidianas de trámite tomadas de un guion de {meta_frases}.",
                    "Whisper transcribe el audio, el modelo local redacta una respuesta corta y Piper la dice en voz alta. "
                    "El servidor cronometra cada etapa.",
                    "Una persona escucha la grabación y escribe la transcripción correcta: lo que de verdad se dijo, "
                    "que puede no ser igual al guion.",
                    "La transcripción del sistema se compara con la correcta después de pasar las dos a minúsculas y "
                    "quitar la puntuación. Si son iguales, la frase es correcta.",
                    "Con la misma normalización se calcula el WER con la biblioteca jiwer: palabras cambiadas, omitidas "
                    "o agregadas, divididas por las palabras dichas.",
                    "Cada turno queda guardado con su audio, sus tiempos y las dos transcripciones.",
                ]
            ),
        ),
        seccion("4. Resultados", *resultados),
        seccion("5. Limitaciones", lista(limitaciones)),
        _seccion_enlaces(
            1,
            ["voz/", "interfaz/demo1_informe.py"],
            ["resultados/demo1/filas.json", "resultados/demo1/turnos.jsonl", "resultados/demo1/informe.json"],
            [
                [
                    b("Audios: "),
                    "las grabaciones no se publican porque la voz identifica a la persona. "
                    "Quedan en el equipo, junto con los consentimientos.",
                ]
            ],
        ),
    ]
    return _documento(1, estado, _ficha(1, informe, fecha), secciones, informe)


# --- Demo 2 ------------------------------------------------------------------------


def _demo2(informe: dict | None) -> dict:
    informe = informe or {}
    modelos = informe.get("modelos") or {}
    criterios = informe.get("criterios") or {}
    minimo = int(informe.get("usuarios_minimos") or 3)
    tope = float(informe.get("segundos_maximos") or 10)
    por_protocolo = int(informe.get("consultas_por_usuario_protocolo") or 10)
    voz = int(informe.get("consultas_voz") or 0)
    consumo = informe.get("consumo") or {}
    hay_voz = voz > 0 and informe.get("entrada") == "voz"

    if informe.get("criterio_cumplido") is True:
        estado = {
            "clase": "ok",
            "texto": (
                f"{informe.get('usuarios_simultaneos')} usuarios a la vez, respuesta de voz en "
                f"{_n(informe.get('tiempo_promedio_s'))} s en promedio y sin salida a internet durante toda la sesión."
            ),
        }
    elif hay_voz:
        faltantes = " ".join(informe.get("faltantes") or [])
        clase = "falla" if criterios.get("tiempo") is False else "parcial"
        estado = {"clase": clase, "texto": f"Hay medición por voz, pero no cumple todo el criterio. {faltantes}"}
    else:
        estado = {
            "clase": "pendiente",
            "texto": (
                "Todavía no se ha hecho la medición por voz con los teléfonos y el router sin internet. "
                "Esta nota describe el montaje y el procedimiento; la tabla de resultados se llena sola al medir."
            ),
        }

    if hay_voz:
        estado["respuesta"] = (
            f"{'Sí' if informe.get('criterio_cumplido') is True else 'Todavía no'}: "
            f"{informe.get('usuarios_simultaneos', '—')} usuarios a la vez y respuesta de voz en "
            f"{_n(informe.get('tiempo_promedio_s'))} s en promedio."
        )
        fecha = _rango_fechas(informe.get("sesion_inicio"), informe.get("sesion_fin"))
    else:
        fecha = "Pendiente"

    montaje = tabla(
        ["Componente", "Detalle"],
        [
            ["Equipo", texto_equipo(informe["equipo"]) if informe.get("equipo") else "El mismo computador de los demás demos."],
            ["Modelo de lenguaje", f"{modelos.get('ollama', 'qwen2.5:3b')}, modelo abierto servido en el equipo con Ollama."],
            ["Reconocimiento de voz", f"{modelos.get('whisper', 'Whisper small')}, en el mismo equipo."],
            ["Síntesis de voz", f"{modelos.get('piper_asistente', 'Piper')}."],
            [
                "Red",
                "Un router wifi sin cable de internet. Los teléfonos y el computador quedan en la misma red local.",
            ],
            [
                "Usuarios",
                f"{minimo} o 4 teléfonos. Cada uno abre la página de consulta con un código QR y habla por su micrófono.",
            ],
            [
                "Comprobación de la red",
                "En cada consulta el servidor intenta abrir una conexión hacia internet (1.1.1.1, puerto 443) "
                "y guarda si lo logró. No depende de lo que diga quien opera.",
            ],
            [
                "Consumo eléctrico",
                f"Medidor de enchufe{': ' + consumo['instrumento'] if consumo.get('instrumento') else ''}. "
                "La lectura la hace una persona, en reposo y durante la carga.",
            ],
        ],
        anchos=[1, 3.4],
    )

    if hay_voz:
        filas_criterio = [
            [
                "Usuarios a la vez",
                f"{minimo} o más",
                str(informe.get("usuarios_simultaneos")),
                _si_no(criterios.get("usuarios")),
            ],
            [
                "Tiempo promedio de respuesta de voz",
                f"menos de {tope:.0f} s",
                f"{_n(informe.get('tiempo_promedio_s'))} s",
                _si_no(criterios.get("tiempo")),
            ],
            [
                "Sin internet",
                "sin salida en toda la sesión",
                {True: "sin salida", False: "hubo salida", None: "no quedó registrado"}[criterios.get("sin_internet")],
                _si_no(criterios.get("sin_internet")),
            ],
        ]
        etapas = informe.get("etapas_promedio") or {}
        resultados: list = [
            p(informe.get("resumen_ejecutivo", "")),
            tabla(
                ["Usuarios simultáneos", "Tiempo promedio (s)", "Tiempo máximo (s)", "Consumo en reposo (W)", "Consumo en carga (W)"],
                [
                    [
                        str(informe.get("usuarios_simultaneos")),
                        _n(informe.get("tiempo_promedio_s")),
                        _n(informe.get("tiempo_maximo_s")),
                        _n(consumo.get("reposo_w"), 1) if consumo else "Sin medir",
                        _n(consumo.get("carga_w"), 1) if consumo else "Sin medir",
                    ]
                ],
                titulo="Tabla 1. Lo que pide medir la especificación",
                alinear=["R", "R", "R", "R", "R"],
            ),
            tabla(
                ["Parte del criterio", "Meta", "Medido", "¿Cumple?"],
                filas_criterio,
                anchos=[2.4, 1.8, 1.6, 0.9],
                titulo="Tabla 2. El criterio, parte por parte",
            ),
            p(
                "«Usuarios a la vez» es el máximo de personas distintas que tenían una consulta en curso en el mismo "
                "instante, según la hora de inicio y de fin de cada consulta. El tiempo va desde que el servidor recibe "
                "el audio hasta que tiene lista la respuesta hablada. En promedio: "
                f"escuchar {_n(etapas.get('asr_s'))} s, responder {_n(etapas.get('llm_s'))} s y hablar {_n(etapas.get('tts_s'))} s."
            ),
        ]
        por_usuario = informe.get("por_usuario") or []
        if por_usuario:
            filas_usuario, sobran = _recortar(
                [[u.get("usuario"), str(u.get("consultas")), _n(u.get("promedio_s")), _n(u.get("maximo_s"))] for u in por_usuario]
            )
            resultados.append(
                tabla(
                    ["Usuario", "Consultas", "Promedio (s)", "Máximo (s)"],
                    filas_usuario,
                    anchos=[3, 1, 1, 1],
                    titulo="Tabla 3. Por usuario",
                    alinear=["L", "R", "R", "R"],
                )
            )
            if sobran:
                resultados.append(p(f"Hay {sobran} usuarios más en los datos."))
        if informe.get("faltantes"):
            resultados.append(aviso(b("Lo que falta. "), " ".join(informe["faltantes"]), clase="parcial"))
        if not consumo:
            resultados.append(
                p("El consumo eléctrico no se midió. La especificación lo pide «si es posible»; no se estima.")
            )
    else:
        resultados = [
            aviso(
                b("Sin resultados todavía. "),
                "No hay consultas por voz registradas. "
                + (
                    f"Lo único guardado es {_plural(int(informe.get('consultas_texto') or 0), 'consulta de verificación', 'consultas de verificación')} "
                    "por texto, que sirve para probar que el servidor responde y no cuenta para el criterio."
                    if informe.get("consultas_texto")
                    else ""
                ),
                clase="pendiente",
            ),
            tabla(
                ["Usuarios simultáneos", "Tiempo promedio (s)", "Tiempo máximo (s)", "Consumo en reposo (W)", "Consumo en carga (W)"],
                [["Sin medir", "Sin medir", "Sin medir", "Sin medir", "Sin medir"]],
                titulo="Tabla 1. Lo que pide medir la especificación",
            ),
            p(
                "Al hacer la sesión con los teléfonos, cada columna se calcula sola con los turnos guardados."
            ),
        ]

    limitaciones: list = [
        [
            b("Programas distintos a los que nombra la especificación. "),
            "La especificación nombra llama.cpp o vLLM y whisper.cpp; aquí el modelo de lenguaje se sirve con Ollama "
            "y Whisper corre con MLX, la versión para procesadores de Apple. Los modelos son abiertos y corren "
            "igual en el equipo; cambia el programa que los ejecuta.",
        ],
        [
            b("Un computador portátil, no el equipo final del nodo. "),
            "Los tiempos y el consumo son de este equipo.",
        ],
        [
            b("El reconocimiento y la síntesis atienden una consulta a la vez. "),
            "Cuando llegan varias juntas, esperan turno; por eso el tiempo sube con cada usuario adicional.",
        ],
        [
            b("Pocas personas y poco tiempo. "),
            f"El protocolo es de {minimo} o 4 teléfonos con {por_protocolo} consultas cada uno; no es una prueba de carga sostenida.",
        ],
        [
            b("La comprobación de internet es una sola señal. "),
            "Que no haya salida hacia 1.1.1.1 indica que el equipo está aislado, y se complementa con el video, "
            "donde se ve la desconexión del router.",
        ],
    ]
    if hay_voz and not informe.get("cobertura_completa"):
        limitaciones.insert(
            0,
            [
                b("Sesión más corta que el protocolo. "),
                f"Hubo {_plural(int(informe.get('usuarios') or 0), 'usuario', 'usuarios')} y {voz} consultas; "
                f"el protocolo pide {por_protocolo} por usuario.",
            ],
        )

    secciones = [
        seccion(
            "1. Objetivo",
            p(
                "Mostrar que un modelo abierto, el reconocimiento de voz y la síntesis de voz corren juntos en un "
                "solo equipo, sin internet y con varios usuarios al mismo tiempo."
            ),
            p(
                b("Criterio de éxito: "),
                f"{minimo} o más usuarios a la vez, respuesta de voz en menos de {tope:.0f} segundos en promedio y "
                "sin conexión a internet.",
            ),
        ),
        seccion("2. Montaje", montaje),
        seccion(
            "3. Procedimiento",
            pasos(
                [
                    "Se desconecta el router de internet frente a la cámara. La pantalla del demo muestra el estado de la red.",
                    "Cada teléfono abre la página de consulta con el código QR y escribe el nombre de quien pregunta.",
                    f"Desde cada teléfono se hacen {por_protocolo} consultas por voz, todos al mismo tiempo.",
                    "El servidor guarda de cada consulta: quién la hizo, la hora de inicio y de fin, el tiempo de cada "
                    "etapa y si el equipo tenía salida a internet.",
                    "Se lee el medidor de consumo con el equipo en reposo y durante la carga, y se anota en la pantalla del demo.",
                    "El informe calcula los usuarios a la vez, el tiempo promedio y el máximo, y dice qué parte del criterio se cumple.",
                ]
            ),
        ),
        seccion("4. Resultados", *resultados),
        seccion("5. Limitaciones", lista(limitaciones)),
        _seccion_enlaces(
            2,
            ["interfaz/demo2_informe.py", "interfaz/servidor.py", "voz/"],
            ["resultados/demo2/turnos.jsonl", "resultados/demo2/consumo.json", "resultados/demo2/informe.json"],
        ),
    ]
    ficha = _ficha(2, informe, fecha)
    return _documento(2, estado, ficha, secciones, informe)


# --- Demo 3 ------------------------------------------------------------------------


NOMBRE_DIMENSION = {
    "exactitud": "Exactitud",
    "completitud": "Completitud",
    "tono": "Tono",
    "utilidad": "Utilidad",
}


def _demo3(informe: dict) -> dict:
    comparacion = informe.get("comparacion") or {}
    paquete = informe.get("paquete_ciego") or {}
    calificacion = paquete.get("calificacion") or {}
    analisis = calificacion.get("analisis") or {}
    rendimiento = informe.get("rendimiento") or {}
    local, referencia = rendimiento.get("local") or {}, rendimiento.get("referencia") or {}
    costo = informe.get("costo") or {}
    costo_ref = costo.get("referencia") or {}
    total = int(comparacion.get("tareas_total") or 40)
    modelo_local = comparacion.get("modelo_local") or informe.get("modelo_local") or "modelo local"
    modelo_ref = comparacion.get("modelo_referencia") or informe.get("modelo_referencia") or "referencia"
    proveedor = comparacion.get("proveedor_referencia") or informe.get("proveedor_referencia") or ""
    calculado = calificacion.get("estado") == "calculado"
    calidad = calificacion.get("calidad_promedio") or {}
    calificadores = calificacion.get("calificadores") or []
    gana = analisis.get("gana") or {}

    # Qué parte de la calidad de la referencia alcanzó el modelo local, con las dos cifras medidas.
    alcanza = (
        calidad["local"] / calidad["referencia"] * 100
        if calculado and isinstance(calidad.get("local"), (int, float)) and calidad.get("referencia")
        else None
    )
    proporcion = f"; el {alcanza:.0f} % de la calidad de la referencia" if alcanza is not None else ""

    if informe.get("ultima_corrida_error"):
        estado = {"clase": "falla", "texto": f"La última corrida falló: {informe['ultima_corrida_error']}"}
    elif informe.get("criterio_cumplido") is True and calculado:
        texto = (
            f"El método funcionó de principio a fin: {total} tareas por los dos caminos, paquete a ciegas, "
            "dos calificaciones humanas y métricas calculadas."
        )
        if gana:
            texto += (
                f" El modelo local quedó por debajo de la referencia ({_n(calidad.get('local'))} frente a "
                f"{_n(calidad.get('referencia'))} sobre 5{proporcion}) y perdió en {gana.get('referencia')} tareas: la medición no lo favorece."
                if (calidad.get("local") or 0) < (calidad.get("referencia") or 0)
                else f" Calidad promedio: local {_n(calidad.get('local'))}, referencia {_n(calidad.get('referencia'))} sobre 5."
            )
        if calificacion.get("porcentaje_comparables") is not None:
            texto += f" El {calificacion['porcentaje_comparables']:g} % de las tareas quedó con calidad comparable"
            if calificacion.get("kappa_cohen_promedio") is not None:
                texto += (
                    f" y el acuerdo entre las dos personas fue {calificacion.get('kappa_interpretacion') or 'medido'}"
                    f" (kappa de Cohen {_n(calificacion.get('kappa_cohen_promedio'), 3)})"
                )
            texto += "."
        estado = {"clase": "ok", "texto": texto}
    else:
        falta = informe.get("pendiente_calificacion") or "Falta completar la comparación."
        estado = {
            "clase": "parcial",
            "texto": (
                f"Hay {comparacion.get('respuestas_local', 0)} respuestas locales y "
                f"{comparacion.get('respuestas_referencia', 0)} de referencia de {total}. {falta}"
            ),
        }

    if alcanza is not None:
        comparables = calificacion.get("porcentaje_comparables")
        estado["respuesta"] = (
            f"{'Sí, cerca' if alcanza < 100 else 'Sí'}: el modelo local obtuvo {_n(calidad.get('local'))} sobre 5 frente a "
            f"{_n(calidad.get('referencia'))} de la referencia, el {alcanza:.0f} % de su calidad"
            + (f". El {comparables:g} % de las {total} tareas quedó comparable." if comparables is not None else ".")
        )

    fecha = f"Generación de respuestas: {fecha_larga(informe.get('fecha_corrida') or informe.get('fecha'))}."
    if calificacion.get("fecha_calificacion"):
        fecha += (
            " Calificación a ciegas: "
            + _rango_fechas(calificacion.get("fecha_calificacion_inicio"), calificacion.get("fecha_calificacion"))
            + "."
        )

    tipos = informe.get("tipos_de_tarea") or []
    texto_tipos = "; ".join(f"{t['nombre'].lower()} ({t['tareas']})" for t in tipos)
    montaje = tabla(
        ["Componente", "Detalle"],
        [
            ["Equipo", texto_equipo(informe["equipo"]) if informe.get("equipo") else "Sin registrar"],
            [
                "Camino local",
                f"{modelo_local}, modelo abierto servido con Ollama en el equipo. Temperatura 0, semilla fija "
                "y hasta 500 tokens por respuesta.",
            ],
            [
                "Camino de referencia",
                f"{modelo_ref} de {proveedor.capitalize() or 'un proveedor comercial'}, por su API. Temperatura 0. "
                "La clave de acceso se escribe al correr y no se guarda en disco.",
            ],
            [
                "Tareas",
                f"{total} tareas con datos ficticios de trámites públicos"
                + (f": {texto_tipos}." if texto_tipos else ".")
                + " Cada tarea trae el texto sobre el que hay que trabajar.",
            ],
            [
                "Calificadores",
                (", ".join(calificadores) + ". " if calificadores else "Dos personas. ")
                + "Cada persona califica por separado, en una hoja web que solo muestra «respuesta A» y «respuesta B».",
            ],
            ["Escala", "De 1 a 5 en cuatro dimensiones: exactitud, completitud, tono y utilidad."],
        ],
        anchos=[1, 3.4],
    )

    semilla = informe.get("semilla_paquete")
    procedimiento = pasos(
        [
            f"Las {total} tareas se envían, con la misma instrucción, al modelo local y al servicio comercial. "
            "De cada respuesta se guarda el texto, el tiempo y, en la referencia, los tokens que reporta el proveedor.",
            "Para cada tarea se sortea cuál respuesta aparece como A y cuál como B"
            + (f" (semilla {semilla})" if semilla else "")
            + ". El paquete que reciben los calificadores no dice qué sistema escribió cada una; la clave queda en un archivo aparte.",
            "Dos personas califican por separado cada respuesta, sin ver la clave ni las notas de la otra.",
            "Al cerrar las dos calificaciones se abre la clave. La calidad de una respuesta es el promedio de sus "
            "cuatro dimensiones; la de un camino en una tarea, el promedio de las dos personas.",
            "Una tarea es «comparable» si la diferencia entre los dos caminos es de 1 punto o menos.",
            "El acuerdo entre las dos personas se mide con el kappa de Cohen en cada dimensión.",
        ]
    )

    resultados: list = []
    if calculado:
        if costo_ref.get("usd_por_tarea") is not None:
            tarifa = costo_ref.get("tarifa") or {}
            celda_costo_ref = f"{costo_ref['usd_por_tarea']:.5f}"
            nota_costo = (
                f"El costo de la referencia sale de los tokens medidos ({costo_ref.get('tokens_entrada')} de entrada y "
                f"{costo_ref.get('tokens_salida')} de salida en las {costo_ref.get('tareas_con_tokens')} tareas) y de la "
                f"tarifa de lista: {tarifa.get('usd_por_millon_entrada')} USD por millón de tokens de entrada y "
                f"{tarifa.get('usd_por_millon_salida')} de salida"
                + (f" ({tarifa['fuente']}" + (f", consultada el {tarifa['fecha_consulta']}" if tarifa.get("fecha_consulta") else "") + ")" if tarifa.get("fuente") else "")
                + f". Total de la corrida: {costo_ref.get('usd_total'):.4f} USD."
            )
        elif costo_ref.get("tareas_con_tokens"):
            celda_costo_ref = "Sin tarifa confirmada"
            nota_costo = (
                f"El uso de la referencia sí está medido: {costo_ref.get('tokens_entrada')} tokens de entrada y "
                f"{costo_ref.get('tokens_salida')} de salida en las {costo_ref.get('tareas_con_tokens')} tareas "
                f"({_n(costo_ref.get('tokens_entrada_por_tarea'), 1)} y {_n(costo_ref.get('tokens_salida_por_tarea'), 1)} por tarea). "
                "Falta multiplicarlo por la tarifa vigente del proveedor; no se escribe un valor en dólares sin confirmarla."
            )
        else:
            celda_costo_ref = "Sin medir"
            nota_costo = "La corrida no guardó los tokens de la referencia."
        comparables = calificacion.get("porcentaje_comparables")
        n_comparables = total - len(analisis.get("no_comparables") or []) if analisis else None
        resultados += [
            tabla(
                ["Medida", f"Local ({modelo_local})", f"Referencia ({modelo_ref})"],
                [
                    [b("Calidad promedio (1 a 5)"), b(_n(calidad.get("local"))), b(_n(calidad.get("referencia")))],
                    ["Tiempo promedio por tarea (s)", _n(local.get("promedio_caliente_s")), _n(referencia.get("promedio_caliente_s"))],
                    ["Tiempo máximo por tarea (s)", _n(local.get("maximo_caliente_s")), _n(referencia.get("maximo_caliente_s"))],
                    ["Tiempo de la primera tarea (s)", _n(local.get("primera_s")), _n(referencia.get("primera_s"))],
                    ["Costo por tarea (USD)", "0, sin contar energía ni equipo", celda_costo_ref],
                ],
                anchos=[2.2, 1.6, 1.6],
                titulo="Tabla 1. Lo que pide medir la especificación",
                alinear=["L", "R", "R"],
            ),
            p(
                b(f"Tareas comparables: {_pct(comparables, 0)}"),
                (f" ({n_comparables} de {total})" if n_comparables is not None else ""),
                ". ",
                b(f"Kappa de Cohen promedio: {_n(calificacion.get('kappa_cohen_promedio'), 3)}"),
                f", acuerdo {calificacion.get('kappa_interpretacion') or 'sin interpretar'} entre las dos personas. "
                "El promedio y el máximo de tiempo excluyen la primera tarea, que incluye la carga del modelo. ",
                nota_costo,
            ),
        ]
        if gana:
            resultados.append(
                p(
                    b("Tarea por tarea: "),
                    f"la referencia fue mejor en {gana.get('referencia')}, hubo empate en {gana.get('empate')} y el "
                    f"modelo local fue mejor en {gana.get('local')}.",
                )
            )
        por_tipo = analisis.get("por_tipo") or []
        if por_tipo:
            resultados.append(
                tabla(
                    ["Tipo de tarea", "Tareas", "Local", "Referencia", "Comparables", "Gana local", "Gana referencia"],
                    [
                        [
                            t.get("nombre"),
                            str(t.get("tareas")),
                            _n(t.get("local")),
                            _n(t.get("referencia")),
                            f"{t.get('comparables')} de {t.get('tareas')}",
                            str(t.get("gana_local")),
                            str(t.get("gana_referencia")),
                        ]
                        for t in por_tipo
                    ],
                    anchos=[3, 0.8, 0.8, 1.1, 1.3, 1.1, 1.4],
                    titulo="Tabla 2. Calidad por tipo de tarea",
                    alinear=["L", "R", "R", "R", "R", "R", "R"],
                )
            )
        no_comparables = analisis.get("no_comparables") or []
        if no_comparables:
            pierde_local = [t["id"] for t in no_comparables if t.get("gana") == "referencia"]
            gana_local = [t["id"] for t in no_comparables if t.get("gana") == "local"]
            frase = f"En {_plural(len(no_comparables), 'tarea', 'tareas')} la diferencia pasó de 1 punto"
            if pierde_local:
                frase += f": en {', '.join(pierde_local)} el modelo local quedó claramente por debajo"
            if gana_local:
                frase += f"{' y' if pierde_local else ':'} en {', '.join(gana_local)} quedó por encima"
            resultados.append(p(frase + "."))
            filas_nc, sobran = _recortar(
                [
                    [t.get("id"), t.get("tipo"), _n(t.get("local"), 3), _n(t.get("referencia"), 3), _n(t.get("diferencia"), 3)]
                    for t in no_comparables
                ],
                8,
            )
            resultados.append(
                tabla(
                    ["Tarea", "Tipo", "Local", "Referencia", "Diferencia"],
                    filas_nc,
                    anchos=[0.8, 3.4, 0.9, 1.1, 1.1],
                    titulo="Tabla 3. Tareas no comparables",
                    alinear=["L", "L", "R", "R", "R"],
                )
            )
            if sobran:
                resultados.append(p(f"Hay {sobran} más en los datos."))
        dimensiones = analisis.get("dimensiones") or []
        if dimensiones:
            resultados.append(
                tabla(
                    ["Dimensión", "Local", "Referencia", "Kappa de Cohen", "Acuerdo", "Kappa cuadrático", "Misma nota", "Notas en 5"],
                    [
                        [
                            NOMBRE_DIMENSION.get(d.get("dimension"), d.get("dimension")),
                            _n(d.get("local")),
                            _n(d.get("referencia")),
                            _n(d.get("kappa_cohen"), 3),
                            d.get("interpretacion") or "",
                            _n(d.get("kappa_cuadratico"), 3),
                            _pct(d.get("acuerdo_exacto_pct"), 1),
                            _pct(d.get("notas_en_cinco_pct"), 1),
                        ]
                        for d in dimensiones
                    ],
                    anchos=[1.4, 0.8, 1.1, 1.3, 1.3, 1.3, 1.1, 1.1],
                    titulo="Tabla 4. Por dimensión, y cuánto coinciden las dos personas",
                    alinear=["L", "R", "R", "R", "L", "R", "R", "R"],
                )
            )
            resultados.append(
                p(
                    "«Misma nota» es el porcentaje de respuestas en que las dos personas pusieron exactamente el mismo "
                    "número. El kappa descuenta el acuerdo que se daría por azar: como la mayoría de las notas son 5, "
                    "ese acuerdo por azar es alto y el kappa queda bajo aunque coincidan casi siempre. El kappa "
                    "cuadrático pesa menos los desacuerdos de un solo punto."
                )
            )
    else:
        resultados.append(
            aviso(
                b("Calificación incompleta. "),
                calificacion.get("descripcion") or informe.get("pendiente_calificacion") or "Faltan las dos calificaciones a ciegas.",
                clase="parcial",
            )
        )
        resultados.append(
            tabla(
                ["Medida", f"Local ({modelo_local})", f"Referencia ({modelo_ref})"],
                [
                    ["Respuestas generadas", f"{comparacion.get('respuestas_local', 0)} de {total}", f"{comparacion.get('respuestas_referencia', 0)} de {total}"],
                    ["Tiempo promedio por tarea (s)", _n(local.get("promedio_caliente_s")), _n(referencia.get("promedio_caliente_s"))],
                    ["Calidad promedio (1 a 5)", "Sin calificar", "Sin calificar"],
                ],
                anchos=[2.2, 1.6, 1.6],
                titulo="Tabla 1. Lo medido hasta ahora",
                alinear=["L", "R", "R"],
            )
        )
    lista_control = informe.get("protocolo_checklist") or []
    if lista_control and not calculado:
        resultados.append(
            tabla(
                ["Paso del método", "Medido", "¿Cumple?"],
                [[c.get("item"), c.get("medido"), _si_no(bool(c.get("cumple")))] for c in lista_control],
                anchos=[3, 2.4, 0.9],
                titulo="Estado del método",
            )
        )

    limitaciones: list = [
        [
            b("Tareas ficticias y con el texto a la vista. "),
            "Cada tarea incluye el documento sobre el que se trabaja, así que se mide si el modelo aplica bien la "
            "instrucción, no si conoce la norma de memoria.",
        ],
        [
            b("Muestra pequeña. "),
            f"Son {total} tareas"
            + (f", {tipos[0]['tareas']} por tipo" if tipos and len({t["tareas"] for t in tipos}) == 1 else "")
            + ". Las diferencias entre tipos de tarea son indicativas.",
        ],
    ]
    if calificacion.get("limitacion_evaluadores") or informe.get("limitacion_calificadores"):
        limitaciones.append(
            [b("Calificadores cercanos al proyecto. "), calificacion.get("limitacion_evaluadores") or informe.get("limitacion_calificadores")]
        )
    limitaciones += [
        [
            b("La escala se queda corta por arriba. "),
            "Con casi todas las notas en 5, la escala distingue poco entre respuestas buenas y el kappa pierde fuerza. "
            "En el proyecto conviene usar tareas más difíciles o una rúbrica más exigente.",
        ],
        [
            b("Un solo modelo local, pequeño. "),
            f"{modelo_local} es un modelo de tamaño reducido, elegido porque corre en un portátil. No representa a todos los modelos abiertos.",
        ],
        [
            b("El costo local no es cero en la realidad. "),
            "No se paga por consulta, pero hay energía y equipo, que esta prueba no midió.",
        ],
        [
            b("Tiempos de la referencia dependen de la red. "),
            "Incluyen el viaje por internet hasta el proveedor; los del modelo local no.",
        ],
    ]

    secciones = [
        seccion(
            "1. Objetivo",
            p(
                "Mostrar que el método de evaluación comparativa del proyecto ya funciona a pequeña escala: las "
                "mismas tareas pasan por un modelo local y por un servicio comercial, dos personas califican a "
                "ciegas y las métricas se calculan de forma reproducible."
            ),
            p(
                b("Criterio de éxito: "),
                "que el método funcione. No se exige que gane el modelo local; si pierde en algunas tareas, eso "
                "muestra que la medición es honesta.",
            ),
        ),
        seccion("2. Montaje", montaje),
        seccion("3. Procedimiento", procedimiento),
        seccion("4. Resultados", *resultados),
        seccion("5. Limitaciones", lista(limitaciones)),
        _seccion_enlaces(
            3,
            ["demo3_comparacion/", "interfaz/demo3_informe.py"],
            [
                "resultados/demo3/generaciones.json",
                "resultados/demo3/ciego.json",
                "resultados/demo3/clave.json",
                "resultados/demo3/calificaciones/",
                "resultados/demo3/metricas.json",
            ],
            [
                [
                    b("Paquete a ciegas: "),
                    "identificador ",
                    cod(str(paquete.get("hash") or "")[:16]),
                    ". Sirve para comprobar que las dos personas calificaron el mismo paquete.",
                ]
            ]
            if paquete.get("hash")
            else None,
        ),
    ]
    return _documento(3, estado, _ficha(3, informe, fecha), secciones, informe)


# --- Demo 4 ------------------------------------------------------------------------


# Con la mitad o más de las palabras mal, la respuesta corta a «¿entienden el palenquero?» es «No».
WER_NO_ENTIENDE = 50


def _traduccion_demo4(traduccion: dict) -> dict:
    """Bloques de la prueba por escrito (traducción español–palenquero). Vacío si no se ha medido."""
    direcciones = traduccion.get("direcciones") or []
    if not direcciones:
        return {}
    fuente = traduccion.get("fuente") or {}
    autores = fuente.get("autores") or []
    de_autores = f", de {', '.join(autores[:-1])} y {autores[-1]}" if len(autores) > 1 else f", de {autores[0]}" if autores else ""
    libro = f"«{fuente.get('titulo') or 'libro sin título registrado'}»{de_autores}"
    estrofas, poemas = int(traduccion.get("estrofas") or 0), int(traduccion.get("poemas") or 0)
    muestra = f"{_plural(estrofas, 'estrofa', 'estrofas')} de {_plural(poemas, 'poema', 'poemas')}"
    sistemas = traduccion.get("sistemas") or {}
    local, referencia = sistemas.get("local") or {}, sistemas.get("referencia") or {}
    nombre_local = f"Modelo local ({local.get('modelo')})" if local.get("modelo") else "Modelo local"
    nombre_ref = f"Referencia comercial ({referencia.get('modelo')})" if referencia.get("modelo") else "Referencia comercial"

    filas, no_supera, supera = [], {"local": [], "referencia": []}, {"local": [], "referencia": []}
    for d in direcciones:
        sentido = f"{d.get('origen')} → {d.get('destino')}"
        control = d.get("control") or {}
        filas.append([sentido, "Sin traducir (control)", _n(control.get("chrf")), _pct(control.get("palabras_pct")), "—"])
        for clave, nombre in (("local", nombre_local), ("referencia", nombre_ref)):
            medida = d.get(clave)
            if not medida:
                filas.append(["", nombre, "Sin correr", "—", "—"])
                continue
            filas.append(["", b(nombre), b(_n(medida.get("chrf"))), _pct(medida.get("palabras_pct")), _pct(medida.get("copiadas_pct"))])
            (supera if (medida.get("chrf") or 0) > (control.get("chrf") or 0) else no_supera)[clave].append(sentido)

    def veredicto(clave: str, nombre: str) -> str:
        if not supera[clave] and not no_supera[clave]:
            return ""
        if not supera[clave]:
            return f"{nombre} no superó al control en ninguna dirección: devolver el texto sin tocar se parece igual o más a la traducción humana. "
        if not no_supera[clave]:
            return f"{nombre} superó al control en las dos direcciones. "
        return f"{nombre} superó al control solo en {supera[clave][0]}. "

    bloques: list = [
        h3("Por escrito: traducción entre español y palenquero"),
        p(
            f"La misma pregunta, sin audio. Cada modelo tradujo {muestra} del libro {libro}, que trae cada poema en "
            "las dos lenguas, y su salida se comparó con la traducción humana del libro."
        ),
        tabla(
            ["Dirección", "Sistema", "chrF (0 a 100)", "Palabras acertadas", "Palabras copiadas del origen"],
            filas,
            anchos=[1.7, 2.4, 1, 1.1, 1.3],
            titulo=f"Tabla 2. Traducción de {muestra} frente a la traducción humana",
            alinear=["L", "L", "R", "R", "R"],
        ),
        p(
            veredicto("local", "El modelo local"),
            veredicto("referencia", "La referencia comercial"),
            "El chrF mide cuánto se parecen las letras de la salida a las de la traducción humana. El control es no "
            "traducir: como el palenquero comparte vocabulario con el español, el texto sin tocar ya se parece algo. "
            "Un modelo que no supera esa cifra no está aportando la lengua.",
        ),
    ]
    ejemplos = [e for e in traduccion.get("ejemplos") or [] if e.get("origen") and e.get("humana")]
    if ejemplos:
        con_ref = any(e.get("referencia") for e in ejemplos)
        nombres = {"es-pal": "español → palenquero", "pal-es": "palenquero → español"}
        bloques.append(
            tabla(
                ["Dirección", "Texto de origen", "Traducción humana", "Modelo local"] + (["Referencia"] if con_ref else []),
                [
                    [nombres.get(e.get("direccion"), e.get("direccion"))]
                    + [" / ".join(e.get(campo) or []) or "—" for campo in ("origen", "humana", "local")]
                    + ([" / ".join(e.get("referencia") or []) or "—"] if con_ref else [])
                    for e in ejemplos
                ],
                anchos=[1.3, 2, 2, 2] + ([2] if con_ref else []),
                titulo=f"Ejemplo: dos versos del poema «{ejemplos[0].get('poema')}» (páginas {ejemplos[0].get('paginas')})",
            )
        )

    limitaciones: list = [
        [
            b("La traducción de los poemas es literaria. "),
            f"Hay una sola traducción humana y es libre, así que una traducción correcta con otras palabras también "
            f"puntúa bajo. Las cifras sirven para comparar contra el control, no como nota de calidad. Son {muestra} "
            "de un solo libro.",
        ]
    ]
    pendientes = []
    if traduccion.get("por_verificar"):
        pendientes.append("revisar la transcripción contra el libro impreso (salió de fotos)")
    if not fuente.get("permiso"):
        pendientes.append("pedir permiso a los autores para usar los poemas en el proyecto")
    if not referencia.get("modelo"):
        pendientes.append("correr la referencia comercial")
    if pendientes:
        limitaciones.append([b("Pendiente en la prueba por escrito: "), "; ".join(pendientes) + "."])

    por_clave = {d.get("clave"): d for d in direcciones}
    directa = por_clave.get("es-pal") or {}
    frase_estado = ""
    if directa.get("local"):
        frase_estado = (
            f" Por escrito, al traducir {muestra} al palenquero, el modelo local obtuvo chrF "
            f"{_n(directa['local'].get('chrf'))}; dejar el texto sin traducir ya da {_n((directa.get('control') or {}).get('chrf'))}."
        )
    respuesta = ""
    if directa.get("local"):
        respuesta = (
            f" Al traducir poemas al palenquero, el modelo local obtuvo chrF {_n(directa['local'].get('chrf'))}; "
            f"no traducir da {_n((directa.get('control') or {}).get('chrf'))}."
        )
    return {
        "bloques": bloques,
        "limitaciones": limitaciones,
        "estado": frase_estado,
        "respuesta": respuesta,
        "montaje": [
            [
                "Prueba por escrito",
                [
                    f"{muestra} ({(traduccion.get('versos') or {}).get('palenquero', '—')} versos en palenquero) del libro {libro}. "
                    f"{nombre_local}"
                    + (f", versión {local.get('version')} en {local.get('motor')}" if local.get("version") else "")
                    + (f"; {nombre_ref.lower()}." if referencia.get("modelo") else "; referencia comercial sin correr.")
                    + f" Métrica: chrF ({traduccion.get('metrica') or 'sacrebleu'})."
                ],
            ]
        ],
        "pasos": [
            "Por escrito: cada modelo traduce cada estrofa en las dos direcciones, con temperatura 0. Se calcula el chrF "
            "frente a la traducción humana y se compara con el control de no traducir.",
        ],
    }


def _demo4(informe: dict) -> dict:
    escrito = _traduccion_demo4(informe.get("traduccion") or {})
    variedades = informe.get("variedades") or []
    por_clave = {v.get("clave") or ("palenquero" if "palenq" in str(v.get("variedad")) else "costeno"): v for v in variedades}
    minimo = int(informe.get("frases_minimas_protocolo") or 30)
    maximo = int(informe.get("frases_maximas_protocolo") or 50)
    pendiente = informe.get("pendiente") or []
    if isinstance(pendiente, str):
        pendiente = [pendiente]
    idioma = informe.get("idioma_whisper") or "es"
    nombres = (("palenquero", "Palenquero"), ("costeno", "Español costeño"))

    cifras = "; ".join(
        f"{nombre.lower()}, WER {_pct(por_clave[clave].get('wer_porcentaje'))} con {_plural(int(por_clave[clave].get('frases') or 0), 'frase', 'frases')}"
        for clave, nombre in nombres
        if clave in por_clave
    )
    faltan = [nombre.lower() for clave, nombre in nombres if clave not in por_clave]
    cortas = [nombre.lower() for clave, nombre in nombres if clave in por_clave and int(por_clave[clave].get("frases") or 0) < minimo]
    if not variedades:
        estado = {"clase": "pendiente", "texto": "Todavía no hay frases con transcripción correcta y del sistema. No se calculó ningún WER."}
    elif faltan:
        estado = {
            "clase": "parcial",
            "texto": f"Hay cifra para {cifras}. Falta la de {' y '.join(faltan)}: sin audios con su transcripción correcta no se calcula.",
        }
    elif cortas:
        estado = {
            "clase": "parcial",
            "texto": f"Hay una cifra por variedad ({cifras}), pero con menos frases que las {minimo} a {maximo} del protocolo en {' y '.join(cortas)}.",
        }
    else:
        estado = {"clase": "ok", "texto": f"Una cifra por variedad, con la muestra del protocolo: {cifras}."}
    estado["texto"] += escrito.get("estado", "")
    pal = (por_clave.get("palenquero") or {}).get("wer_porcentaje")
    if isinstance(pal, (int, float)):
        cos = (por_clave.get("costeno") or {}).get("wer_porcentaje")
        estado["respuesta"] = (
            f"{'No' if pal >= WER_NO_ENTIENDE else 'Solo en parte'}: al transcribir palenquero hablado, el error de palabras fue de "
            f"{_pct(pal)}"
            + (f", frente a {_pct(cos)} en español costeño." if isinstance(cos, (int, float)) else ".")
            + escrito.get("respuesta", "")
        )

    modelo = informe.get("modelo") or "Whisper small, sin ajustar"
    montaje_filas = [
        ["Equipo", texto_equipo(informe["equipo"]) if informe.get("equipo") else "Sin registrar"],
        ["Modelo", f"Whisper ({modelo}). Es el modelo tal como se descarga, sin entrenamiento adicional."],
        [
            "Idioma del reconocimiento",
            (
                "Fijado en español para las dos variedades. Whisper no incluye el palenquero entre sus idiomas, "
                "así que se mide con la misma configuración que usaría hoy una entidad."
                if idioma == "es"
                else "Detección automática de idioma en las dos variedades."
            ),
        ],
    ]
    for clave, nombre in nombres:
        v = por_clave.get(clave)
        origen = (v or {}).get("origen") or {}
        if v:
            partes = []
            if origen.get("demo1"):
                partes.append(f"{origen['demo1']} grabadas en la pantalla del demo 1")
            if origen.get("carpeta"):
                partes.append(f"{origen['carpeta']} subidas al corpus")
            detalle = f"{_plural(int(v.get('frases') or 0), 'frase', 'frases')}" + (f": {' y '.join(partes)}." if partes else ".")
        else:
            detalle = "Sin frases todavía."
        if clave == "palenquero":
            detalle += (
                " Deben ser grabaciones públicas o de una persona hablante designada por la Fundación Chano y "
                "Chalole, con consentimiento y aval."
            )
        montaje_filas.append([f"Corpus de {nombre.lower()}", detalle])
    montaje_filas.append(["Cálculo", "Biblioteca jiwer, sobre el texto en minúsculas y sin puntuación. Se conservan las tildes."])
    montaje_filas += escrito.get("montaje", [])

    filas_wer = []
    for clave, nombre in nombres:
        v = por_clave.get(clave)
        if not v:
            filas_wer.append([nombre, "0", "—", "—", "—", "—", "Sin medir"])
            continue
        d = v.get("detalle") or {}
        filas_wer.append(
            [
                nombre,
                str(v.get("frases")),
                str(d.get("palabras_referencia", "—")),
                str(d.get("sustituciones", "—")),
                str(d.get("eliminaciones", "—")),
                str(d.get("inserciones", "—")),
                b(_n(v.get("wer_porcentaje"))),
            ]
        )
    resultados: list = [
        tabla(
            ["Variedad", "Número de frases", "Palabras dichas", "Cambiadas", "Omitidas", "Agregadas", "WER (%)"],
            filas_wer,
            anchos=[1.8, 1.4, 1.3, 1.1, 1.0, 1.1, 1.0],
            titulo="Tabla 1. Error de palabras por variedad",
            alinear=["L", "R", "R", "R", "R", "R", "R"],
        ),
        p(
            "El WER es la suma de palabras cambiadas, omitidas y agregadas, dividida por las palabras que de verdad "
            "se dijeron. Se calcula sobre todo el conjunto de frases de la variedad, no como promedio de cada frase. "
            "Un WER de 20 % significa que, de cada cinco palabras, el sistema falla en una."
        ),
    ]
    for clave, nombre in nombres:
        v = por_clave.get(clave)
        if not v:
            continue
        frases = sorted((v.get("detalle") or {}).get("por_frase") or [], key=lambda f: -(f.get("wer") or 0))
        peores = [f for f in frases if (f.get("wer") or 0) > 0][:5]
        if peores:
            resultados.append(
                tabla(
                    ["Transcripción correcta", "Transcripción del sistema", "WER"],
                    [[f.get("referencia", "").strip(), f.get("hipotesis", "").strip(), _pct((f.get("wer") or 0) * 100, 1)] for f in peores],
                    anchos=[3, 3, 0.7],
                    titulo=f"{nombre}: las frases con más error",
                    alinear=["L", "L", "R"],
                )
            )
        sin_error = sum(1 for f in frases if not f.get("wer"))
        if frases:
            resultados.append(
                p(f"{nombre}: {sin_error} de {len(frases)} frases quedaron sin ningún error.")
            )
    if pendiente:
        frases_pendientes = [str(x).strip().rstrip(".") + "." for x in pendiente if str(x).strip()]
        resultados.append(
            aviso(b("Lo que falta. "), " ".join(x[0].upper() + x[1:] for x in frases_pendientes), clase="parcial")
        )
    if len(por_clave) == 2:
        pal, cos = por_clave["palenquero"].get("wer_porcentaje"), por_clave["costeno"].get("wer_porcentaje")
        if isinstance(pal, (int, float)) and isinstance(cos, (int, float)):
            relacion = "más alto" if pal > cos else "más bajo" if pal < cos else "igual"
            resultados.append(
                p(
                    f"El error en palenquero ({_pct(pal)}) es {relacion} que en español costeño ({_pct(cos)}). "
                    "La especificación esperaba un error alto en palenquero y moderado en costeño."
                )
            )
    resultados += escrito.get("bloques", [])

    limitaciones: list = []
    for clave, nombre in nombres:
        v = por_clave.get(clave)
        if v and int(v.get("frases") or 0) < minimo:
            limitaciones.append(
                [
                    b(f"Muestra corta en {nombre.lower()}. "),
                    f"Son {_plural(int(v.get('frases') or 0), 'frase', 'frases')}; el protocolo pide de {minimo} a {maximo}. "
                    "Con tan pocas, unas cuantas palabras mueven el porcentaje varios puntos.",
                ]
            )
    if "costeno" in por_clave and (por_clave["costeno"].get("origen") or {}).get("demo1"):
        limitaciones.append(
            [
                b("Las frases de costeño son las del demo 1. "),
                "Comparten sus límites: pocas voces y frases leídas de un guion.",
            ]
        )
    limitaciones += [
        [
            b("El palenquero no tiene una sola forma de escribirse. "),
            "El WER compara texto contra texto, así que depende de la ortografía que use quien fija la "
            "transcripción correcta. Esa convención la debe avalar la comunidad hablante.",
        ],
        [
            b("El WER cuenta palabras, no gravedad. "),
            "Un cambio de género pesa lo mismo que confundir el nombre de un trámite.",
        ],
        [
            b("Un solo modelo y un solo tamaño. "),
            "Se midió Whisper small; los modelos más grandes pueden dar cifras distintas.",
        ],
        [
            b("Una sola persona fija cada transcripción correcta. "),
            "No hubo doble revisión de las referencias.",
        ],
    ]
    limitaciones += escrito.get("limitaciones", [])

    secciones = [
        seccion(
            "1. Objetivo",
            p(
                "Mostrar, con un número, cuánto fallan hoy los modelos con el palenquero, hablado y escrito. El español "
                "costeño se mide con el mismo método y sirve de comparación. Justifica el objetivo específico 3 del proyecto."
            ),
            p(b("Criterio de éxito: "), "una cifra clara de error por cada variedad."),
        ),
        seccion("2. Montaje", tabla(["Componente", "Detalle"], montaje_filas, anchos=[1, 3.4])),
        seccion(
            "3. Procedimiento",
            pasos(
                [
                    f"Se reúnen de {minimo} a {maximo} frases por variedad, cada una con su audio y su transcripción correcta.",
                    "Whisper, sin ajustar, transcribe cada audio.",
                    "Las dos transcripciones se pasan a minúsculas y se les quita la puntuación.",
                    "Se calcula el WER de cada variedad con jiwer, sobre todas sus frases juntas.",
                    "Si a una variedad le faltan frases, el informe lo dice y no calcula una cifra para ella.",
                    *escrito.get("pasos", []),
                ]
            ),
        ),
        seccion("4. Resultados", *resultados),
        seccion("5. Limitaciones", lista(limitaciones)),
        _seccion_enlaces(
            4,
            ["demo4_wer/", "medicion.py"],
            ["resultados/demo4/informe.json", "resultados/demo4/traduccion.json", "resultados/demo1/filas.json", "demo4_wer/corpus/"],
            [
                [
                    b("Audios: "),
                    "no se publican grabaciones con voz identificable. Los consentimientos y el aval se conservan, no se suben.",
                ],
                *(
                    [[b("Poemas: "), "son obras con autor. El repositorio publica las cifras y dos versos de ejemplo, no los poemas."]]
                    if escrito
                    else []
                ),
            ],
        ),
    ]
    return _documento(4, estado, _ficha(4, informe, fecha_larga(informe.get("fecha")), "Fecha del cálculo"), secciones, informe)


# --- Demo 5 ------------------------------------------------------------------------


def _demo5(informe: dict) -> dict:
    filas = informe.get("filas") or []
    eventos = informe.get("eventos") or []
    bloqueo = informe.get("bloqueo") or {}
    pasadas, total = int(informe.get("pruebas_pasadas") or 0), int(informe.get("pruebas_total") or len(filas) or 11)
    entidades = sorted({str(e.get("entidad")) for e in eventos if e.get("entidad")})

    if informe.get("criterio_cumplido") is True:
        estado = {
            "clase": "ok",
            "texto": (
                f"El intento de lectura cruzada quedó bloqueado, pasaron {pasadas} de {total} pruebas y el registro "
                "de auditoría conserva su cadena íntegra."
            ),
        }
    else:
        estado = {
            "clase": "falla",
            "texto": (
                f"Pasaron {pasadas} de {total} pruebas. Acceso cruzado bloqueado: {_si_no(bloqueo.get('bloqueado')).lower()}. "
                f"Auditoría íntegra: {_si_no(informe.get('auditoria_integra')).lower()}."
            ),
        }

    estado["respuesta"] = (
        f"{'Sí' if informe.get('criterio_cumplido') is True else 'Todavía no'}: pasaron {pasadas} de {total} pruebas; "
        f"acceso cruzado bloqueado: {_si_no(bloqueo.get('bloqueado')).lower()}; "
        f"auditoría íntegra: {_si_no(informe.get('auditoria_integra')).lower()}."
    )

    python = (informe.get("equipo") or {}).get("python", "")
    montaje = tabla(
        ["Componente", "Detalle"],
        [
            ["Equipo", texto_equipo(informe["equipo"]) if informe.get("equipo") else "Sin registrar"],
            [
                "Prototipo",
                "Un nodo que entrega a cada entidad un agente con su propia caja de archivos. Toda lectura, escritura "
                "y listado pasa por el agente; si la ruta sale de la caja, la operación se niega y se anota.",
            ],
            [
                "Entidades",
                (f"Dos, ficticias: {' y '.join(entidades)}." if entidades else "Dos entidades ficticias."),
            ],
            ["Datos", "Ficticios: un trámite inventado y una lista inventada de cupos escolares."],
            [
                "Registro de auditoría",
                "Cada operación queda en una línea con su resultado y un hash que encadena la línea anterior; "
                "si alguien cambia o borra una línea, la cadena deja de cuadrar.",
            ],
            ["Software", f"Python {python}, pruebas con unittest de la biblioteca estándar. No usa modelo de lenguaje."],
            ["Internet", "No usa red: el prototipo solo lee y escribe archivos en el equipo."],
        ],
        anchos=[1, 3.4],
    )

    resultados: list = [
        p(
            b("Acceso cruzado: "),
            f"el agente de la alcaldía pidió el archivo {bloqueo.get('ruta', '')} de la otra entidad. "
            + (
                f"El nodo lo negó (motivo: {bloqueo.get('motivo', '')}) y dejó el intento en el registro."
                if bloqueo.get("bloqueado")
                else "El nodo NO lo bloqueó."
            ),
        ),
    ]
    if eventos:
        resultados.append(
            tabla(
                ["#", "Entidad", "Acción", "Ruta pedida", "Resultado", "Motivo"],
                [
                    [str(e.get("n")), e.get("entidad"), e.get("accion"), e.get("ruta"), e.get("resultado"), e.get("motivo")]
                    for e in eventos[:MAXIMO_FILAS]
                ],
                anchos=[0.35, 1.9, 0.8, 3.3, 1, 1.9],
                titulo="Tabla 1. Registro de auditoría de la corrida, en orden",
            )
        )
        resultados.append(
            p(
                "Cadena de hashes del registro: ",
                b("íntegra." if informe.get("auditoria_integra") else "ROTA."),
                " Se verifica recalculando el hash de cada línea a partir de la anterior.",
            )
        )
    resultados.append(
        tabla(
            ["Prueba", "Esperado", "Obtenido"],
            [[f.get("prueba"), f.get("esperado"), f.get("obtenido")] for f in filas],
            anchos=[3.3, 4.2, 0.8],
            titulo=f"Tabla 2. Las {total} pruebas automatizadas: {pasadas} de {total} pasaron",
        )
    )

    secciones = [
        seccion(
            "1. Objetivo",
            p(
                "Mostrar que la arquitectura de agentes aislados por entidad ya existe y está probada: dos agentes "
                "de dos entidades trabajan en el mismo nodo y ninguno puede leer ni escribir los archivos del otro."
            ),
            p(b("Criterio de éxito: "), f"acceso cruzado bloqueado y las {total} pruebas pasando."),
        ),
        seccion("2. Montaje", montaje),
        seccion(
            "3. Procedimiento",
            pasos(
                [
                    "Se crea un entorno nuevo con las dos cajas y sus archivos ficticios.",
                    "Cada agente escribe una nota de trabajo en su propia caja.",
                    "El agente de la alcaldía intenta leer un archivo de la gobernación usando una ruta que sale de su caja.",
                    "Se muestra el registro de auditoría y se verifica su cadena de hashes.",
                    f"Se corren las {total} pruebas automatizadas, cada una en un directorio temporal propio: lectura "
                    "y escritura propias, trabajo simultáneo, lectura, escritura y listado cruzados, rutas con «..», "
                    "enlaces simbólicos y auditoría.",
                ]
            ),
        ),
        seccion("4. Resultados", *resultados),
        seccion(
            "5. Limitaciones",
            lista(
                [
                    [
                        b("Entorno simulado. "),
                        "Un solo computador, datos ficticios y entidades inventadas. No hay red ni entidades reales.",
                    ],
                    [
                        b("El aislamiento está en las herramientas del agente. "),
                        "Quien ya controla el proceso de Python puede saltárselo. No se usan usuarios distintos del "
                        "sistema operativo ni contenedores.",
                    ],
                    [
                        b("El registro es un archivo en el mismo equipo. "),
                        "La cadena de hashes detecta si alguien cambia o quita una línea, pero no impide que quien "
                        "tenga acceso al disco borre el archivo o lo reescriba entero.",
                    ],
                    [
                        b("No es el nodo del proyecto. "),
                        "Es la prueba de concepto de la arquitectura (TRL 3). En las fases siguientes el mismo "
                        "aislamiento se debe sostener con entidades reales y con un registro que no dependa de un solo proceso.",
                    ],
                ]
            ),
        ),
        _seccion_enlaces(
            5,
            ["demo5_agentes/nodo.py", "demo5_agentes/test_aislamiento.py", "demo5_agentes/en_vivo.py"],
            ["resultados/demo5/informe.json", "resultados/demo5/pruebas.csv"],
            [[b("Para repetirla: "), cod("python -m demo5_agentes.en_vivo"), "."]],
        ),
    ]
    return _documento(5, estado, _ficha(5, informe, fecha_larga(informe.get("fecha"))), secciones, informe)


# --- Entrada pública ---------------------------------------------------------------

_CONSTRUCTORES = {1: _demo1, 3: _demo3, 4: _demo4, 5: _demo5}


def documento(demo_id: int, informe: dict | None) -> dict:
    """Nota técnica del demo. Sin informe, devuelve una nota que dice que aún no se ha medido."""
    if demo_id not in DEMOS:
        raise KeyError(demo_id)
    if demo_id == 2:
        return _demo2(informe)
    if not informe:
        meta = DEMOS[demo_id]
        return _documento(
            demo_id,
            {"clase": "pendiente", "texto": "Este demo todavía no se ha corrido. No hay cifras que informar."},
            _ficha(demo_id, {}, "Pendiente"),
            [
                seccion("1. Objetivo", p(meta["tesis"]), p(b("Criterio de éxito: "), meta["criterio"])),
                seccion("2. Montaje", p(meta["montaje"])),
            ],
            None,
        )
    return _CONSTRUCTORES[demo_id](informe)


def ruta_nota(demo_id: int) -> Path:
    return NOTAS / f"{ARCHIVO_NOTA[demo_id]}.md"


def escribir_nota(demo_id: int, informe: dict | None) -> Path:
    """Escribe la nota en Markdown en `notas/`. El PDF sale del mismo documento."""
    NOTAS.mkdir(parents=True, exist_ok=True)
    destino = ruta_nota(demo_id)
    texto = a_markdown(documento(demo_id, informe))

    def sin_sello(contenido: str) -> str:
        return "\n".join(linea for linea in contenido.splitlines() if not linea.startswith("Nota generada el "))

    # Si solo cambió la hora de generación, el archivo se deja como está.
    if destino.is_file() and sin_sello(destino.read_text(encoding="utf-8")) == sin_sello(texto):
        return destino
    destino.write_text(texto, encoding="utf-8")
    return destino
