# Demo 1. Voz en español costeño

Nodo IA Caribe · Convocatoria 54

**Criterio cumplido.** El flujo completo (escuchar, responder y hablar) funcionó en 40 de 40 frases y en 19 de ellas quedó registrado un error real de reconocimiento.

| Campo | Contenido |
| --- | --- |
| Pregunta que responde | **¿Un equipo común puede escuchar, entender y responder sin servicios externos?** |
| Respuesta medida | Sí, con fallas: el flujo se completó en 40 de 40 frases, en 5.53 s en promedio. 19 de 40 quedaron con error de transcripción (WER 7.05 %) y el modelo inventó datos en 7 respuestas. |
| Qué sostiene en el proyecto | Objetivo específico 4. |
| Fecha de la prueba | del 11 de noviembre de 2026, 00:58 al 12 de noviembre de 2026, 19:45 |
| Responsable | Anuar Harb |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |
| Video | <https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing> |
| Código y datos | <https://github.com/AnuarHarb/node-ia-caribe> |

## 1. Objetivo

Mostrar que el reconocimiento y la síntesis de voz ya funcionan con habla costeña, y dónde fallan hoy. Justifica el objetivo específico 4 del proyecto.

**Criterio de éxito:**flujo de punta a punta y al menos un error real de reconocimiento registrado.

## 2. Montaje

| Componente | Detalle |
| --- | --- |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |
| Reconocimiento de voz | Whisper small (MLX, mlx-community/whisper-small-mlx), sin ajustar, con el idioma fijado en español. |
| Modelo de lenguaje | qwen2.5:3b servido con Ollama en el mismo equipo. Temperatura 0.2 y respuestas de hasta 120 tokens. |
| Síntesis de voz | Piper es_MX-ald-medium.onnx (español México, voz masculina medium). |
| Interfaz | Página web local (python -m interfaz); el audio entra por el micrófono del navegador. |
| Hablantes | 4 personas del equipo: Camila Rentería, Diego Molina, Jairo Barrios, Marelvis Pérez. |
| Consentimiento | El protocolo exige consentimiento escrito de cada hablante. La Fundación lo conserva y no se publica. |
| Internet | Los tres modelos corren en el equipo y ninguno llama a un servicio externo. La prueba con la red cortada y medida es el demo 2. |

## 3. Procedimiento

1. Cada hablante dice, con su habla natural, frases cotidianas de trámite tomadas de un guion de 10.
2. Whisper transcribe el audio, el modelo local redacta una respuesta corta y Piper la dice en voz alta. El servidor cronometra cada etapa.
3. Una persona escucha la grabación y escribe la transcripción correcta: lo que de verdad se dijo, que puede no ser igual al guion.
4. La transcripción del sistema se compara con la correcta después de pasar las dos a minúsculas y quitar la puntuación. Si son iguales, la frase es correcta.
5. Con la misma normalización se calcula el WER con la biblioteca jiwer: palabras cambiadas, omitidas o agregadas, divididas por las palabras dichas.
6. Cada turno queda guardado con su audio, sus tiempos y las dos transcripciones.

## 4. Resultados

Se midieron 40 frases de 4 hablantes. El flujo de punta a punta se completó en 40 de 40: el sistema escuchó, respondió y habló. **Transcribió sin error 21 y se equivocó en 19.**

**Tabla 1. Lo que se dijo y lo que escribió el sistema**

| # | Transcripción correcta (lo que se dijo) | Transcripción del sistema | ¿Correcta? | WER |
| --- | --- | --- | --- | --- |
| 1 | Buenas, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer? | Bueno, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer? | No | 7.7 % |
| 2 | ¿A qué horas atienden hoy en la secretaría de hacienda? | ¿A qué hora atiende Noi en la Secretaría de Hacienda? | No | 30.0 % |
| 3 | Necesito un turno para el Sisbén. ¿Me lo pueden dar ahora? | Necesito un turno para el 6. Me lo pueden dar ahora. | No | 9.1 % |
| 4 | ¿Dónde queda la oficina del predial? Es que me perdí. | ¿Dónde queda la oficina de el pre dial? Es que me perdí. | No | 40.0 % |
| 5 | Quiero saber si ya salió la respuesta de mi derecho de petición del mes pasado. | Quiero saber si ya salió la respuesta de mi derecho de petición del mes pasado. | Sí | 0.0 % |
| 6 | ¿Hasta qué hora están recibiendo el pago del impuesto hoy? | ¿Hasta qué hora están recibiendo el pago del impuesto hoy? | Sí | 0.0 % |
| 7 | Se me dañó el recibo del agua. ¿Cómo pido uno nuevo? | Se me dañó el recibo del agua, como pido uno nuevo. | No | 9.1 % |
| 8 | ¿El médico de la cita de las tres todavía está atendiendo? | ¿El médico de la cita de las tres todavía está atendiendo? | Sí | 0.0 % |
| 9 | Buenas tardes, ¿me regala el horario del colegio para la reunión de padres? | Buenas tardes, ¿me regala el horario del colegio para la reunión de padres? | Sí | 0.0 % |
| 10 | En mi calle no hay luz desde anoche. ¿A quién le toca eso? | En mi calle no hay luz desde anoche. ¿A quién le toca ese? | No | 7.7 % |
| 11 | Buenas, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer? | Buenas, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer? | Sí | 0.0 % |
| 12 | ¿A qué horas atienden hoy en la secretaría de hacienda? | ¿A qué horas atienden hoy en la secretaría de hacienda? | Sí | 0.0 % |

La tabla muestra las primeras 12 frases; hay 28 más en los datos.

**Error de palabras (WER) del conjunto: 7.05 %.**Son 33 palabras con error sobre 468 dichas: 28 cambiadas, 0 omitidas y 5 agregadas. Una frase cuenta como correcta solo si coincide entera con la transcripción correcta, después de pasar todo a minúsculas y quitar la puntuación.

**Tabla 2. Dónde falla el reconocimiento, palabra por palabra**

| # | Qué hizo | Lo que se dijo | Lo que escribió el sistema |
| --- | --- | --- | --- |
| 1 | Cambió | buenas | bueno |
| 2 | Cambió | horas atienden hoy | hora atiende noi |
| 3 | Cambió | sisbén | 6 |
| 4 | Agregó | (nada) | de el |
| 4 | Cambió | del predial | pre dial |
| 7 | Cambió | cómo | como |
| 10 | Cambió | eso | ese |
| 14 | Agregó | (nada) | de el |
| 14 | Cambió | del predial | pre dial |
| 21 | Cambió | un certificado | una certificada |
| 22 | Cambió | horas atienden hoy | hora atiende noi |
| 23 | Cambió | sisbén | sistema |
| 25 | Cambió | derecho | derecha |
| 27 | Cambió | cómo | como |

Hay 9 errores más en los datos.

**WER por hablante**

| Hablante | Frases | WER |
| --- | --- | --- |
| Camila Rentería | 10 | 9.40 % |
| Diego Molina | 10 | 3.42 % |
| Jairo Barrios | 10 | 7.69 % |
| Marelvis Pérez | 10 | 7.69 % |

**Tabla 3. Cuánto tarda cada etapa del flujo (40 frases)**

| Etapa | Promedio (s) | Mínimo (s) | Máximo (s) |
| --- | --- | --- | --- |
| Escuchar y transcribir (Whisper) | 2.10 | 1.71 | 2.39 |
| Responder (modelo local) | 2.51 | 2.13 | 2.93 |
| Hablar (Piper) | 0.37 | 0.30 | 0.42 |
| **Total de la frase** | **5.53** | **4.83** | **6.24** |

La primera frase tardó 5.66 s porque los modelos se cargan en memoria en la primera consulta. Sin ella, el promedio es de 5.53 s y el máximo registrado fue de 6.24 s. El total es algo mayor que la suma de las tres etapas porque incluye guardar el audio y convertirlo al formato que lee Whisper.

### Lo que respondió el asistente

En 7 respuestas el modelo local dio un dato que nadie le había dado. Se anota porque es un fallo real del sistema, distinto del error de reconocimiento:

- El asistente pidió «cédula de residencia»; el ciudadano hablaba de un certificado de residencia. Requisito inventado. (3 veces)
- Inventó que la oficina del predial «está en la avenida principal» sin dato en la petición. (4 veces)

## 5. Limitaciones

- **Habla leída.**Son frases de un guion dichas frente al computador, no conversación espontánea ni ruido de una oficina. En esas condiciones el error puede ser mayor.
- **Una sola persona fijó la transcripción correcta.**El WER depende de esa referencia; no hubo segunda revisión.
- **La voz que responde no es costeña.**Piper no tiene una voz del Caribe colombiano; se usó una voz de español de México. La síntesis funciona, pero no suena local.
- **El asistente no consulta fuentes oficiales.**Por eso inventó requisitos y ubicaciones. Para atender trámites reales tiene que conectarse a la información oficial de cada entidad.
- **Un solo equipo y un solo modelo.**Los tiempos son de este portátil y de Whisper small; con otro equipo u otro tamaño de modelo cambian.
- Las 30 frases en palenquero grabadas en esta misma pantalla no entran en estas cifras; se miden en el demo 4.

## 6. Enlaces

- **Video:**<https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing>
- **Repositorio:**<https://github.com/AnuarHarb/node-ia-caribe>
- **Código:**`voz/`, `interfaz/demo1_informe.py`.
- **Datos medidos:**`resultados/demo1/filas.json`, `resultados/demo1/turnos.jsonl`, `resultados/demo1/informe.json`.
- **Audios:**las grabaciones no se publican porque la voz identifica a la persona. Quedan en el equipo, junto con los consentimientos.
