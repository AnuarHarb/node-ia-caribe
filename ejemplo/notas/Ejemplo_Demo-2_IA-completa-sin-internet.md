# Demo 2. IA completa sin internet

Nodo IA Caribe · Convocatoria 54

**Criterio cumplido.** 3 usuarios a la vez, respuesta de voz en 7.16 s en promedio y sin salida a internet durante toda la sesión.

| Campo | Contenido |
| --- | --- |
| Pregunta que responde | **¿El mismo equipo atiende a varias personas a la vez con el internet cortado?** |
| Respuesta medida | Sí: 3 usuarios a la vez y respuesta de voz en 7.16 s en promedio. |
| Qué sostiene en el proyecto | La operación del nodo sin conexión. |
| Fecha de la prueba | 12 de noviembre de 2026, de 20:14 a 20:17 |
| Responsable | Anuar Harb |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |
| Video | <https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing> |
| Código y datos | <https://github.com/AnuarHarb/node-ia-caribe> |

## 1. Objetivo

Mostrar que un modelo abierto, el reconocimiento de voz y la síntesis de voz corren juntos en un solo equipo, sin internet y con varios usuarios al mismo tiempo.

**Criterio de éxito:**3 o más usuarios a la vez, respuesta de voz en menos de 10 segundos en promedio y sin conexión a internet.

## 2. Montaje

| Componente | Detalle |
| --- | --- |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |
| Modelo de lenguaje | qwen2.5:3b, modelo abierto servido en el equipo con Ollama. |
| Reconocimiento de voz | Whisper small (MLX, mlx-community/whisper-small-mlx), en el mismo equipo. |
| Síntesis de voz | Piper es_MX-ald-medium.onnx (español México, voz masculina medium). |
| Red | Un router wifi sin cable de internet. Los teléfonos y el computador quedan en la misma red local. |
| Usuarios | 3 o 4 teléfonos. Cada uno abre la página de consulta con un código QR y habla por su micrófono. |
| Comprobación de la red | En cada consulta el servidor intenta abrir una conexión hacia internet (1.1.1.1, puerto 443) y guarda si lo logró. No depende de lo que diga quien opera. |
| Consumo eléctrico | Medidor de enchufe: vatímetro de enchufe, resolución de 0,1 W. La lectura la hace una persona, en reposo y durante la carga. |

## 3. Procedimiento

1. Se desconecta el router de internet frente a la cámara. La pantalla del demo muestra el estado de la red.
2. Cada teléfono abre la página de consulta con el código QR y escribe el nombre de quien pregunta.
3. Desde cada teléfono se hacen 10 consultas por voz, todos al mismo tiempo.
4. El servidor guarda de cada consulta: quién la hizo, la hora de inicio y de fin, el tiempo de cada etapa y si el equipo tenía salida a internet.
5. Se lee el medidor de consumo con el equipo en reposo y durante la carga, y se anota en la pantalla del demo.
6. El informe calcula los usuarios a la vez, el tiempo promedio y el máximo, y dice qué parte del criterio se cumple.

## 4. Resultados

30 consultas por voz de 3 usuario(s), hasta 3 a la vez, sin internet. Tiempo de respuesta promedio 7.16 s y máximo 13.09 s.

**Tabla 1. Lo que pide medir la especificación**

| Usuarios simultáneos | Tiempo promedio (s) | Tiempo máximo (s) | Consumo en reposo (W) | Consumo en carga (W) |
| --- | --- | --- | --- | --- |
| 3 | 7.16 | 13.09 | 7.4 | 41.8 |

**Tabla 2. El criterio, parte por parte**

| Parte del criterio | Meta | Medido | ¿Cumple? |
| --- | --- | --- | --- |
| Usuarios a la vez | 3 o más | 3 | Sí |
| Tiempo promedio de respuesta de voz | menos de 10 s | 7.16 s | Sí |
| Sin internet | sin salida en toda la sesión | sin salida | Sí |

«Usuarios a la vez» es el máximo de personas distintas que tenían una consulta en curso en el mismo instante, según la hora de inicio y de fin de cada consulta. El tiempo va desde que el servidor recibe el audio hasta que tiene lista la respuesta hablada. En promedio: escuchar 3.25 s, responder 2.61 s y hablar 0.38 s.

**Tabla 3. Por usuario**

| Usuario | Consultas | Promedio (s) | Máximo (s) |
| --- | --- | --- | --- |
| Dayana Mercado | 10 | 7.22 | 9.98 |
| Jairo Barrios | 10 | 6.21 | 7.97 |
| Marelvis Pérez | 10 | 8.04 | 13.09 |

## 5. Limitaciones

- **Programas distintos a los que nombra la especificación.**La especificación nombra llama.cpp o vLLM y whisper.cpp; aquí el modelo de lenguaje se sirve con Ollama y Whisper corre con MLX, la versión para procesadores de Apple. Los modelos son abiertos y corren igual en el equipo; cambia el programa que los ejecuta.
- **Un computador portátil, no el equipo final del nodo.**Los tiempos y el consumo son de este equipo.
- **El reconocimiento y la síntesis atienden una consulta a la vez.**Cuando llegan varias juntas, esperan turno; por eso el tiempo sube con cada usuario adicional.
- **Pocas personas y poco tiempo.**El protocolo es de 3 o 4 teléfonos con 10 consultas cada uno; no es una prueba de carga sostenida.
- **La comprobación de internet es una sola señal.**Que no haya salida hacia 1.1.1.1 indica que el equipo está aislado, y se complementa con el video, donde se ve la desconexión del router.

## 6. Enlaces

- **Video:**<https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing>
- **Repositorio:**<https://github.com/AnuarHarb/node-ia-caribe>
- **Código:**`interfaz/demo2_informe.py`, `interfaz/servidor.py`, `voz/`.
- **Datos medidos:**`resultados/demo2/turnos.jsonl`.
