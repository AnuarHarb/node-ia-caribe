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
| 1 | Voz en español costeño | `resultados/demo1/` · WER y flujo punta a punta |
| 2 | IA completa sin internet | Tiempos con router desconectado · QR a teléfonos |
| 3 | Local vs referencia comercial | 40 tareas · paquete ciego · calificación humana |
| 4 | WER palenquero y costeño | Corpus en `demo4_wer/corpus/` |
| 5 | Agentes aislados por entidad | 11 pruebas sin red |

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

- **Nota técnica del laboratorio:** http://127.0.0.1:8765/nota-tecnica  
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

El costeño consume las filas del demo 1; el palenquero requiere corpus con consentimiento
(ver `demo4_wer/corpus/palenquero/`).

## Estructura del repositorio

```
interfaz/          Servidor web y exportación PDF
demo3_comparacion/ Protocolo de comparación y calificación
demo4_wer/         Cálculo WER
demo5_agentes/     Aislamiento multi-entidad
voz/               ASR, LLM local y Piper (demo 1 y 2)
resultados/        Informes JSON, PDF, historial y videos .webm
notas/             Notas técnicas por demo
entregables/       Guion de video de laboratorio
```

No subas al repositorio: `.env`, API keys, grabaciones con datos personales sin consentimiento
documentado, ni `grabaciones/` si contienen voz identificable (revisa `.gitignore`).

## Pruebas automatizadas

```bash
.venv/bin/python -m unittest demo5_agentes.test_aislamiento demo3_comparacion.test_metodo demo4_wer.test_wer
```

## Video e informes

- Video de presentación (2–3 min): guion en `entregables/VIDEO-LABORATORIO.md`  
- Por corrida: captura automática en demos 2–5 → `resultados/demoN/historial/*.webm`  
- PDF: tipografía Poppins (sistema de diseño FCA)

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
