"""Cuarenta tareas ficticias de entidades del Caribe, para la comparación a ciegas.

Los nombres, radicados y cifras son de laboratorio. No hay datos de personas reales.
"""

from __future__ import annotations

INS_RESUMIR = (
    "Resume la petición en máximo 4 líneas. Di quién pide, qué pide y qué dato falta. "
    "No inventes datos."
)
INS_REDACTAR = (
    "Redacta la respuesta de la entidad en un solo párrafo breve y respetuoso. "
    "No prometas plazos, obras ni entregas que la ficha no autorice. "
    "Si falta un dato, pide solo ese dato."
)
INS_CLASIFICAR = (
    "Clasifica el mensaje en exactamente una etiqueta: "
    "peticion, queja, reclamo, sugerencia, felicitacion, informacion. "
    "Responde solo con la etiqueta, en minúscula y sin punto."
)
INS_EXTRAER = (
    "Devuelve un único objeto JSON con exactamente las claves pedidas. "
    "Si el dato no está en el texto, usa null. No uses markdown ni expliques."
)
INS_NORMA = (
    "Responde la consulta aplicando solo el texto de trabajo. "
    "Si el texto no alcanza para responder, dilo. No cites normas que no estén escritas ahí."
)

TAREAS: list[dict] = [
    {
        "id": "T01",
        "tipo": "resumir_peticion",
        "entidad": "Alcaldía de Galapa (ficticia)",
        "instruccion": INS_RESUMIR,
        "entrada": (
            "Radicado ficticio GA-1042. María del Carmen Gómez, documento de ejemplo terminado en 0001, "
            "barrio El Campito, pide un certificado de residencia para un subsidio de vivienda. "
            "Dice que vive ahí desde 2019. No adjunta recibo de servicio ni declaración de un vecino. "
            "Deja el celular de ejemplo 3000000001."
        ),
    },
    {
        "id": "T02",
        "tipo": "resumir_peticion",
        "entidad": "Inspección de Policía de Soledad (ficticia)",
        "instruccion": INS_RESUMIR,
        "entrada": (
            "Radicado ficticio SO-221. El señor Lázaro Peña, calle 30 con carrera 18, barrio La Paz, "
            "pide que revisen un hueco que lleva tres semanas frente a su casa. Dice que ya se cayó "
            "una moto. No indica el número de la casa ni si ya reportó el daño a la empresa de servicios."
        ),
    },
    {
        "id": "T03",
        "tipo": "resumir_peticion",
        "entidad": "Secretaría de Educación de Bolívar (ficticia)",
        "instruccion": INS_RESUMIR,
        "entrada": (
            "Radicado ficticio BOL-ED-77. La señora Rosa Mercado pide cupo en grado segundo para su hijo "
            "Tomás Mercado, de 7 años, en la IED Los Manglares, institución ficticia de Mahates. "
            "Adjunta registro civil de ejemplo. No adjunta el boletín del año anterior ni dice si el niño "
            "ya está matriculado en otro colegio."
        ),
    },
    {
        "id": "T04",
        "tipo": "resumir_peticion",
        "entidad": "Alcaldía de Mahates (ficticia)",
        "instruccion": INS_RESUMIR,
        "entrada": (
            "Radicado ficticio MA-15. La Junta de Acción Comunal del corregimiento de San Basilio, "
            "en este ejercicio una junta ficticia, pide el arreglo de un puente de madera que usa el "
            "transporte escolar. El puente está sobre un caño. No envían fotos ni el número de familias "
            "afectadas. Firman como presidenta de ejemplo: Nidia Cassiani."
        ),
    },
    {
        "id": "T05",
        "tipo": "resumir_peticion",
        "entidad": "Aguas del Río (empresa ficticia)",
        "instruccion": INS_RESUMIR,
        "entrada": (
            "PQR ficticia AR-900. Doña Eulalia Jiménez, manzana 4 casa 2 del barrio La Orilla, en Ciénaga, "
            "informa que lleva seis días sin agua. El último recibo que menciona es de agosto, por un valor "
            "de ejemplo de 48.000 pesos, y dice que está paga. Pide carro tanque. No da el número del contrato."
        ),
    },
    {
        "id": "T06",
        "tipo": "resumir_peticion",
        "entidad": "Puesto de salud El Carmen (ficticio)",
        "instruccion": INS_RESUMIR,
        "entrada": (
            "Turno ficticio PS-33. Don Héctor Viloria, de 71 años, pide una cita de vacunación. "
            "No describe síntomas ni diagnósticos. Dice que puede ir los martes en la mañana y que "
            "su nieta lo acompaña. No indica el régimen de salud ni el número de documento."
        ),
    },
    {
        "id": "T07",
        "tipo": "resumir_peticion",
        "entidad": "IED Los Manglares (institución ficticia)",
        "instruccion": INS_RESUMIR,
        "entrada": (
            "Comunicación ficticia IE-12. La docente Ana Ferrer pide marcadores, resmas de papel y "
            "un video beam para el grado noveno. Hay 36 estudiantes en el curso. La reunión de padres "
            "es el viernes. No dice la fecha de la reunión ni el salón."
        ),
    },
    {
        "id": "T08",
        "tipo": "resumir_peticion",
        "entidad": "Personería de Santa Marta (ficticia)",
        "instruccion": INS_RESUMIR,
        "entrada": (
            "Radicado ficticio SM-P-58. El ciudadano Pablo Gómez pregunta si ya salió la respuesta "
            "a su derecho de petición del mes pasado, radicado ficticio SM-P-19, sobre el alumbrado "
            "de la calle 15. No adjunta copia del radicado anterior. Deja correo de ejemplo pablo.ejemplo@correo.test."
        ),
    },
    {
        "id": "T09",
        "tipo": "redactar_respuesta",
        "entidad": "Alcaldía de Galapa (ficticia)",
        "instruccion": INS_REDACTAR,
        "entrada": (
            "Ficha de respuesta autorizada: acusar recibo del radicado GA-1042; pedir únicamente "
            "el recibo de un servicio público del barrio o una declaración de dos vecinos; "
            "no prometer la fecha del certificado. Trato de ventanilla, en español sencillo."
        ),
    },
    {
        "id": "T10",
        "tipo": "redactar_respuesta",
        "entidad": "Inspección de Policía de Soledad (ficticia)",
        "instruccion": INS_REDACTAR,
        "entrada": (
            "Ficha de respuesta autorizada: informar que la queja SO-221 quedó registrada; "
            "pedir el número exacto de la casa; no prometer la fecha del arreglo del hueco; "
            "indicar que un inspector ficticio hará visita, sin fijar día."
        ),
    },
    {
        "id": "T11",
        "tipo": "redactar_respuesta",
        "entidad": "Secretaría de Educación de Bolívar (ficticia)",
        "instruccion": INS_REDACTAR,
        "entrada": (
            "Ficha de respuesta autorizada: no hay cupo asignado todavía; pedir el boletín del año "
            "anterior o una constancia de que el niño no estudió; no prometer cupo en la IED Los Manglares."
        ),
    },
    {
        "id": "T12",
        "tipo": "redactar_respuesta",
        "entidad": "Alcaldía de Mahates (ficticia)",
        "instruccion": INS_REDACTAR,
        "entrada": (
            "Ficha de respuesta autorizada: agradecer el reporte del puente; pedir fotos y el número "
            "de familias que lo usan para llegar a la escuela; no prometer obra ni presupuesto."
        ),
    },
    {
        "id": "T13",
        "tipo": "redactar_respuesta",
        "entidad": "Aguas del Río (empresa ficticia)",
        "instruccion": INS_REDACTAR,
        "entrada": (
            "Ficha de respuesta autorizada: la suspensión del barrio La Orilla está en revisión; "
            "pedir el número del contrato; no confirmar carro tanque; no echarle la culpa al usuario."
        ),
    },
    {
        "id": "T14",
        "tipo": "redactar_respuesta",
        "entidad": "Puesto de salud El Carmen (ficticio)",
        "instruccion": INS_REDACTAR,
        "entrada": (
            "Ficha de respuesta autorizada: hay jornada de vacunación los martes de 8 a 11, sin cita; "
            "pedir que lleve el documento de identidad; no preguntar por diagnósticos; no inventar otras sedes."
        ),
    },
    {
        "id": "T15",
        "tipo": "redactar_respuesta",
        "entidad": "IED Los Manglares (institución ficticia)",
        "instruccion": INS_REDACTAR,
        "entrada": (
            "Ficha de respuesta autorizada: hay papel en secretaría, máximo dos resmas por docente esta semana; "
            "no hay video beam disponible; los marcadores están agotados y no se puede prometer la compra."
        ),
    },
    {
        "id": "T16",
        "tipo": "redactar_respuesta",
        "entidad": "Personería de Santa Marta (ficticia)",
        "instruccion": INS_REDACTAR,
        "entrada": (
            "Ficha de respuesta autorizada: el radicado SM-P-19 sigue en trámite y todavía no tiene respuesta; "
            "pedir un teléfono de contacto; no inventar la fecha en que responderán; no opinar sobre el alumbrado."
        ),
    },
    {
        "id": "T17",
        "tipo": "clasificar_solicitud",
        "entidad": "Alcaldía de Galapa (ficticia)",
        "instruccion": INS_CLASIFICAR,
        "entrada": "Buenas. Necesito el certificado de residencia para un subsidio. ¿Qué papeles llevo?",
        "etiqueta_esperada": "peticion",
    },
    {
        "id": "T18",
        "tipo": "clasificar_solicitud",
        "entidad": "Aguas del Río (empresa ficticia)",
        "instruccion": INS_CLASIFICAR,
        "entrada": "Llevo seis días sin agua y nadie contesta el teléfono de la empresa. Esto es un irrespeto.",
        "etiqueta_esperada": "queja",
    },
    {
        "id": "T19",
        "tipo": "clasificar_solicitud",
        "entidad": "Aguas del Río (empresa ficticia)",
        "instruccion": INS_CLASIFICAR,
        "entrada": (
            "Me cobraron 120.000 pesos de un cargo que no reconozco. Exijo la reliquidación "
            "del recibo y la devolución de lo que pagué de más."
        ),
        "etiqueta_esperada": "reclamo",
    },
    {
        "id": "T20",
        "tipo": "clasificar_solicitud",
        "entidad": "IED Los Manglares (institución ficticia)",
        "instruccion": INS_CLASIFICAR,
        "entrada": "Sería bueno avisar la reunión de padres también por el grupo de WhatsApp, no solo en la cartelera.",
        "etiqueta_esperada": "sugerencia",
    },
    {
        "id": "T21",
        "tipo": "clasificar_solicitud",
        "entidad": "Puesto de salud El Carmen (ficticio)",
        "instruccion": INS_CLASIFICAR,
        "entrada": "Quiero agradecer a la enfermera de la jornada del martes. Atendió a mi papá con mucha paciencia.",
        "etiqueta_esperada": "felicitacion",
    },
    {
        "id": "T22",
        "tipo": "clasificar_solicitud",
        "entidad": "Secretaría de Educación de Bolívar (ficticia)",
        "instruccion": INS_CLASIFICAR,
        "entrada": "¿Hasta qué hora atienden hoy en la oficina de cobertura?",
        "etiqueta_esperada": "informacion",
    },
    {
        "id": "T23",
        "tipo": "clasificar_solicitud",
        "entidad": "Alcaldía de Mahates (ficticia)",
        "instruccion": INS_CLASIFICAR,
        "entrada": "Solicito copia del recibo de pago del impuesto predial del año pasado, a mi nombre.",
        "etiqueta_esperada": "peticion",
    },
    {
        "id": "T24",
        "tipo": "clasificar_solicitud",
        "entidad": "Inspección de Policía de Soledad (ficticia)",
        "instruccion": INS_CLASIFICAR,
        "entrada": "El ruido del establecimiento de la esquina sigue después de las diez de la noche. Ya no se puede dormir.",
        "etiqueta_esperada": "queja",
    },
    {
        "id": "T25",
        "tipo": "extraer_datos",
        "entidad": "Alcaldía de Galapa (ficticia)",
        "instruccion": INS_EXTRAER + " Claves: radicado, nombre, barrio, documento, telefono.",
        "entrada": (
            "Radicado GA-1042. Solicitante: María del Carmen Gómez. Documento de ejemplo terminado en 0001. "
            "Barrio El Campito. Celular de ejemplo 3000000001."
        ),
        "campos_esperados": {
            "radicado": "GA-1042",
            "nombre": "María del Carmen Gómez",
            "barrio": "El Campito",
            "documento": "0001",
            "telefono": "3000000001",
        },
    },
    {
        "id": "T26",
        "tipo": "extraer_datos",
        "entidad": "Secretaría de Educación de Bolívar (ficticia)",
        "instruccion": INS_EXTRAER + " Claves: radicado, acudiente, estudiante, edad, grado, institucion.",
        "entrada": (
            "Radicado BOL-ED-77. Acudiente Rosa Mercado. Estudiante Tomás Mercado, 7 años. "
            "Pide grado segundo en la IED Los Manglares."
        ),
        "campos_esperados": {
            "radicado": "BOL-ED-77",
            "acudiente": "Rosa Mercado",
            "estudiante": "Tomás Mercado",
            "edad": "7",
            "grado": "segundo",
            "institucion": "IED Los Manglares",
        },
    },
    {
        "id": "T27",
        "tipo": "extraer_datos",
        "entidad": "Aguas del Río (empresa ficticia)",
        "instruccion": INS_EXTRAER + " Claves: nombre, barrio, dias_sin_servicio, valor_recibo, numero_contrato.",
        "entrada": (
            "Doña Eulalia Jiménez, barrio La Orilla, lleva seis días sin agua. "
            "El recibo de agosto fue de 48.000 pesos. No informa el número del contrato."
        ),
        "campos_esperados": {
            "nombre": "Eulalia Jiménez",
            "barrio": "La Orilla",
            "dias_sin_servicio": "6",
            "valor_recibo": "48000",
            "numero_contrato": None,
        },
    },
    {
        "id": "T28",
        "tipo": "extraer_datos",
        "entidad": "Puesto de salud El Carmen (ficticio)",
        "instruccion": INS_EXTRAER + " Claves: nombre, edad, dia_disponible, documento.",
        "entrada": "Don Héctor Viloria, de 71 años, puede ir los martes en la mañana. No dictó el documento.",
        "campos_esperados": {
            "nombre": "Héctor Viloria",
            "edad": "71",
            "dia_disponible": "martes",
            "documento": None,
        },
    },
    {
        "id": "T29",
        "tipo": "extraer_datos",
        "entidad": "IED Los Manglares (institución ficticia)",
        "instruccion": INS_EXTRAER + " Claves: docente, curso, estudiantes, pedido.",
        "entrada": "La docente Ana Ferrer, del grado noveno, con 36 estudiantes, pide marcadores, resmas y un video beam.",
        "campos_esperados": {
            "docente": "Ana Ferrer",
            "curso": "noveno",
            "estudiantes": "36",
            "pedido": "marcadores, resmas y un video beam",
        },
    },
    {
        "id": "T30",
        "tipo": "extraer_datos",
        "entidad": "Personería de Santa Marta (ficticia)",
        "instruccion": INS_EXTRAER + " Claves: nombre, radicado_anterior, tema, correo.",
        "entrada": (
            "Pablo Gómez pregunta por el radicado SM-P-19, sobre el alumbrado de la calle 15. "
            "Correo pablo.ejemplo@correo.test."
        ),
        "campos_esperados": {
            "nombre": "Pablo Gómez",
            "radicado_anterior": "SM-P-19",
            "tema": "alumbrado de la calle 15",
            "correo": "pablo.ejemplo@correo.test",
        },
    },
    {
        "id": "T31",
        "tipo": "extraer_datos",
        "entidad": "Alcaldía de Mahates (ficticia)",
        "instruccion": INS_EXTRAER + " Claves: firmante, cargo, obra_pedida, numero_de_familias.",
        "entrada": (
            "Firma Nidia Cassiani, presidenta de la junta ficticia. Pide el arreglo del puente de madera "
            "del transporte escolar. No dice cuántas familias lo usan."
        ),
        "campos_esperados": {
            "firmante": "Nidia Cassiani",
            "cargo": "presidenta",
            "obra_pedida": "arreglo del puente de madera",
            "numero_de_familias": None,
        },
    },
    {
        "id": "T32",
        "tipo": "extraer_datos",
        "entidad": "Inspección de Policía de Soledad (ficticia)",
        "instruccion": INS_EXTRAER + " Claves: nombre, barrio, direccion, numero_de_casa.",
        "entrada": "Lázaro Peña reporta un hueco en la calle 30 con carrera 18, barrio La Paz. No da el número de la casa.",
        "campos_esperados": {
            "nombre": "Lázaro Peña",
            "barrio": "La Paz",
            "direccion": "calle 30 con carrera 18",
            "numero_de_casa": None,
        },
    },
    {
        "id": "T33",
        "tipo": "consulta_normativa",
        "entidad": "Texto de trabajo, no es el texto oficial de una ley",
        "instruccion": INS_NORMA,
        "entrada": (
            "Texto de trabajo: una petición completa de interés particular se responde en 15 días hábiles, "
            "contados desde el día siguiente a la radicación. Sábado y domingo no son hábiles. "
            "En este ejercicio no hay festivos. El 2 de noviembre de 2026 es lunes.\n\n"
            "Consulta: la petición GA-1042, completa, se radicó el lunes 2 de noviembre de 2026. "
            "¿Cuál es la fecha límite para responder?"
        ),
    },
    {
        "id": "T34",
        "tipo": "consulta_normativa",
        "entidad": "Texto de trabajo, no es el texto oficial de una ley",
        "instruccion": INS_NORMA,
        "entrada": (
            "Texto de trabajo: si la petición está incompleta, la entidad pide lo que falta dentro de "
            "los 10 días siguientes. El plazo de 15 días hábiles empieza a contarse el día hábil "
            "siguiente a aquel en que el ciudadano completa la petición. El 13 de noviembre de 2026 es viernes.\n\n"
            "Consulta: el ciudadano completó la petición el viernes 13 de noviembre de 2026. "
            "¿Qué día empieza a contarse el plazo de 15 días hábiles?"
        ),
    },
    {
        "id": "T35",
        "tipo": "consulta_normativa",
        "entidad": "Texto de trabajo, no es el texto oficial de una ley",
        "instruccion": INS_NORMA,
        "entrada": (
            "Texto de trabajo: los datos personales de estudiantes menores de edad no se envían a "
            "proveedores externos ni se publican. Una consulta sobre cupos se responde con cifras "
            "agregadas, sin nombres ni documentos.\n\n"
            "Consulta: un proveedor pide la lista de nombres y documentos de los niños sin cupo "
            "para 'mejorar el modelo'. ¿Se puede enviar?"
        ),
    },
    {
        "id": "T36",
        "tipo": "consulta_normativa",
        "entidad": "Texto de trabajo, no es el texto oficial de una ley",
        "instruccion": INS_NORMA,
        "entrada": (
            "Texto de trabajo: la petición verbal es válida. Quien atiende la escribe, la lee en voz "
            "alta y le entrega el número de radicado a la persona. No se exige que la persona sepa escribir.\n\n"
            "Consulta: una mujer llega a la ventanilla y quiere pedir el certificado de palabra, "
            "porque no trajo la carta. ¿La entidad debe recibirla?"
        ),
    },
    {
        "id": "T37",
        "tipo": "consulta_normativa",
        "entidad": "Texto de trabajo, no es el texto oficial de una ley",
        "instruccion": INS_NORMA,
        "entrada": (
            "Texto de trabajo: en este ejercicio el certificado de residencia no tiene costo. "
            "Cualquier cobro se devuelve y se deja constancia.\n\n"
            "Consulta: en la ventanilla le pidieron 20.000 pesos por el certificado. ¿Qué debe hacer la entidad?"
        ),
    },
    {
        "id": "T38",
        "tipo": "consulta_normativa",
        "entidad": "Texto de trabajo, no es el texto oficial de una ley",
        "instruccion": INS_NORMA,
        "entrada": (
            "Texto de trabajo: una solicitud de información se responde en 10 días hábiles. "
            "Una petición que pide una actuación de la entidad se responde en 15 días hábiles. "
            "Si el escrito solo pregunta un horario, es solicitud de información.\n\n"
            "Consulta: el escrito dice únicamente '¿Hasta qué hora atienden hoy en hacienda?'. "
            "¿Qué plazo aplica?"
        ),
    },
    {
        "id": "T39",
        "tipo": "consulta_normativa",
        "entidad": "Texto de trabajo, no es el texto oficial de una ley",
        "instruccion": INS_NORMA,
        "entrada": (
            "Texto de trabajo: si una circular interna da un plazo más largo que el del texto de trabajo, "
            "se aplica el plazo más corto. La circular de ventanilla dice 30 días. El texto de trabajo "
            "dice 15 días hábiles para esta petición.\n\n"
            "Consulta: ¿qué plazo debe usar el funcionario?"
        ),
    },
    {
        "id": "T40",
        "tipo": "consulta_normativa",
        "entidad": "Texto de trabajo, no es el texto oficial de una ley",
        "instruccion": INS_NORMA,
        "entrada": (
            "Texto de trabajo: la entidad no promete una obra, un cupo ni un reembolso si la ficha "
            "de respuesta no lo autoriza. Puede acusar recibo, pedir un dato faltante y explicar el estado.\n\n"
            "Consulta: la ficha solo autoriza acusar recibo y pedir el número de la casa. "
            "El ciudadano pregunta '¿me arreglan el hueco esta semana?'. ¿Qué puede contestar la entidad?"
        ),
    },
]


def por_id() -> dict[str, dict]:
    return {tarea["id"]: tarea for tarea in TAREAS}
