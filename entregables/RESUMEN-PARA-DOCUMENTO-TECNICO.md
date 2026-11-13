# Resultados de los demos para el documento técnico

Texto para la sección de antecedentes y punto de partida del TRL. Lo genera `python -m interfaz.entregar` con las mismas cifras de las notas técnicas; no se edita a mano.

## Viabilidad: qué pregunta responde cada demo

Los demos sostienen el punto de partida en TRL 3: la idea funciona en laboratorio, se sabe dónde falla y cuánto falta. Cada respuesta es la misma que abre la nota técnica del demo.

| Demo | Pregunta | Respuesta medida | Qué sostiene |
| --- | --- | --- | --- |
| 1. Voz en español costeño | ¿Un equipo común puede escuchar, entender y responder sin servicios externos? | Sí, con fallas: el flujo se completó en 15 de 15 frases, en 6.43 s en promedio. 9 de 15 quedaron con error de transcripción (WER 11.05 %) y el modelo inventó datos en 4 respuestas. | Objetivo específico 4. |
| 2. IA completa sin internet | ¿El mismo equipo atiende a varias personas a la vez con el internet cortado? | Sin medir todavía. | La operación del nodo sin conexión. |
| 3. IA local frente a referencia externa | ¿Un modelo abierto alcanza una calidad comparable a la de un servicio comercial? | Sí, cerca: el modelo local obtuvo 4.62 sobre 5 frente a 4.79 de la referencia, el 96 % de su calidad. El 85 % de las 40 tareas quedó comparable. | Objetivo específico 1 y el método de evaluación. |
| 4. Línea base del error (WER) | ¿Los modelos de hoy entienden el palenquero? | No: al transcribir palenquero hablado, el error de palabras fue de 89.47 %, frente a 11.05 % en español costeño. Al traducir poemas al palenquero, el modelo local obtuvo chrF 24.64; no traducir da 24.85. | Objetivo específico 3. |
| 5. Agentes aislados por entidad | ¿Cada entidad puede tener un agente que no vea los datos de las otras? | Sí: pasaron 11 de 11 pruebas; acceso cruzado bloqueado: sí; auditoría íntegra: sí. | El arnés y los agentes. |

## Demo 1. Voz en español costeño

**Criterio cumplido.** El flujo completo (escuchar, responder y hablar) funcionó en 15 de 15 frases y en 9 de ellas quedó registrado un error real de reconocimiento. La muestra es menor que la del protocolo: 15 frases de 2 hablantes, frente a 3 o 4 hablantes con 10 frases cada uno.

- Nota técnica: `Nodo-IA-Caribe_Demo-1_Voz-en-espanol-costeno.pdf` (3 páginas)
- Video: https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing
- Código y datos: https://github.com/AnuarHarb/node-ia-caribe

## Demo 2. IA completa sin internet

**Sin medición.** Todavía no se ha hecho la medición por voz con los teléfonos y el router sin internet. Esta nota describe el montaje y el procedimiento; la tabla de resultados se llena sola al medir.

- Nota técnica: `Nodo-IA-Caribe_Demo-2_IA-completa-sin-internet.pdf` (2 páginas)
- Video: https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing
- Código y datos: https://github.com/AnuarHarb/node-ia-caribe

## Demo 3. IA local frente a referencia externa

**Criterio cumplido.** El método funcionó de principio a fin: 40 tareas por los dos caminos, paquete a ciegas, dos calificaciones humanas y métricas calculadas. El modelo local quedó por debajo de la referencia (4.62 frente a 4.79 sobre 5; el 96 % de la calidad de la referencia) y perdió en 18 tareas: la medición no lo favorece. El 85 % de las tareas quedó con calidad comparable y el acuerdo entre las dos personas fue moderado (kappa de Cohen 0.456).

- Nota técnica: `Nodo-IA-Caribe_Demo-3_IA-local-frente-a-referencia-externa.pdf` (3 páginas)
- Video: https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing
- Código y datos: https://github.com/AnuarHarb/node-ia-caribe

## Demo 4. Línea base del error (WER)

**Evidencia parcial.** Hay una cifra por variedad (palenquero, WER 89.47 % con 10 frases; español costeño, WER 11.05 % con 15 frases), pero con menos frases que las 30 a 50 del protocolo en palenquero y español costeño. Por escrito, al traducir 12 estrofas de 8 poemas al palenquero, el modelo local obtuvo chrF 24.64; dejar el texto sin traducir ya da 24.85.

- Nota técnica: `Nodo-IA-Caribe_Demo-4_Linea-base-del-error-WER.pdf` (3 páginas)
- Video: https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing
- Código y datos: https://github.com/AnuarHarb/node-ia-caribe

## Demo 5. Agentes aislados por entidad

**Criterio cumplido.** El intento de lectura cruzada quedó bloqueado, pasaron 11 de 11 pruebas y el registro de auditoría conserva su cadena íntegra.

- Nota técnica: `Nodo-IA-Caribe_Demo-5_Agentes-aislados-por-entidad.pdf` (2 páginas)
- Video: https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing
- Código y datos: https://github.com/AnuarHarb/node-ia-caribe

## Falta antes de radicar

- Demo 2: sin medición. Todavía no se ha hecho la medición por voz con los teléfonos y el router sin internet. Esta nota describe el montaje y el procedimiento; la tabla de resultados se llena sola al medir.
- Demo 4: evidencia parcial. Hay una cifra por variedad (palenquero, WER 89.47 % con 10 frases; español costeño, WER 11.05 % con 15 frases), pero con menos frases que las 30 a 50 del protocolo en palenquero y español costeño. Por escrito, al traducir 12 estrofas de 8 poemas al palenquero, el modelo local obtuvo chrF 24.64; dejar el texto sin traducir ya da 24.85.
