"""Frases cotidianas para el demo 1. Son el guion, no la transcripción correcta.

La transcripción correcta es lo que la persona dijo, y se anota al escucharla.
"""

FRASES = [
    "Buenas, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer?",
    "¿A qué horas atienden hoy en la secretaría de hacienda?",
    "Necesito un turno para el Sisbén. ¿Me lo pueden dar ahora?",
    "¿Dónde queda la oficina del predial? Es que me perdí.",
    "Quiero saber si ya salió la respuesta de mi derecho de petición del mes pasado.",
    "¿Hasta qué hora están recibiendo el pago del impuesto hoy?",
    "Se me dañó el recibo del agua. ¿Cómo pido uno nuevo?",
    "¿El médico de la cita de las tres todavía está atendiendo?",
    "Buenas tardes, ¿me regala el horario del colegio para la reunión de padres?",
    "En mi calle no hay luz desde anoche. ¿A quién le toca eso?",
]

_SIMARRA = {
    "nombre": "Rutsely Simarra Obeso, «La lengua palenquera», Universidad Nacional de Colombia",
    "url": "https://www.humanas.unal.edu.co/colantropos/files/6914/7330/4008/Lengua_palenquera_Simarra.pdf",
}
_DICCIONARIO_2005 = {
    "nombre": "Diccionario lengua palenquera–español (2005), citado por el Centro Virtual Cervantes",
    "url": "https://cvc.cervantes.es/el_rinconete/anteriores/julio_07/12072007_02.asp",
}

# Oraciones publicadas con su traducción, en la ortografía de cada fuente. Antes de grabar,
# el hablante o la Fundación Chano y Chalole confirman que así se dice.
FRASES_PALENQUERO = [
    {"texto": "Suto á bae pa Katagena.", "espanol": "Nosotros nos fuimos para Cartagena.", "fuente": _SIMARRA},
    {"texto": "Ma pueko a kumé eso.", "espanol": "Los puercos se comieron eso.", "fuente": _SIMARRA},
    {"texto": "Ele á kojé un kusa ngandísimo.", "espanol": "Él o ella cogió una cosa grandísima.", "fuente": _SIMARRA},
    {"texto": "Ané kume mbollo mí.", "espanol": "Ellos o ellas se comieron mi bollo.", "fuente": _SIMARRA},
    {
        "texto": "I advedtí mae mí nú komblá eso nú.",
        "espanol": "Yo le advertí a mi mamá que no comprara eso.",
        "fuente": _SIMARRA,
    },
    {"texto": "Tiela lo que kelá sin semblá.", "espanol": "La tierra que quedó sin sembrar.", "fuente": _SIMARRA},
    {"texto": "I tá saká un ma matika ñame.", "espanol": "Yo voy a sacar unas maticas de ñame.", "fuente": _SIMARRA},
    {"texto": "Suto se jablá lengua africano.", "espanol": "Nosotros hablamos una lengua africana.", "fuente": _SIMARRA},
    {"texto": "Ané a tre machete mí.", "espanol": "Ellos o ellas trajeron mi machete.", "fuente": _SIMARRA},
    {
        "texto": "Palenke tiela suto, asino kumo Afrika.",
        "espanol": "Palenque es nuestra tierra, como lo es África.",
        "fuente": _DICCIONARIO_2005,
    },
]
