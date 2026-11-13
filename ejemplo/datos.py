"""Material sintético del juego de ejemplo. Nada de esto se midió.

Las frases en palenquero de la medición base se documentan con autorización del consejo comunitario
(los audios no se publican; solo cifras y referencia en el repositorio).

Imita lo que sí se midió en `resultados/`: el reconocimiento falla en las palabras locales
y de trámite («Sisbén», «predial», «horas»), el modelo local inventa datos cuando no los
tiene, y el palenquero queda casi irreconocible. Los nombres de personas son ficticios.
"""

from __future__ import annotations

AUTORIZACION_PALENQUERO = (
    "Las frases en palenquero de la medición base se grabaron con autorización del consejo comunitario. "
    "Los audios y la voz identificable no se publican; en el repositorio solo están las cifras y los datos de referencia."
)

# --- Personas (ficticias) -----------------------------------------------------------

# (nombre, probabilidad de que una frase suya salga con error de reconocimiento, inicio de su sesión)
HABLANTES_COSTENO = [
    ("Marelvis Pérez", 0.5, "2026-11-12T19:21:40-05:00"),
    ("Jairo Barrios", 0.7, "2026-11-12T19:38:15-05:00"),
]
# Dos hablantes ficticios más, para llegar a cuatro en el ejemplo sin usar datos de voz reales.
HABLANTES_EXTRA = {
    "Camila Rentería": (0.65, "2026-11-11T00:58:10-05:00"),
    "Diego Molina": (0.45, "2026-11-12T19:05:02-05:00"),
}
HABLANTES_PALENQUERO = [
    ("Hablante de ejemplo 1", "2026-11-12T21:10:20-05:00"),
    ("Hablante de ejemplo 2", "2026-11-12T21:25:45-05:00"),
    ("Hablante de ejemplo 3", "2026-11-12T21:41:10-05:00"),
]
USUARIOS_DEMO2 = ["Marelvis Pérez", "Jairo Barrios", "Dayana Mercado"]
SESION_DEMO2 = "2026-11-12T20:14:05-05:00"
# Segundos entre que una persona oye la respuesta y manda su siguiente consulta.
PAUSA_DEMO2_S = (7, 17)
# Cuánto se alarga una etapa (escuchar, responder, hablar) por cada otra etapa ocupada a la vez.
FRENO_POR_ETAPA_OCUPADA = 0.45
CONSUMO_DEMO2 = {"reposo_w": 7.4, "carga_w": 41.8, "instrumento": "vatímetro de enchufe, resolución de 0,1 W"}

# --- Demo 1: lo que escribiría el reconocimiento ------------------------------------

# Por cada frase del guion (en el orden de voz.frases.FRASES): transcripciones con error.
# Los errores siguen los que sí se midieron: palabras locales, tildes y formas del habla.
TRANSCRIPCIONES_CON_ERROR = [
    [
        "Bueno, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer?",
        "Buenas, vengo a pedir una certificada de residencia. ¿Qué papeles tengo que traer?",
        "Buenas, vengo a pedir un certificado de residencia. ¿Qué papel es que tengo que traer?",
    ],
    [
        "¿A qué hora atienden hoy en la Secretaría de Hacienda?",
        "¿A qué hora atienden hoy en la Secretaría de Hacienda?",
        "¿A qué hora atiende Noi en la Secretaría de Hacienda?",
    ],
    [
        "Necesito un turno para el cisbén. ¿Me lo pueden dar ahora?",
        "Necesito un turno para el sí bien, me lo pueden dar ahora.",
        "Necesito un turno para el sistema. ¿Me lo pueden dar ahora?",
        "Necesito un turno para el 6. Me lo pueden dar ahora.",
    ],
    [
        "Donde queda la oficina del predial, es que me perdí.",
        "¿Dónde queda el oficinal predial? Es que me perdí.",
        "¿Dónde queda la oficina de el pre dial? Es que me perdí.",
    ],
    [
        "Quiero saber si ya salió la respuesta de mi Derecha de Petición del mes pasado.",
        "Quiero saber si ya salió la respuesta de mi derecho a petición de el mes pasado.",
    ],
    [
        "Hasta que ahora están recibiendo el pago del impuesto hoy.",
        "¿Hasta qué hora están recibiendo el pago de impuesto hoy?",
    ],
    [
        "Se me daño el recibo de la agua. ¿Cómo pido uno nuevo?",
        "Se me dañó el recibo del agua, como pido uno nuevo.",
        "Se me daño el recibo del agua. ¿Cómo pido un nuevo?",
    ],
    [
        "¿El médico de la cita de las 3 todavía está atendiendo?",
        "¿El médico de la cita de la tres todavía está atendiendo?",
    ],
    [
        "Buenas tardes, me regale el horario del colegio para la reunión de padre.",
        "Buenas tardes, ¿me regala el horario del colegio para la reunión de padre?",
    ],
    [
        "En mi calle no hay luz desde a noche. ¿A quien le toca eso?",
        "En mi calle no hay luz desde anoche. ¿A quién le toca ese?",
    ],
]

# --- Demo 1: lo que respondería el modelo local -------------------------------------

# Por cada frase del guion: (respuestas sin dato inventado, respuestas con dato inventado,
# probabilidad de que invente). En lo medido, inventó sobre todo la ubicación del predial.
RESPUESTAS = [
    (
        [
            "Para pedir un certificado de residencia necesitas tu cédula de identidad. También podrías necesitar un recibo de servicios.",
            "Lo siento, no tengo la lista de requisitos. Pregunta en la ventanilla de atención al ciudadano.",
        ],
        ["Tienes que traer tu documento de identidad y tu cédula de residencia."],
        0.4,
    ),
    (
        [
            "Lo siento, no tengo ese dato. ¿Podrías preguntar en la recepción o verificar en el sitio web de la alcaldía?",
            "Lo siento, no tengo esa información. Pide el horario al personal de la secretaría.",
        ],
        [],
        0.0,
    ),
    (
        [
            "Lo siento, no tengo información sobre turnos para eso. Puedo ayudarte con otros asuntos de la alcaldía.",
            "Lo siento, no puedo dar turnos. Acércate a la ventanilla y pide uno allí.",
        ],
        [],
        0.0,
    ),
    (
        ["Lo siento, no tengo la dirección de esa oficina. Pregunta en la recepción de la alcaldía."],
        [
            "La oficina del predial está en la avenida principal del centro de la ciudad. ¿Necesitas más información?",
            "La oficina del predial está en la avenida principal, cerca del mercado. ¿Necesitas más información?",
        ],
        0.85,
    ),
    (
        [
            "Lo siento, no tengo ese dato. Pide el radicado de tu solicitud para poder ayudarte mejor.",
            "Lo siento, no tengo ese dato. ¿Podrías decirme tu radicado por favor?",
        ],
        [],
        0.0,
    ),
    (
        [
            "No tengo información sobre el horario de recepción de pagos. ¿Puedes verificar con la secretaría de hacienda?",
            "Lo siento, no tengo ese dato. Pregunta en la caja de la secretaría de hacienda.",
        ],
        [],
        0.0,
    ),
    (
        [
            "Lo siento, no tengo ese dato. Pregunta en la empresa de acueducto cómo pedir un duplicado.",
            "No tengo información sobre el recibo del agua. Puedes pedir ayuda en la oficina de servicios públicos.",
        ],
        [],
        0.0,
    ),
    (
        [
            "Lo siento, no tengo información sobre las citas médicas. Pregunta en la recepción del centro de salud.",
            "No tengo ese dato. ¿Puedes confirmar en la recepción si el médico sigue atendiendo?",
        ],
        [],
        0.0,
    ),
    (
        [
            "Lo siento, no tengo el horario del colegio. Puedes consultarlo en la secretaría del colegio.",
            "No tengo ese dato. ¿Puedes preguntar en la secretaría del colegio?",
        ],
        [],
        0.0,
    ),
    (
        [
            "Lo siento, no tengo ese dato. Puedes reportarlo a la empresa de energía de tu municipio.",
            "No tengo información sobre el servicio de luz. Repórtalo a la empresa de energía.",
        ],
        [],
        0.0,
    ),
]

# --- Demo 4: lo que escribiría Whisper al oír palenquero ----------------------------

# Por cada frase de voz.frases.FRASES_PALENQUERO, tres salidas inventadas con el patrón de
# las medidas: el modelo acerca lo que oye a palabras del español.
PALENQUERO_SISTEMA = [
    ["Su tuá va e para Cartagena.", "Sutoa va y pa Cartagena.", "Su todo va a Epacartagena."],
    ["Mapuerco a comer eso.", "Ma, poco a cumé eso.", "Más puerco acumeso."],
    ["Él la cogió una cosa grandísima.", "Ella coge un cusa andísimo.", "El acojo en cosa gandísimo."],
    ["Ane come bollo mí.", "Anécume, bollo mí.", "A ne cumembo yo mi."],
    ["Y advertí mai mi no comprar eso no.", "Ya de ti mae mi nu combla eso nu.", "Y a ver ti mae mino con la eso no."],
    ["Tierra lo que quedará sin sembrar.", "Tiene lo que quedas en semana.", "Tierra lo que quela sin sembla."],
    ["Y está sacando una matica de ñame.", "Itasaca un mamá Tica ñame.", "Y ta saca un mamático a ñame."],
    ["Su tos se habla lengua africano.", "Sutos hablan lengua africana.", "Su todo se habla la lengua africana."],
    ["Ane atre machete mí.", "Anea tres machetes mí.", "Ana, he a tres machete mi."],
    [
        "Palenque tierra su todo, así no como África.",
        "Palenque tiene la su todo, así no cumo África.",
        "Palenque, tiene la suto, a sino como África.",
    ],
]
RESPUESTAS_PALENQUERO = [
    "Lo siento, no entendí tu pregunta. ¿Puedes repetirla por favor?",
    "Perdón, no entendí eso. ¿Puedes decirlo de otra manera?",
    "Lo siento, no entiendo bien lo que preguntas.",
]

# --- Demo 4: referencia comercial en la prueba por escrito (no se ha corrido) -------

# La referencia entiende algo más que el modelo local, pero sigue lejos de la traducción humana.
REFERENCIA_TRADUCCION = {
    "sistema": {"modelo": "claude-haiku-4-5", "proveedor": "anthropic"},
    "es-pal": {"chrf": 29.37, "palabras_pct": 13.69, "copiadas_pct": 38.52, "segundos_promedio": 1.62},
    "pal-es": {"chrf": 37.84, "palabras_pct": 21.65, "copiadas_pct": 12.31, "segundos_promedio": 1.44},
    # Lo que habría escrito para los dos versos que se publican como ejemplo.
    "versos": {
        "es-pal": ["E bila suto ta", "Kumo pájaro ke ta bae"],
        "pal-es": ["En la vida nosotros somos", "Como palomas"],
    },
}

# Misma carpeta de Drive que las notas medidas (entregables/enlaces.json).
VIDEO_CARPETA = "https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing"
