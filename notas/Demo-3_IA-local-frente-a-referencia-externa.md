# Nota técnica · IA local frente a una referencia externa

Evidencia TRL 3 · Nodo IA Caribe.

| Campo | Contenido |
| --- | --- |
| Fecha de la corrida (40+40) | 2026-11-09T23:49:03 |
| Fecha de calificación ciega | 2026-11-11T05:46:24.622Z |
| Responsable | Anuar Harb |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |

## 1. Resumen

Se compararon 40 tareas con modelo local qwen2.5:3b frente a anthropic claude-haiku-4-5. Paquete ciego generado (40 tareas, identificador 6fef1ff49dccfcae…). Tras calificación: calidad media local 4.6188 vs referencia 4.7938; Kappa Cohen 0.456.

## 2. Comparación de sistemas

- Tareas del protocolo: **40**
- Respuestas modelo local (qwen2.5:3b): **40/40**
- Respuestas referencia (anthropic · claude-haiku-4-5): **40/40**

### Tiempos de respuesta (segundos, medidos)

| Camino | Primera tarea | Promedio en caliente | Promedio todas | Máximo en caliente |
| --- | --- | --- | --- | --- |
| Local | 4.35 | 0.767 | 0.857 | 1.234 |
| Referencia | — | 1.405 | 1.42 | 2.936 |

**Costo local:** 0 USD por consulta (inferencia en el nodo). No incluye energía ni amortización del equipo. El costo de la referencia comercial no se consolida aquí sin tarifa confirmada del día.

## 3. Paquete ciego

- **Generado:** sí (40 tareas).
- **Identificador (hash):** `6fef1ff49dccfcae50137c8aeeaac3c03cc3a2eb5b4bc5c9979abae433eb6414`
- **Archivo para calificadores:** `resultados/demo3/ciego.json` (sin identificar qué respuesta es local o comercial).
- **Clave de desblindaje (no entregar a calificadores):** `resultados/demo3/clave.json`
- Las respuestas están marcadas como A y B. No se indica qué sistema escribió cada una.

Calificación: [http://127.0.0.1:8765/calificar](http://127.0.0.1:8765/calificar) o interfaz Demo 3 → *Calificar paquete ciego*.

## 4. Estado del protocolo

| Paso | Medido | Cumple |
| --- | --- | --- |
| 40 tareas con respuesta local (Ollama) | 40/40 | Sí |
| 40 tareas con respuesta de referencia comercial | 40/40 | Sí |
| Paquete ciego (A/B sin identificar sistema) | 40 tareas · hash 6fef1ff49dcc… | Sí |
| Dos calificaciones humanas a ciegas | 2/2 · Anuar Harb, Grace Torres | Sí |
| Métricas de comparación (Kappa Cohen, % comparables) | 85.0 % comparables · Kappa Cohen 0.456 | Sí |

## 5. Calificación humana y métricas

Calificación cerrada (Anuar Harb, Grace Torres). Calidad promedio local 4.6188 vs referencia 4.7938 (escala 1–5). 85.0 % comparables · Kappa Cohen promedio entre evaluadores: 0.456.

- Evaluadores: **Anuar Harb, Grace Torres**
- Calidad promedio **local:** 4.6188
- Calidad promedio **referencia:** 4.7938
- Tareas comparables: 85.0 %
- κ Cohen promedio (acuerdo entre evaluadores): **0.456**

- *Limitación:* Evaluaron el director del proyecto (Anuar Harb) y la representante legal de FCA (Grace Torres). Aceptable en este laboratorio TRL 3; para mayor independencia, conviene un tercer evaluador ajeno a la fundación.

## 6. Definiciones

- **Calidad de una respuesta:** promedio de exactitud, completitud, tono y utilidad (1–5).
- **Calidad de un camino:** promedio de las dos calificaciones humanas por tarea.
- **Tarea comparable:** diferencia absoluta ≤ 1 punto entre caminos.
- **Kappa de Cohen:** acuerdo entre calificadores (sin ponderar); kappa cuadrático aparte.

## 7. Limitaciones

Evaluaron el director del proyecto (Anuar Harb) y la representante legal de FCA (Grace Torres). Aceptable en este laboratorio TRL 3; para mayor independencia, conviene un tercer evaluador ajeno a la fundación.

Tareas y radicados ficticios. Modelo local pequeño (nodo borde). No se exige que gane lo local; se valida el método. Las entradas incluyen el texto de trabajo: se mide aplicación de la instrucción, no memoria legal.
