# Nodo IA Caribe · Laboratorio TRL 3

Mediciones de punto de partida para un nodo de inteligencia artificial soberano
en el Caribe colombiano: cinco demos reproducibles, informes PDF y evidencia de
corridas.

**Propietario:** [Fundación Código Abierto](https://codigoabierto.tech) (FCA)  
**Repositorio:** [github.com/AnuarHarb/node-ia-caribe](https://github.com/AnuarHarb/node-ia-caribe)  
**Licencia:** ver [LICENSE](LICENSE) (copyright FCA; uso educativo e investigación con atribución).

## Qué hay aquí

| Demo | Tema | Evidencia principal |
| --- | --- | --- |
| 1 | Voz en español costeño | Flujo de punta a punta y errores reales de reconocimiento, frase por frase |
| 2 | IA completa sin internet | Usuarios a la vez, tiempo promedio y máximo, red comprobada en cada consulta, consumo |
| 3 | IA local frente a referencia externa | 40 tareas, calificación a ciegas de dos personas, % comparables, kappa de Cohen |
| 4 | Línea base del error (WER) | Una cifra por variedad: palenquero y español costeño |
| 5 | Agentes aislados por entidad | Acceso cruzado bloqueado, registro de auditoría y 11 pruebas |

Cada demo tiene su **nota técnica** de 2 a 3 páginas (objetivo, montaje, procedimiento, resultados,
limitaciones y enlaces). Se arma sola con el informe medido; si un dato no se midió, dice «sin medir».

La forma recomendada de ejecutar y presentar todo es la **interfaz web** (puerto local 8765).

## Inicio rápido

```bash
git clone https://github.com/AnuarHarb/node-ia-caribe.git
cd node-ia-caribe
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
ollama pull qwen2.5:3b   # demos 1–4 (salvo demo 5)
.venv/bin/python -m interfaz
```

Abrir **http://127.0.0.1:8765/** — portada, cinco demos, informes, historial y PDF.

- **Entrega del laboratorio** (cómo va cada nota y qué falta): http://127.0.0.1:8765/nota-tecnica  
- **Calificación ciega (demo 3):** http://127.0.0.1:8765/calificar  
- Variables de entorno: copiar `.env.example` a `.env` si usas API comercial en el demo 3 (la clave no se guarda en disco en el servidor).

## Demos por separado (terminal)

**Demo 5** (sin internet ni modelo pesado adicional):

```bash
.venv/bin/python -m demo5_agentes.en_vivo
```

**Demo 3** — local y referencia:

```bash
.venv/bin/python -m demo3_comparacion.correr
# Referencia comercial (clave en el entorno, no en el repo):
export ANTHROPIC_API_KEY='…'
.venv/bin/python -m demo3_comparacion.correr --sin-local --referencia anthropic --modelo-referencia claude-haiku-4-5
```

**Demo 4** — WER:

```bash
.venv/bin/python -m demo4_wer.calcular --transcribir
```

El español costeño usa las frases del demo 1. El palenquero entra por dos caminos:

- grabar en el demo 1 eligiendo la variedad «palenquero» y escribiendo la frase acordada, o
- subir audio y transcripción correcta en la página del demo 4, sección «Armar el corpus»
  (quedan en `demo4_wer/corpus/palenquero/`).

En los dos casos hace falta consentimiento individual y el aval de la Fundación Chano y Chalole.
El protocolo pide de 30 a 50 frases por variedad; con menos, la nota queda como evidencia parcial.

Whisper no incluye el palenquero entre sus idiomas, así que las dos variedades se transcriben con el
idioma fijado en español. Para probar otra configuración: `DEMO4_IDIOMA_WHISPER=auto` (detección
automática) o un código de idioma.

El demo 4 tiene además una prueba por escrito: los modelos traducen estrofas de poemas entre español
y palenquero, y la salida se compara con la traducción humana del libro (chrF, con el control de no
traducir).

```bash
.venv/bin/python -m demo4_wer.traduccion                          # modelo local (Ollama)
export ANTHROPIC_API_KEY='…'
.venv/bin/python -m demo4_wer.traduccion --referencia anthropic   # agrega la referencia comercial
.venv/bin/python -m interfaz.entregar                             # lleva las cifras a la nota
```

Los poemas son obras con autor: van en `demo4_wer/corpus/poemas/poemas.json`, que no se sube al
repositorio. Lo que se publica es `resultados/demo4/traduccion.json`, con las cifras y dos versos de
ejemplo. Correr la referencia envía las estrofas a un servicio externo; hazlo solo con permiso de los
autores.

**Demo 2** — sin internet y con varios usuarios:

1. Desconecta el router de internet. La página del demo 2 muestra si el equipo tiene salida.
2. Cada teléfono abre el enlace del código QR y hace 10 consultas por voz, todos a la vez.
3. Anota en la misma página la lectura del medidor de consumo, en reposo y en carga.
4. Pulsa **Correr experimento**: el informe se calcula con las consultas por voz de la sesión.

Las consultas por texto sirven para probar que el servidor responde; no cuentan para el criterio.

**Costo por tarea del demo 3:** la nota reporta los tokens que midió el servicio de referencia. Para
que salga en dólares, escribe la tarifa vigente y su fuente en `demo3_comparacion/tarifa_referencia.json`.

## Estructura del repositorio

```
interfaz/          Servidor web, notas técnicas (PDF, HTML y Markdown) y paquete de entrega
demo3_comparacion/ Protocolo de comparación y calificación
demo4_wer/         Cálculo WER y prueba de traducción por escrito
demo5_agentes/     Aislamiento multi-entidad
voz/               ASR, LLM local y Piper (demo 1 y 2)
resultados/        Mediciones locales (gitignore). Ver resultados/README.md
ejemplo/resultados/ Medición base en el clon (python -m ejemplo.generar)
notas/             Notas técnicas por demo
entregables/       Notas en PDF, ZIP, enlaces a los videos y guion de cada video
ejemplo/           Medición base: notas y datos de referencia (no sustituye resultados/)
```

**.** `.venv/bin/python -m ejemplo.generar` escribe en `ejemplo/` cómo se verían las
cinco notas al completar el protocolo. Los demos 1, 2 y 4 combinan lo medido con datos sintéticos que
siguen su tendencia; cada nota lo dice en el encabezado y en el pie de cada página, y cada fila
sintética lleva `"sintetica": true`. No toca `resultados/` ni `entregables/`, y no sirve como evidencia.
Desde la portada o en `/medicion-base` (alias `/ejemplo`).

No subas al repositorio: `resultados/` (voz, historial, calificaciones), `.env`, API keys,
grabaciones con datos personales sin consentimiento documentado, ni `grabaciones/` con voz
identificable. En Git solo el historial ilustrativo en `ejemplo/resultados/`.

## Pruebas automatizadas

```bash
.venv/bin/python -m unittest interfaz.test_notas demo5_agentes.test_aislamiento demo3_comparacion.test_metodo demo4_wer.test_wer demo4_wer.test_traduccion
```

`interfaz.test_notas` comprueba que las cinco notas se generan, traen las seis secciones de la
plantilla y caben en 2 a 3 páginas.

## Entrega: notas, videos y enlaces

```bash
.venv/bin/python -m interfaz.entregar
```

Escribe las cinco notas en `entregables/notas/`, el ZIP `entregables/Nodo-IA-Caribe_Notas-tecnicas.zip`
(máximo 10 MB) y `entregables/RESUMEN-PARA-DOCUMENTO-TECNICO.md`, y lista lo que falta para radicar.

- Un video por demo, de 2 a 3 minutos, no listado (opcional en el demo 4). Qué debe verse en cada
  uno: `entregables/VIDEO-LABORATORIO.md`.
- El enlace de cada video se pega en `entregables/enlaces.json`; las notas lo toman de ahí.
- Los consentimientos de voz se guardan y no se suben.

## ¿GitHub Pages?

**No para el laboratorio completo.** GitHub Pages solo sirve sitios **estáticos** (HTML/CSS/JS sin backend). Este proyecto necesita:

- servidor Python (`interfaz`),
- Ollama / MLX / Whisper en tu máquina,
- subida de audio, SSE en vivo y a veces API keys.

**Qué sí puedes hacer:**

| Objetivo | Opción |
| --- | --- |
| Mostrar el código y el README | Este repo en GitHub (ya listo) |
| Publicar solo PDFs o informes exportados | Otra rama/`docs/` estática en Pages, o releases con adjuntos |
| Demostrar la interfaz en vivo | Ejecutar localmente, Cloud Agent, Railway/Render con servidor Python, o grabar el video del laboratorio |
| Documentación pública | Pages con un `docs/index.html` *sobre* el proyecto (sin correr los demos) |

Para una demo en la nube haría falta un host con Python, Ollama o modelos embebidos, y política clara de datos; no encaja en Pages tal cual.

### Publicar la página informativa (GitHub Pages)

El directorio [`docs/`](docs/) incluye `index.html` (landing estática, no ejecuta el laboratorio).

1. En GitHub: **Settings → Pages**.
2. **Build and deployment → Source:** Deploy from a branch.
3. **Branch:** `main` (o la que uses) y carpeta **`/docs`**.
4. Guardar. La URL quedará como `https://anuarharb.github.io/node-ia-caribe/` (o el dominio que asignes).

Tras el primer push con `docs/`, puede tardar unos minutos en publicarse.

## Autoría y contacto

Desarrollo y medición del laboratorio: equipo **Fundación Código Abierto**.  
Responsable de protocolo en los informes: **Anuar Harb** (según `interfaz/catalogo.py`).

Si reutilizas este trabajo, cita el repositorio y la fundación según [LICENSE](LICENSE).
