"""Metadatos de los cinco demos, para la portada y cada página."""

from __future__ import annotations

DEMOS: dict[int, dict] = {
    1: {
        "id": 1,
        "slug": "voz-costeno",
        "titulo": "Voz en español costeño",
        "tesis": "El reconocimiento y la síntesis ya funcionan con habla costeña, y se ve dónde fallan.",
        "montaje": (
            "Whisper small, Piper y un modelo local en Ollama. Tres o cuatro personas del equipo "
            "hablan en costeño natural, con consentimiento escrito."
        ),
        "criterio": "Flujo de punta a punta y al menos un error real de reconocimiento.",
        "criterio_corto": "Flujo completo grabado y al menos un error real de reconocimiento.",
        "responsable": "Anuar Harb",
        "explicacion_simple": (
            "Imagina que le cuentas un secreto a una caja muy lista que vive en este computador. "
            "Tú hablas en costeño, como en la casa o en la tienda. La caja te escucha con sus orejas "
            "(eso es el reconocimiento de voz), escribe lo que entendió y le pide ayuda a otro cerebro "
            "pequeño que también vive aquí adentro, sin internet. Ese cerebro piensa una respuesta y "
            "la caja te la devuelve hablando, con una vocecita inventada (la síntesis). "
            "En este demo no hay truco de nube: todo pasa en la misma mesa. Vamos a grabar frases de "
            "verdad, ver si entendió bien las palabras tuyas y guardar cada intento, bonito o torcido, "
            "para enseñar qué ya sirve y qué todavía se enreda con el acento del Caribe."
        ),
    },
    2: {
        "id": 2,
        "slug": "sin-internet",
        "titulo": "IA completa sin internet",
        "tesis": "Modelo abierto, reconocimiento y síntesis responden juntos en un equipo, con varios usuarios a la vez y sin red.",
        "montaje": "El mismo nodo local; el router desconectado de internet; teléfonos en la página de consulta.",
        "criterio": "Tres usuarios simultáneos; respuesta de voz en menos de 10 s en promedio.",
        "criterio_corto": "3 usuarios a la vez · voz < 10 s promedio · sin internet.",
        "responsable": "Anuar Harb",
        "explicacion_simple": (
            "A veces no hay señal de internet, o no queremos depender de ella. Este demo es como "
            "un parque de juegos que funciona aunque el Wi‑Fi esté apagado: el router sigue encendido "
            "para que los celulares se hablen con el computador, pero la puerta hacia afuera "
            "(internet) queda cerrada. Varias personas —tú, un amigo y otra persona— pueden preguntar "
            "al mismo tiempo desde el teléfono. El computador escucha, piensa con modelos que viven "
            "adentro y responde con voz, sin llamar a nadie en otro país. Cuando pulses correr, "
            "medimos si aguanta varias preguntas juntas y si las respuestas llegan rápido, como cuando "
            "alguien te contesta enseguida en una conversación de verdad."
        ),
    },
    3: {
        "id": 3,
        "slug": "comparacion",
        "titulo": "IA local frente a referencia externa",
        "tesis": "El método de evaluación comparativa a ciegas ya funciona a pequeña escala.",
        "montaje": "40 tareas ficticias; modelo local y un servicio comercial; dos calificadores.",
        "criterio": "El método funciona; no se exige que la IA local gane.",
        "criterio_corto": "Paquete ciego listo y dos calificaciones; no hace falta que gane lo local.",
        "responsable": "Anuar Harb",
        "explicacion_simple": (
            "Es como una competencia de dibujos donde hay dos estudiantes: uno es el computador de "
            "aquí al lado y el otro es un servicio famoso en internet. A los dos les damos las mismas "
            "tareas de mentira —preguntas y ejercicios que inventamos para probarlos— y cada uno escribe "
            "su respuesta. Luego mezclamos todo en un sobre cerrado: las respuestas van marcadas A y B "
            "y nadie sabe cuál la escribió el de la casa ni cuál la escribió el de afuera. Dos personas "
            "adultas las leen y las califican, como jueces en un concurso de talentos a ciegas. "
            "No estamos obligando a que gane el de aquí: solo queremos saber si el juego de evaluar "
            "es justo y si podemos repetirlo sin hacer trampa. Cuando corres el demo, el computador "
            "hace la parte local; si también corres la referencia comercial, se completa el sobre "
            "para que los jueces puedan empezar."
        ),
    },
    4: {
        "id": 4,
        "slug": "wer",
        "titulo": "Línea base del error (WER)",
        "tesis": "Whisper sin ajustar falla en palenquero y en costeño, con un número por variedad.",
        "montaje": "30–50 frases por variedad; jiwer tras normalizar; palenquero con aval de Chano y Chalole.",
        "criterio": "Una cifra clara por variedad.",
        "criterio_corto": "Un WER medido por variedad (palenquero y costeño).",
        "responsable": "Anuar Harb",
        "explicacion_simple": (
            "Hay personas que hablan palenquero o costeño, y queremos un número honesto de cuánto "
            "se equivoca el oído automático cuando aún no lo hemos enseñado con cariño. Imagina que "
            "lees en voz alta un cuento frase por frase y un amigo escribe lo que creyó escuchar. "
            "Después contamos cuántas palabras cambió: ese es el error de reconocimiento (WER). "
            "Aquí el amigo es Whisper, que viene sin entrenar especial para nuestras voces. "
            "Ponemos frases que ya aprobaron hablantes nativos y el demo cuenta los tropiezos por "
            "cada variedad. Así no adivinamos: sabemos con un puntaje claro dónde hay que trabajar "
            "antes de soñar con asistentes para todo el Caribe."
        ),
    },
    5: {
        "id": 5,
        "slug": "agentes",
        "titulo": "Agentes aislados por entidad",
        "tesis": "Dos agentes de dos entidades no pueden leer los archivos del otro; el registro de auditoría queda íntegro.",
        "montaje": "Prototipo con datos ficticios y 11 pruebas automatizadas.",
        "criterio": "Acceso cruzado bloqueado y las 11 pruebas pasando.",
        "criterio_corto": "11/11 pruebas · sin acceso cruzado · auditoría íntegra.",
        "responsable": "Anuar Harb",
        "explicacion_simple": (
            "Piensa en dos casitas de fichas en la misma mesa: una es de la Alcaldía y otra del "
            "Hospital. Cada una tiene su cajón con papeles de mentira (datos de prueba). Los "
            "ayudantes robot —los agentes— solo pueden abrir el cajón de su casa. Si el robot del "
            "Hospital intenta asomarse al cajón de la Alcaldía, la puerta debe quedarse trabada y "
            "decir «no puedes». También llevamos un cuaderno de auditoría: cada vez que alguien "
            "intenta abrir algo, se anota en ese cuaderno y al final revisamos que nadie lo haya "
            "roto ni borrado. Cuando pulses correr, verás en la pantalla cómo se prueban esas reglas "
            "una por una, como si fueran once retos en un videojuego, hasta saber si las casitas "
            "respetan los límites de verdad."
        ),
    },
}


def por_id(demo_id: int) -> dict:
    if demo_id not in DEMOS:
        raise KeyError(demo_id)
    return DEMOS[demo_id]
