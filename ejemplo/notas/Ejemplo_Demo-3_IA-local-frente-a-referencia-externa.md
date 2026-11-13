# Demo 3. IA local frente a referencia externa

Nodo IA Caribe · Convocatoria 54

**Criterio cumplido.** El método funcionó de principio a fin: 40 tareas por los dos caminos, paquete a ciegas, dos calificaciones humanas y métricas calculadas. El modelo local quedó por debajo de la referencia (4.62 frente a 4.79 sobre 5; el 96 % de la calidad de la referencia) y perdió en 18 tareas: la medición no lo favorece. El 85 % de las tareas quedó con calidad comparable y el acuerdo entre las dos personas fue moderado (kappa de Cohen 0.456).

| Campo | Contenido |
| --- | --- |
| Pregunta que responde | **¿Un modelo abierto alcanza una calidad comparable a la de un servicio comercial?** |
| Respuesta medida | Sí, cerca: el modelo local obtuvo 4.62 sobre 5 frente a 4.79 de la referencia, el 96 % de su calidad. El 85 % de las 40 tareas quedó comparable. |
| Qué sostiene en el proyecto | Objetivo específico 1 y el método de evaluación. |
| Fecha de la prueba | Generación de respuestas: 9 de noviembre de 2026, 23:49. Calificación a ciegas: del 10 de noviembre de 2026, 15:36 al 11 de noviembre de 2026, 00:46. |
| Responsable | Equipo del laboratorio |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |
| Video | <https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing> |
| Código y datos | <https://github.com/AnuarHarb/node-ia-caribe> |

## 1. Objetivo

Mostrar que el método de evaluación comparativa del proyecto ya funciona a pequeña escala: las mismas tareas pasan por un modelo local y por un servicio comercial, dos personas califican a ciegas y las métricas se calculan de forma reproducible.

**Criterio de éxito:**que el método funcione. No se exige que gane el modelo local; si pierde en algunas tareas, eso muestra que la medición es honesta.

## 2. Montaje

| Componente | Detalle |
| --- | --- |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |
| Camino local | qwen2.5:3b, modelo abierto servido con Ollama en el equipo. Temperatura 0, semilla fija y hasta 500 tokens por respuesta. |
| Camino de referencia | claude-haiku-4-5 de Anthropic, por su API. Temperatura 0. La clave de acceso se escribe al correr y no se guarda en disco. |
| Tareas | 40 tareas con datos ficticios de trámites públicos: resumir una petición ciudadana (8); redactar una respuesta (8); clasificar una solicitud (8); extraer datos de un documento (8); responder una consulta normativa (8). Cada tarea trae el texto sobre el que hay que trabajar. |
| Calificadores | Anuar Harb, Grace Torres. Cada persona califica por separado, en una hoja web que solo muestra «respuesta A» y «respuesta B». |
| Escala | De 1 a 5 en cuatro dimensiones: exactitud, completitud, tono y utilidad. |

## 3. Procedimiento

1. Las 40 tareas se envían, con la misma instrucción, al modelo local y al servicio comercial. De cada respuesta se guarda el texto, el tiempo y, en la referencia, los tokens que reporta el proveedor.
2. Para cada tarea se sortea cuál respuesta aparece como A y cuál como B (semilla 20261110). El paquete que reciben los calificadores no dice qué sistema escribió cada una; la clave queda en un archivo aparte.
3. Dos personas califican por separado cada respuesta, sin ver la clave ni las notas de la otra.
4. Al cerrar las dos calificaciones se abre la clave. La calidad de una respuesta es el promedio de sus cuatro dimensiones; la de un camino en una tarea, el promedio de las dos personas.
5. Una tarea es «comparable» si la diferencia entre los dos caminos es de 1 punto o menos.
6. El acuerdo entre las dos personas se mide con el kappa de Cohen en cada dimensión.

## 4. Resultados

**Tabla 1. Lo que pide medir la especificación**

| Medida | Local (qwen2.5:3b) | Referencia (claude-haiku-4-5) |
| --- | --- | --- |
| **Calidad promedio (1 a 5)** | **4.62** | **4.79** |
| Tiempo promedio por tarea (s) | 0.77 | 1.41 |
| Tiempo máximo por tarea (s) | 1.23 | 2.94 |
| Tiempo de la primera tarea (s) | 4.35 | 2.02 |
| Costo por tarea (USD) | 0, sin contar energía ni equipo | Sin tarifa confirmada |

**Tareas comparables: 85 %** (34 de 40). **Kappa de Cohen promedio: 0.456**, acuerdo moderado entre las dos personas. El promedio y el máximo de tiempo excluyen la primera tarea, que incluye la carga del modelo. El uso de la referencia sí está medido: 8382 tokens de entrada y 3497 de salida en las 40 tareas (209.6 y 87.4 por tarea). Falta multiplicarlo por la tarifa vigente del proveedor; no se escribe un valor en dólares sin confirmarla.

**Tarea por tarea:**la referencia fue mejor en 18, hubo empate en 15 y el modelo local fue mejor en 7.

**Tabla 2. Calidad por tipo de tarea**

| Tipo de tarea | Tareas | Local | Referencia | Comparables | Gana local | Gana referencia |
| --- | --- | --- | --- | --- | --- | --- |
| Resumir una petición ciudadana | 8 | 4.66 | 4.98 | 7 de 8 | 0 | 7 |
| Redactar una respuesta | 8 | 4.14 | 5.00 | 6 de 8 | 0 | 8 |
| Clasificar una solicitud | 8 | 4.69 | 4.50 | 6 de 8 | 1 | 1 |
| Extraer datos de un documento | 8 | 5.00 | 5.00 | 8 de 8 | 0 | 0 |
| Responder una consulta normativa | 8 | 4.61 | 4.48 | 7 de 8 | 6 | 2 |

En 6 tareas la diferencia pasó de 1 punto: en T05, T13, T15, T17, T33 el modelo local quedó claramente por debajo y en T22 quedó por encima.

**Tabla 3. Tareas no comparables**

| Tarea | Tipo | Local | Referencia | Diferencia |
| --- | --- | --- | --- | --- |
| T05 | Resumir una petición ciudadana | 3.375 | 5.000 | 1.625 |
| T13 | Redactar una respuesta | 3.625 | 5.000 | 1.375 |
| T15 | Redactar una respuesta | 3.625 | 5.000 | 1.375 |
| T17 | Clasificar una solicitud | 2.500 | 5.000 | 2.500 |
| T22 | Clasificar una solicitud | 5.000 | 1.000 | 4.000 |
| T33 | Responder una consulta normativa | 2.625 | 3.750 | 1.125 |

**Tabla 4. Por dimensión, y cuánto coinciden las dos personas**

| Dimensión | Local | Referencia | Kappa de Cohen | Acuerdo | Kappa cuadrático | Misma nota | Notas en 5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Exactitud | 4.76 | 4.85 | 0.650 | considerable | 0.925 | 95.0 % | 92.5 % |
| Completitud | 4.86 | 4.89 | 0.307 | aceptable | 0.583 | 92.5 % | 94.4 % |
| Tono | 4.38 | 4.74 | 0.443 | moderado | 0.682 | 77.5 % | 76.2 % |
| Utilidad | 4.47 | 4.70 | 0.424 | moderado | 0.707 | 77.5 % | 76.9 % |

«Misma nota» es el porcentaje de respuestas en que las dos personas pusieron exactamente el mismo número. El kappa descuenta el acuerdo que se daría por azar: como la mayoría de las notas son 5, ese acuerdo por azar es alto y el kappa queda bajo aunque coincidan casi siempre. El kappa cuadrático pesa menos los desacuerdos de un solo punto.

## 5. Limitaciones

- **Tareas ficticias y con el texto a la vista.**Cada tarea incluye el documento sobre el que se trabaja, así que se mide si el modelo aplica bien la instrucción, no si conoce la norma de memoria.
- **Muestra pequeña.**Son 40 tareas, 8 por tipo. Las diferencias entre tipos de tarea son indicativas.
- **Calificadores cercanos al proyecto.**Evaluaron el director del proyecto (Anuar Harb) y la representante legal de FCA (Grace Torres). Aceptable en este laboratorio TRL 3; para mayor independencia, conviene un tercer evaluador ajeno a la fundación.
- **La escala se queda corta por arriba.**Con casi todas las notas en 5, la escala distingue poco entre respuestas buenas y el kappa pierde fuerza. En el proyecto conviene usar tareas más difíciles o una rúbrica más exigente.
- **Un solo modelo local, pequeño.**qwen2.5:3b es un modelo de tamaño reducido, elegido porque corre en un portátil. No representa a todos los modelos abiertos.
- **El costo local no es cero en la realidad.**No se paga por consulta, pero hay energía y equipo, que esta prueba no midió.
- **Tiempos de la referencia dependen de la red.**Incluyen el viaje por internet hasta el proveedor; los del modelo local no.

## 6. Enlaces

- **Video:**<https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing>
- **Repositorio:**<https://github.com/AnuarHarb/node-ia-caribe>
- **Código:**`demo3_comparacion/`, `interfaz/demo3_informe.py`.
- **Datos medidos:**`resultados/demo3/generaciones.json`, `resultados/demo3/ciego.json`, `resultados/demo3/clave.json`, `resultados/demo3/calificaciones/`, `resultados/demo3/metricas.json`.
- **Paquete a ciegas:**identificador `6fef1ff49dccfcae`. Sirve para comprobar que las dos personas calificaron el mismo paquete.
