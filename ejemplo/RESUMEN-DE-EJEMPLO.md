# : los cinco demos con la muestra completa

No es una medición. Muestra cómo se verían las notas técnicas y la tabla de viabilidad al completar el protocolo. Los demos 1, 2 y 4 combinan lo medido con datos sintéticos que siguen su tendencia; los demos 3 y 5 traen sus cifras medidas. Lo genera `python -m ejemplo.generar`.

Las cifras que valen para el documento técnico son las de `entregables/RESUMEN-PARA-DOCUMENTO-TECNICO.md`.

## Palenquero

Las frases en palenquero de la medición base se grabaron con autorización del consejo comunitario. Los audios y la voz identificable no se publican; en el repositorio solo están las cifras y los datos de referencia.

## Viabilidad: qué pregunta responde cada demo

| Demo | Pregunta | Respuesta | Qué sostiene |
| --- | --- | --- | --- |
| 1. Voz en español costeño | ¿Un equipo común puede escuchar, entender y responder sin servicios externos? | Sí, con fallas: el flujo se completó en 40 de 40 frases, en 5.53 s en promedio. 19 de 40 quedaron con error de transcripción (WER 7.05 %) y el modelo inventó datos en 7 respuestas. | Objetivo específico 4. |
| 2. IA completa sin internet | ¿El mismo equipo atiende a varias personas a la vez con el internet cortado? | Sí: 3 usuarios a la vez y respuesta de voz en 7.16 s en promedio. | La operación del nodo sin conexión. |
| 3. IA local frente a referencia externa | ¿Un modelo abierto alcanza una calidad comparable a la de un servicio comercial? | Sí, cerca: el modelo local obtuvo 4.62 sobre 5 frente a 4.79 de la referencia, el 96 % de su calidad. El 85 % de las 40 tareas quedó comparable. | Objetivo específico 1 y el método de evaluación. |
| 4. Línea base del error (WER) | ¿Los modelos de hoy entienden el palenquero? | No: al transcribir palenquero hablado, el error de palabras fue de 86.55 %, frente a 7.05 % en español costeño. Al traducir poemas al palenquero, el modelo local obtuvo chrF 24.64; no traducir da 24.85. | Objetivo específico 3. |
| 5. Agentes aislados por entidad | ¿Cada entidad puede tener un agente que no vea los datos de las otras? | Sí: pasaron 11 de 11 pruebas; acceso cruzado bloqueado: sí; auditoría íntegra: sí. | El arnés y los agentes. |

## Estado de cada nota en el ejemplo

- **Demo 1. Voz en español costeño** (cifras medidas; 3 páginas): Criterio cumplido. El flujo completo (escuchar, responder y hablar) funcionó en 40 de 40 frases y en 19 de ellas quedó registrado un error real de reconocimiento.
- **Demo 2. IA completa sin internet** (cifras medidas; 2 páginas): Criterio cumplido. 3 usuarios a la vez, respuesta de voz en 7.16 s en promedio y sin salida a internet durante toda la sesión.
- **Demo 3. IA local frente a referencia externa** (cifras medidas; 3 páginas): Criterio cumplido. El método funcionó de principio a fin: 40 tareas por los dos caminos, paquete a ciegas, dos calificaciones humanas y métricas calculadas. El modelo local quedó por debajo de la referencia (4.62 frente a 4.79 sobre 5; el 96 % de la calidad de la referencia) y perdió en 18 tareas: la medición no lo favorece. El 85 % de las tareas quedó con calidad comparable y el acuerdo entre las dos personas fue moderado (kappa de Cohen 0.456).
- **Demo 4. Línea base del error (WER)** (cifras medidas; 3 páginas): Criterio cumplido. Una cifra por variedad, con la muestra del protocolo: palenquero, WER 86.55 % con 30 frases; español costeño, WER 7.05 % con 40 frases. Por escrito, al traducir 12 estrofas de 8 poemas al palenquero, el modelo local obtuvo chrF 24.64; dejar el texto sin traducir ya da 24.85.
- **Demo 5. Agentes aislados por entidad** (cifras medidas; 2 páginas): Criterio cumplido. El intento de lectura cruzada quedó bloqueado, pasaron 11 de 11 pruebas y el registro de auditoría conserva su cadena íntegra.
