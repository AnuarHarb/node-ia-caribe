# Nota técnica · Demo 1. Voz en español costeño

Nodo IA Caribe · Convocatoria 54 · Evidencia del punto de partida (TRL 3)

**Criterio cumplido.** El flujo completo (escuchar, responder y hablar) funcionó en 15 de 15 frases y en 9 de ellas quedó registrado un error real de reconocimiento. La muestra es menor que la del protocolo: 15 frases de 2 hablantes, frente a 3 o 4 hablantes con 10 frases cada uno.

| Campo | Contenido |
| --- | --- |
| Pregunta que responde | **¿Un equipo común puede escuchar, entender y responder sin servicios externos?** |
| Respuesta medida | Sí, con fallas: el flujo se completó en 15 de 15 frases, en 6.43 s en promedio. 9 de 15 quedaron con error de transcripción (WER 11.05 %) y el modelo inventó datos en 4 respuestas. |
| Qué sostiene en el proyecto | Objetivo específico 4. |
| Fecha de la prueba | del 11 de noviembre de 2026, 00:51 al 12 de noviembre de 2026, 23:05 |
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
| Hablantes | 2 personas del equipo: Anuar Harb, Grace Torres. |
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

Se midieron 15 frases de 2 hablantes. El flujo de punta a punta se completó en 15 de 15: el sistema escuchó, respondió y habló. **Transcribió sin error 6 y se equivocó en 9.**

**Tabla 1. Lo que se dijo y lo que escribió el sistema**

| # | Transcripción correcta (lo que se dijo) | Transcripción del sistema | ¿Correcta? | WER |
| --- | --- | --- | --- | --- |
| 1 | Buenas, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer? | Bueno, me voy a pedir una certificada de residencia. ¿Qué papeles tengo que traer? | No | 38.5 % |
| 2 | ¿A qué hora atienden hoy en la Secretaría de Hacienda? | ¿A qué hora atienden hoy en la Secretaría de Hacienda? | Sí | 0.0 % |
| 3 | Necesito un turno para el Sisbén. Me lo pueden dar ahora. | Necesito un turno para el 6. Me lo pueden dar ahora. | No | 9.1 % |
| 4 | ¿Dónde queda la oficina del peredial? Es que me perdí. | ¿Dónde queda el oficinal peredial? Es que me perdí. | No | 30.0 % |
| 5 | Quiero saber si ya salió la respuesta de mi derecho de petición del mes pasado. | Quiero saber si ya salió la respuesta de mi Derecha de Petición del mes pasado. | No | 6.7 % |
| 6 | ¿Hasta qué hora están recibiendo el pago del impuesto hoy? | hasta que ahora están recibiendo el pago del impuesto hoy | No | 20.0 % |
| 7 | Buenas, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer? | Buenas, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer? | Sí | 0.0 % |
| 8 | ¿A qué horas atienden hoy en la secretaría de hacienda? | ¿A qué hora atienden hoy en la Secretaría de Hacienda? | Sí | 10.0 % |
| 9 | Necesito un turno para el Sisbén. ¿Me lo pueden dar ahora? | Necesito un turno para el cisbeño, me lo pueden dar ahora. | No | 9.1 % |
| 10 | ¿Dónde queda la oficina del predial? Es que me perdí. | donde queda la oficina del predial es que me perdí | No | 10.0 % |
| 11 | Quiero saber si ya salió la respuesta de mi derecho de petición del mes pasado. | Quiero saber si ya salió la respuesta de mi derecho de petición del mes pasado. | Sí | 0.0 % |
| 12 | Buenas, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer? | Buenas, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer? | Sí | 0.0 % |

La tabla muestra las primeras 12 frases; hay 3 más en los datos.

**Error de palabras (WER) del conjunto: 11.05 %.**Son 19 palabras con error sobre 172 dichas: 17 cambiadas, 1 omitidas y 1 agregadas. Una frase cuenta como correcta solo si coincide entera con la transcripción correcta, después de pasar todo a minúsculas y quitar la puntuación.

**Tabla 2. Dónde falla el reconocimiento, palabra por palabra**

| # | Qué hizo | Lo que se dijo | Lo que escribió el sistema |
| --- | --- | --- | --- |
| 1 | Agregó | (nada) | bueno |
| 1 | Cambió | buenas vengo | me voy |
| 1 | Cambió | un certificado | una certificada |
| 3 | Cambió | sisbén | 6 |
| 4 | Cambió | la oficina | el oficinal |
| 4 | Omitió | del | (nada) |
| 5 | Cambió | derecho | derecha |
| 6 | Cambió | qué hora | que ahora |
| 8 | Cambió | horas | hora |
| 9 | Cambió | sisbén | cisbeño |
| 10 | Cambió | dónde | donde |
| 13 | Cambió | atienden hoy | atiende nubi |
| 14 | Cambió | sisbén | system |
| 15 | Cambió | dónde | donde |

**WER por hablante**

| Hablante | Frases | WER |
| --- | --- | --- |
| Anuar Harb | 6 | 17.39 % |
| Grace Torres | 9 | 6.80 % |

**Tabla 3. Cuánto tarda cada etapa del flujo (15 frases)**

| Etapa | Promedio (s) | Mínimo (s) | Máximo (s) |
| --- | --- | --- | --- |
| Escuchar y transcribir (Whisper) | 2.59 | 0.82 | 6.21 |
| Responder (modelo local) | 3.17 | 1.35 | 7.17 |
| Hablar (Piper) | 0.39 | 0.17 | 0.72 |
| **Total de la frase** | **6.43** | **2.68** | **12.59** |

La primera frase tardó 10.99 s porque los modelos se cargan en memoria en la primera consulta. Sin ella, el promedio es de 6.10 s y el máximo registrado fue de 12.59 s. El total es algo mayor que la suma de las tres etapas porque incluye guardar el audio y convertirlo al formato que lee Whisper.

### Lo que respondió el asistente

En 4 respuestas el modelo local dio un dato que nadie le había dado. Se anota porque es un fallo real del sistema, distinto del error de reconocimiento:

- El asistente pidió «cédula de residencia»; el ciudadano hablaba de un certificado de residencia. Requisito inventado.
- Inventó que la oficina del predial «está en la avenida principal» sin dato en la petición. (3 veces)

## 5. Limitaciones

- **Muestra pequeña.**Hay 15 frases de 2 hablantes; el protocolo pide 3 o 4 hablantes con 10 frases cada uno. El porcentaje de error es indicativo y puede cambiar con más voces.
- **Habla leída.**Son frases de un guion dichas frente al computador, no conversación espontánea ni ruido de una oficina. En esas condiciones el error puede ser mayor.
- **Una sola persona fijó la transcripción correcta.**El WER depende de esa referencia; no hubo segunda revisión.
- **La voz que responde no es costeña.**Piper no tiene una voz del Caribe colombiano; se usó una voz de español de México. La síntesis funciona, pero no suena local.
- **El asistente no consulta fuentes oficiales.**Por eso inventó requisitos y ubicaciones. Para atender trámites reales tiene que conectarse a la información oficial de cada entidad.
- **Un solo equipo y un solo modelo.**Los tiempos son de este portátil y de Whisper small; con otro equipo u otro tamaño de modelo cambian.
- Las 10 frases en palenquero grabadas en esta misma pantalla no entran en estas cifras; se miden en el demo 4.

## 6. Enlaces

- **Video:**<https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing>
- **Repositorio:**<https://github.com/AnuarHarb/node-ia-caribe>
- **Código:**`voz/`, `interfaz/demo1_informe.py`.
- **Datos medidos:**`resultados/demo1/filas.json`, `resultados/demo1/turnos.jsonl`, `resultados/demo1/informe.json`.
- **Audios:**las grabaciones no se publican porque la voz identifica a la persona. Quedan en el equipo, junto con los consentimientos.

---

Nota generada el 13 de noviembre de 2026, 03:06 (hora de Colombia) a partir de resultados/demo1/informe.json. Todas las cifras son medidas; ninguna se estima ni se completa a mano.
