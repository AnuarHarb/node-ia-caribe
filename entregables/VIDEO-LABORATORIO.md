# Videos de los demos

La especificación pide **un video por demo**, de **2 a 3 minutos**, sin editar de más, subido como **no listado** (YouTube o Drive con enlace abierto). En el demo 4 el video es opcional: basta la tabla de resultados.

## Antes de grabar

1. Arranca la interfaz: `.venv/bin/python -m interfaz` y abre `http://127.0.0.1:8765/`.
2. En cada demo, pestaña **Experimento**, bloque **Video para la entrega**: **Empezar a grabar** → comparte pantalla o ventana → **Detener y guardar**. El archivo queda en `entregables/videos/` con nombre `Nodo-IA-Caribe_Demo-N_….webm`.
3. También puedes usar QuickTime (Cmd + Shift + 5) u OBS si necesitas cámara, varios monitores o el router físico con más claridad (recomendado en el demo 2).
4. Ten firmado el consentimiento de cada persona cuya voz se oiga. Se guarda; no se sube.

## Qué debe verse en cada video

### Demo 1 · Voz en español costeño

La especificación pide: una persona habla en costeño, la transcripción aparece en pantalla, el asistente responde en voz y se ve un error.

1. Página del demo 1, con el nombre del hablante escrito.
2. La persona dice dos o tres frases del guion con su habla natural.
3. En cada una: la transcripción en pantalla y la respuesta en voz alta.
4. Una frase donde el sistema se equivoque, con la transcripción correcta al lado.
5. Pestaña **Resultados**: la tabla con la columna «¿Correcta?» y el WER.

### Demo 2 · IA completa sin internet

La especificación pide: el cable desconectado, varios teléfonos preguntando a la vez y las respuestas.

1. Con el teléfono que graba: se desconecta el cable de internet del router.
2. En el computador, la página del demo 2 dice «sin salida a internet».
3. Tres o cuatro teléfonos abren la página con el código QR y preguntan por voz al mismo tiempo.
4. Se oyen las respuestas en los teléfonos.
5. El medidor de consumo, en reposo y durante la carga, si lo hay.
6. Pestaña **Resultados**: usuarios a la vez, tiempo promedio y máximo.

### Demo 3 · IA local frente a referencia externa

La especificación pide: una tarea pasando por los dos caminos y la hoja de calificación a ciegas.

1. Página del demo 3: una tarea resuelta por el modelo local y por el servicio de referencia.
2. La hoja de calificación en `/calificar`: solo se ve «respuesta A» y «respuesta B», con las cuatro dimensiones de 1 a 5.
3. Pestaña **Resultados**: calidad promedio, porcentaje de tareas comparables, kappa de Cohen y las tareas donde pierde el modelo local.

### Demo 4 · Línea base del error (WER) · opcional

Si se graba: la tabla de resultados con una fila por variedad (número de frases y WER) y dos o tres frases con su transcripción correcta y la del sistema.

### Demo 5 · Agentes aislados por entidad

La especificación pide: los dos agentes, el intento bloqueado, el registro de auditoría y las pruebas en verde.

1. Página del demo 5, botón **Correr experimento**.
2. Los dos agentes escriben, cada uno en su caja.
3. El agente de la alcaldía intenta leer un archivo de la gobernación y queda bloqueado.
4. El registro de auditoría, con el intento negado.
5. Las 11 pruebas en verde.

## Después de grabar

1. Sube cada video como no listado.
2. Pega cada enlace en `entregables/enlaces.json`, en el número de su demo.
3. Corre `.venv/bin/python -m interfaz.entregar`. Las notas toman el enlace de ahí y el comando avisa si falta alguno.

## Videos que guarda la interfaz

Al pulsar **Correr experimento**, el navegador puede grabar la pestaña y guardar un `.webm` junto a la corrida, en `resultados/demoN/historial/`. Sirve de respaldo. No reemplaza el video del demo cuando hay que mostrar personas, teléfonos o el router.
