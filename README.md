# Demos de laboratorio · Nodo IA Caribe

Medición del punto de partida (TRL 3) en este computador: Apple M2 Pro, 16 GB. Los números salen de los comandos de abajo. Lo que todavía no se ha grabado o calificado queda pendiente; no se rellena.

Entorno:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
ollama pull qwen2.5:3b
```

## Demo 5 · Agentes aislados por entidad

Ya se puede correr entero, sin internet y sin modelo.

```bash
.venv/bin/python -m demo5_agentes.en_vivo
```

Deja `resultados/demo5/informe.html`, la tabla de las 11 pruebas y la nota en `notas/Demo-5_Agentes-aislados-por-entidad.md`. Entidades ficticias: `alcaldia-santa-marta` y `gobernacion-atlantico`. Para el video de entrega (2–3 min): `entregables/VIDEO-LABORATORIO.md`.

## Interfaz (recomendado)

Una sola aplicación con portada, cinco páginas y avance en vivo:

```bash
.venv/bin/python -m interfaz
```

Abrir `http://127.0.0.1:8765/`. Cada demo tiene su página, el último informe y el botón **Correr experimento**. En la sección del informe: **Vista PDF**, **Descargar PDF** (Poppins, no Times) y video de corrida en `resultados/demoN/historial/*.webm` (demos 2–5). **Nota técnica:** `http://127.0.0.1:8765/nota-tecnica`.

## Demo 1 · Voz en español costeño

Desde la interfaz, en **Demo 1**, o con `python -m voz.servidor` si solo quieres voz. Hace falta consentimiento escrito antes de grabar.

## Demo 2 · IA completa sin internet

1. Encender el servidor del demo 1.
2. Conectar el computador y tres o cuatro teléfonos a un router. Desconectar el cable de internet del router delante de la cámara.
3. En la página **Demo 2** hay un **código QR**, un enlace clicable y un campo para **poner la IPv4 del Mac** si la detección falla (el QR se regenera al instante; queda guardado en ese navegador).
4. En el computador abrir `http://127.0.0.1:8765/?modo=sala` para ver los tiempos. Si hay medidor de enchufe, anotar reposo y carga ahí.
5. El criterio es tres usuarios a la vez, respuesta de voz en menos de 10 segundos en promedio, sin internet.

`voz/carga.py` mide la cola con texto, no con voz. Esa cifra es parcial y no reemplaza la de los teléfonos.

## Demo 3 · IA local frente a una referencia externa

Cuarenta tareas ficticias. Primero el modelo local:

```bash
.venv/bin/python -m demo3_comparacion.correr
```

La referencia comercial no se inventa. La clave **no va en el código**: exporta una variable en el shell o copia `.env.example` a `.env` y cárgala antes de correr. Demos 1, 2, 4 y 5 no usan clave externa.

En la página **Demo 3** pegá la API key (opcional), elegí el modelo y usá un solo **Correr experimento**: primero la mitad local y, si hay clave, la referencia comercial en el mismo flujo. La clave no se guarda en disco en el servidor.

Por terminal (alternativa):

```bash
export ANTHROPIC_API_KEY='tu-clave'
.venv/bin/python -m demo3_comparacion.correr --sin-local --referencia anthropic --modelo-referencia claude-haiku-4-5
```

O un JSON `{ "T01": "respuesta...", ... }` exportado de la interfaz del servicio:

```bash
.venv/bin/python -m demo3_comparacion.correr --sin-local --referencia-archivo respuestas.json --modelo-referencia "nombre y fecha del servicio"
```

Cuando las 40 tareas tienen las dos respuestas, aparecen `resultados/demo3/ciego.json` y `clave.json`. Dos personas abren `demo3_comparacion/calificar.html`, cargan solo el ciego, y cada una descarga su calificación. `clave.json` no se les muestra.

```bash
.venv/bin/python -m demo3_comparacion.metricas resultados/demo3/clave.json calificacion-una.json calificacion-otra.json
```

## Demo 4 · WER en palenquero y en costeño

El costeño sale de las filas del demo 1. El palenquero no se graba a la comunidad en esta prueba: van audios públicos, o una persona hablante que designe la Fundación Chano y Chalole, con consentimiento y aval. Cada frase es `001.wav` y `001.txt` (la transcripción correcta) dentro de `demo4_wer/corpus/palenquero/`.

```bash
.venv/bin/python -m demo4_wer.calcular --transcribir
```

Whisper va sin forzar idioma. El WER es el del corpus, con jiwer, en minúsculas y sin puntuación. Sin esas grabaciones el comando no publica una cifra.

## Qué ya queda medido en código

```bash
.venv/bin/python -m unittest demo5_agentes.test_aislamiento demo3_comparacion.test_metodo demo4_wer.test_wer
```
