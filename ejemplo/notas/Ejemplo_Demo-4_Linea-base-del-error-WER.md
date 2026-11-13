# Demo 4. Línea base del error (WER)

Nodo IA Caribe · Convocatoria 54

**Criterio cumplido.** Una cifra por variedad, con la muestra del protocolo: palenquero, WER 86.55 % con 30 frases; español costeño, WER 7.05 % con 40 frases. Por escrito, al traducir 12 estrofas de 8 poemas al palenquero, el modelo local obtuvo chrF 24.64; dejar el texto sin traducir ya da 24.85.

| Campo | Contenido |
| --- | --- |
| Pregunta que responde | **¿Los modelos de hoy entienden el palenquero?** |
| Respuesta medida | No: al transcribir palenquero hablado, el error de palabras fue de 86.55 %, frente a 7.05 % en español costeño. Al traducir poemas al palenquero, el modelo local obtuvo chrF 24.64; no traducir da 24.85. |
| Qué sostiene en el proyecto | Objetivo específico 3. |
| Fecha del cálculo | 12 de noviembre de 2026, 23:41 |
| Responsable | Anuar Harb |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |
| Video | <https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing> |
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
| Corpus de palenquero | 30 frases: 30 grabadas en la pantalla del demo 1. Deben ser grabaciones públicas o de una persona hablante designada por la Fundación Chano y Chalole, con consentimiento y aval. |
| Corpus de español costeño | 40 frases: 40 grabadas en la pantalla del demo 1. |
| Cálculo | Biblioteca jiwer, sobre el texto en minúsculas y sin puntuación. Se conservan las tildes. |
| Prueba por escrito | 12 estrofas de 8 poemas (83 versos en palenquero) del libro «Letras palenqueras, la profunda necesidad de nombrar», de Sebastián Salgado, Faustino Torres y Uriel Cassiani. Modelo local (qwen2.5:3b), versión 357c53fb659c en Ollama; referencia comercial (claude-haiku-4-5). Métrica: chrF (sacrebleu 2.5.1, nrefs:1\|case:mixed\|eff:yes\|nc:6\|nw:0\|space:no\|version:2.5.1). |

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
| Palenquero | 30 | 171 | 121 | 11 | 16 | **86.55** |
| Español costeño | 40 | 468 | 28 | 0 | 5 | **7.05** |

El WER es la suma de palabras cambiadas, omitidas y agregadas, dividida por las palabras que de verdad se dijeron. Se calcula sobre todo el conjunto de frases de la variedad, no como promedio de cada frase. Un WER de 20 % significa que, de cada cinco palabras, el sistema falla en una.

**Palenquero: las frases con más error**

| Transcripción correcta | Transcripción del sistema | WER |
| --- | --- | --- |
| Palenke tiela suto, asino kumo Afrika. | Palenque tiene la su todo, así no cumo África. | 150.0 % |
| Palenke tiela suto, asino kumo Afrika. | Palenque tierra su todo, así no como África. | 133.3 % |
| Ané kume mbollo mí. | A ne cumembo yo mi. | 125.0 % |
| Suto á bae pa Katagena. | Su tuá va e para Cartagena. | 120.0 % |
| Palenke tiela suto, asino kumo Afrika. | Palenque, tiene la suto, a sino como África. | 116.7 % |

Palenquero: 0 de 30 frases quedaron sin ningún error.

**Español costeño: las frases con más error**

| Transcripción correcta | Transcripción del sistema | WER |
| --- | --- | --- |
| ¿Dónde queda la oficina del predial? Es que me perdí. | ¿Dónde queda la oficina de el pre dial? Es que me perdí. | 40.0 % |
| ¿Dónde queda la oficina del predial? Es que me perdí. | ¿Dónde queda la oficina de el pre dial? Es que me perdí. | 40.0 % |
| ¿A qué horas atienden hoy en la secretaría de hacienda? | ¿A qué hora atiende Noi en la Secretaría de Hacienda? | 30.0 % |
| ¿A qué horas atienden hoy en la secretaría de hacienda? | ¿A qué hora atiende Noi en la Secretaría de Hacienda? | 30.0 % |
| Se me dañó el recibo del agua. ¿Cómo pido uno nuevo? | Se me daño el recibo de la agua. ¿Cómo pido uno nuevo? | 27.3 % |

Español costeño: 21 de 40 frases quedaron sin ningún error.

El error en palenquero (86.55 %) es más alto que en español costeño (7.05 %). La especificación esperaba un error alto en palenquero y moderado en costeño.

### Por escrito: traducción entre español y palenquero

La misma pregunta, sin audio. Cada modelo tradujo 12 estrofas de 8 poemas del libro «Letras palenqueras, la profunda necesidad de nombrar», de Sebastián Salgado, Faustino Torres y Uriel Cassiani, que trae cada poema en las dos lenguas, y su salida se comparó con la traducción humana del libro.

**Tabla 2. Traducción de 12 estrofas de 8 poemas frente a la traducción humana**

| Dirección | Sistema | chrF (0 a 100) | Palabras acertadas | Palabras copiadas del origen |
| --- | --- | --- | --- | --- |
| español → palenquero | Sin traducir (control) | 24.85 | 5.10 % | — |
|  | **Modelo local (qwen2.5:3b)** | **24.64** | 6.05 % | 84.17 % |
|  | **Referencia comercial (claude-haiku-4-5)** | **29.37** | 13.69 % | 38.52 % |
| palenquero → español | Sin traducir (control) | 21.42 | 4.56 % | — |
|  | **Modelo local (qwen2.5:3b)** | **20.54** | 3.99 % | 97.76 % |
|  | **Referencia comercial (claude-haiku-4-5)** | **37.84** | 21.65 % | 12.31 % |

El modelo local no superó al control en ninguna dirección: devolver el texto sin tocar se parece igual o más a la traducción humana. La referencia comercial superó al control en las dos direcciones. El chrF mide cuánto se parecen las letras de la salida a las de la traducción humana. El control es no traducir: como el palenquero comparte vocabulario con el español, el texto sin tocar ya se parece algo. Un modelo que no supera esa cifra no está aportando la lengua.

**Ejemplo: dos versos del poema «Nosotros» (páginas 70-71)**

| Dirección | Texto de origen | Traducción humana | Modelo local | Referencia |
| --- | --- | --- | --- | --- |
| español → palenquero | En esta vida somos / Como aves que emigran | E bila suto sendá / Kumo kajomba | En ahi vida somos / Como aves ke emigran | E bila suto ta / Kumo pájaro ke ta bae |
| palenquero → español | E bila suto sendá / Kumo kajomba | En esta vida somos / Como aves que emigran | E bila suto sendá / Kumo kajomba | En la vida nosotros somos / Como palomas |

## 5. Limitaciones

- **Las frases de costeño son las del demo 1.**Comparten sus límites: pocas voces y frases leídas de un guion.
- **El palenquero no tiene una sola forma de escribirse.**El WER compara texto contra texto, así que depende de la ortografía que use quien fija la transcripción correcta. Esa convención la debe avalar la comunidad hablante.
- **El WER cuenta palabras, no gravedad.**Un cambio de género pesa lo mismo que confundir el nombre de un trámite.
- **Un solo modelo y un solo tamaño.**Se midió Whisper small; los modelos más grandes pueden dar cifras distintas.
- **Una sola persona fija cada transcripción correcta.**No hubo doble revisión de las referencias.
- **La traducción de los poemas es literaria.**Hay una sola traducción humana y es libre, así que una traducción correcta con otras palabras también puntúa bajo. Las cifras sirven para comparar contra el control, no como nota de calidad. Son 12 estrofas de 8 poemas de un solo libro.

## 6. Enlaces

- **Video:**<https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing>
- **Repositorio:**<https://github.com/AnuarHarb/node-ia-caribe>
- **Código:**`demo4_wer/`, `medicion.py`.
- **Datos medidos:**`resultados/demo4/informe.json`, `resultados/demo4/traduccion.json`, `resultados/demo1/filas.json`, `demo4_wer/corpus/`.
- **Audios:**no se publican grabaciones con voz identificable. Los consentimientos y el aval se conservan, no se suben.
- **Poemas:**son obras con autor. El repositorio publica las cifras y dos versos de ejemplo, no los poemas.
