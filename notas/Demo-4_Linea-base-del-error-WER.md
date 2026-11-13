# Nota técnica · Demo 4. Línea base del error (WER)

Nodo IA Caribe · Convocatoria 54 · Evidencia del punto de partida (TRL 3)

**Evidencia parcial.** Hay una cifra por variedad (palenquero, WER 89.47 % con 10 frases; español costeño, WER 11.05 % con 15 frases), pero con menos frases que las 30 a 50 del protocolo en palenquero y español costeño. Por escrito, al traducir 12 estrofas de 8 poemas al palenquero, el modelo local obtuvo chrF 24.64; dejar el texto sin traducir ya da 24.85.

| Campo | Contenido |
| --- | --- |
| Pregunta que responde | **¿Los modelos de hoy entienden el palenquero?** |
| Respuesta medida | No: al transcribir palenquero hablado, el error de palabras fue de 89.47 %, frente a 11.05 % en español costeño. Al traducir poemas al palenquero, el modelo local obtuvo chrF 24.64; no traducir da 24.85. |
| Qué sostiene en el proyecto | Objetivo específico 3. |
| Fecha del cálculo | 13 de noviembre de 2026, 02:28 |
| Responsable | Anuar Harb |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |
| Video | Opcional en este demo. Sin enlace todavía. |
| Código y datos | <https://github.com/AnuarHarb/node-ia-caribe> |

## 1. Objetivo

Mostrar, con un número, cuánto fallan hoy los modelos con el palenquero, hablado y escrito. El español costeño se mide con el mismo método y sirve de comparación. Justifica el objetivo específico 3 del proyecto.

**Criterio de éxito:**una cifra clara de error por cada variedad.

## 2. Montaje

| Componente | Detalle |
| --- | --- |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |
| Modelo | Whisper (mlx-community/whisper-small-mlx, sin ajustar). Es el modelo tal como se descarga, sin entrenamiento adicional. |
| Idioma del reconocimiento | Fijado en español para las dos variedades. Whisper no incluye el palenquero entre sus idiomas, así que se mide con la misma configuración que usaría hoy una entidad. |
| Corpus de palenquero | 10 frases: 10 grabadas en la pantalla del demo 1. Deben ser grabaciones públicas o de una persona hablante designada por la Fundación Chano y Chalole, con consentimiento y aval. |
| Corpus de español costeño | 15 frases: 15 grabadas en la pantalla del demo 1. |
| Cálculo | Biblioteca jiwer, sobre el texto en minúsculas y sin puntuación. Se conservan las tildes. |
| Prueba por escrito | 12 estrofas de 8 poemas (83 versos en palenquero) del libro «Letras palenqueras, la profunda necesidad de nombrar», de Sebastián Salgado, Faustino Torres y Uriel Cassiani. Modelo local (qwen2.5:3b), versión 357c53fb659c en Ollama; referencia comercial sin correr. Métrica: chrF (sacrebleu 2.5.1, nrefs:1\|case:mixed\|eff:yes\|nc:6\|nw:0\|space:no\|version:2.5.1). |

## 3. Procedimiento

1. Se reúnen de 30 a 50 frases por variedad, cada una con su audio y su transcripción correcta.
2. Whisper, sin ajustar, transcribe cada audio.
3. Las dos transcripciones se pasan a minúsculas y se les quita la puntuación.
4. Se calcula el WER de cada variedad con jiwer, sobre todas sus frases juntas.
5. Si a una variedad le faltan frases, el informe lo dice y no calcula una cifra para ella.
6. Por escrito: cada modelo traduce cada estrofa en las dos direcciones, con temperatura 0. Se calcula el chrF frente a la traducción humana y se compara con el control de no traducir.

## 4. Resultados

**Tabla 1. Error de palabras por variedad**

| Variedad | Número de frases | Palabras dichas | Cambiadas | Omitidas | Agregadas | WER (%) |
| --- | --- | --- | --- | --- | --- | --- |
| Palenquero | 10 | 57 | 37 | 12 | 2 | **89.47** |
| Español costeño | 15 | 172 | 17 | 1 | 1 | **11.05** |

El WER es la suma de palabras cambiadas, omitidas y agregadas, dividida por las palabras que de verdad se dijeron. Se calcula sobre todo el conjunto de frases de la variedad, no como promedio de cada frase. Un WER de 20 % significa que, de cada cinco palabras, el sistema falla en una.

**Palenquero: las frases con más error**

| Transcripción correcta | Transcripción del sistema | WER |
| --- | --- | --- |
| Palenke tiela suto, asino kumo Afrika. | Palenque tiene el asunto, así no como África. | 133.3 % |
| Suto á bae pa Katagena. | Sútuaváe, pacatajéna. | 100.0 % |
| I advedtí mae mí nú komblá eso nú. | Las allied Pablo Else Привет Ads | 100.0 % |
| I tá saká un ma matika ñame. | 훈alalalal adjournos bargaining | 100.0 % |
| Ané a tre machete mí. | NHÍ seperti referencing precedent İyi | 100.0 % |

Palenquero: 0 de 10 frases quedaron sin ningún error.

**Español costeño: las frases con más error**

| Transcripción correcta | Transcripción del sistema | WER |
| --- | --- | --- |
| Buenas, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer? | Bueno, me voy a pedir una certificada de residencia. ¿Qué papeles tengo que traer? | 38.5 % |
| ¿Dónde queda la oficina del peredial? Es que me perdí. | ¿Dónde queda el oficinal peredial? Es que me perdí. | 30.0 % |
| ¿Hasta qué hora están recibiendo el pago del impuesto hoy? | hasta que ahora están recibiendo el pago del impuesto hoy | 20.0 % |
| ¿A qué horas atienden hoy en la secretaría de hacienda? | A qué horas atiende Nubi en la Secretaría de Hacienda? | 20.0 % |
| ¿A qué horas atienden hoy en la secretaría de hacienda? | ¿A qué hora atienden hoy en la Secretaría de Hacienda? | 10.0 % |

Español costeño: 4 de 15 frases quedaron sin ningún error.

El error en palenquero (89.47 %) es más alto que en español costeño (11.05 %). La especificación esperaba un error alto en palenquero y moderado en costeño.

### Por escrito: traducción entre español y palenquero

La misma pregunta, sin audio. Cada modelo tradujo 12 estrofas de 8 poemas del libro «Letras palenqueras, la profunda necesidad de nombrar», de Sebastián Salgado, Faustino Torres y Uriel Cassiani, que trae cada poema en las dos lenguas, y su salida se comparó con la traducción humana del libro.

**Tabla 2. Traducción de 12 estrofas de 8 poemas frente a la traducción humana**

| Dirección | Sistema | chrF (0 a 100) | Palabras acertadas | Palabras copiadas del origen |
| --- | --- | --- | --- | --- |
| español → palenquero | Sin traducir (control) | 24.85 | 5.10 % | — |
|  | **Modelo local (qwen2.5:3b)** | **24.64** | 6.05 % | 84.17 % |
|  | Referencia comercial | Sin correr | — | — |
| palenquero → español | Sin traducir (control) | 21.42 | 4.56 % | — |
|  | **Modelo local (qwen2.5:3b)** | **20.54** | 3.99 % | 97.76 % |
|  | Referencia comercial | Sin correr | — | — |

El modelo local no superó al control en ninguna dirección: devolver el texto sin tocar se parece igual o más a la traducción humana. El chrF mide cuánto se parecen las letras de la salida a las de la traducción humana. El control es no traducir: como el palenquero comparte vocabulario con el español, el texto sin tocar ya se parece algo. Un modelo que no supera esa cifra no está aportando la lengua.

**Ejemplo: dos versos del poema «Nosotros» (páginas 70-71)**

| Dirección | Texto de origen | Traducción humana | Modelo local |
| --- | --- | --- | --- |
| español → palenquero | En esta vida somos / Como aves que emigran | E bila suto sendá / Kumo kajomba | En ahi vida somos / Como aves ke emigran |
| palenquero → español | E bila suto sendá / Kumo kajomba | En esta vida somos / Como aves que emigran | E bila suto sendá / Kumo kajomba |

## 5. Limitaciones

- **Muestra corta en palenquero.**Son 10 frases; el protocolo pide de 30 a 50. Con tan pocas, unas cuantas palabras mueven el porcentaje varios puntos.
- **Muestra corta en español costeño.**Son 15 frases; el protocolo pide de 30 a 50. Con tan pocas, unas cuantas palabras mueven el porcentaje varios puntos.
- **Las frases de costeño son las del demo 1.**Comparten sus límites: pocas voces y frases leídas de un guion.
- **El palenquero no tiene una sola forma de escribirse.**El WER compara texto contra texto, así que depende de la ortografía que use quien fija la transcripción correcta. Esa convención la debe avalar la comunidad hablante.
- **El WER cuenta palabras, no gravedad.**Un cambio de género pesa lo mismo que confundir el nombre de un trámite.
- **Un solo modelo y un solo tamaño.**Se midió Whisper small; los modelos más grandes pueden dar cifras distintas.
- **Una sola persona fija cada transcripción correcta.**No hubo doble revisión de las referencias.
- **La traducción de los poemas es literaria.**Hay una sola traducción humana y es libre, así que una traducción correcta con otras palabras también puntúa bajo. Las cifras sirven para comparar contra el control, no como nota de calidad. Son 12 estrofas de 8 poemas de un solo libro.
- **Pendiente en la prueba por escrito:**revisar la transcripción contra el libro impreso (salió de fotos); pedir permiso a los autores para usar los poemas en el proyecto; correr la referencia comercial.

## 6. Enlaces

- **Video:**opcional en este demo; no se ha subido.
- **Repositorio:**<https://github.com/AnuarHarb/node-ia-caribe>
- **Código:**`demo4_wer/`, `medicion.py`.
- **Datos medidos:**`resultados/demo4/informe.json`, `resultados/demo4/traduccion.json`, `resultados/demo1/filas.json`, `demo4_wer/corpus/`.
- **Audios:**no se publican grabaciones con voz identificable. Los consentimientos y el aval se conservan, no se suben.
- **Poemas:**son obras con autor. El repositorio publica las cifras y dos versos de ejemplo, no los poemas.

---

Nota generada el 13 de noviembre de 2026, 02:30 (hora de Colombia) a partir de resultados/demo4/informe.json. Todas las cifras son medidas; ninguna se estima ni se completa a mano.
