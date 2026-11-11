# Nota técnica · Laboratorio Nodo IA Caribe (TRL 3)

## Resumen

Cinco demos miden el punto de partida del nodo de inteligencia artificial soberano para entidades del Caribe. Cada corrida desde la interfaz web deja un informe JSON, PDF y un **video corto** de la pantalla (`resultados/demoN/historial/{corrida_id}.webm`).

## Enlaces obligatorios de la especificación

| Campo | Valor |
| --- | --- |
| Repositorio | https://github.com/AnuarHarb/node-ia-caribe |
| Video de presentación (2–3 min) | Guion en `entregables/VIDEO-LABORATORIO.md`. Montaje sugerido: `scripts/montar-video-laboratorio.sh` (une los `.webm` del historial con ffmpeg). |
| Interfaz local | `http://127.0.0.1:8765/` tras `.venv/bin/python -m interfaz` |
| Página informativa (GitHub Pages) | Carpeta `docs/` del repositorio; no ejecuta los demos |

## Cómo reproducir

- Entorno: `python3 -m venv .venv` y `pip install -r requirements.txt`.
- Demo 5 (sin red ni modelo): `.venv/bin/python -m demo5_agentes.en_vivo` o botón **Correr experimento** en la página Demo 5.
- Demos 2–4: requieren Ollama (`ollama serve`, modelo `qwen2.5:3b`). Demo 3 acepta API key opcional en el mismo botón de corrida.
- Demo 1: grabación de voz en la misma página (consentimiento previo).

## Video por corrida (automático)

Al pulsar **Correr experimento** en los demos 2, 3, 4 y 5, el navegador captura la pestaña *Experimento* (escena + bitácora) y sube un WebM al terminar la corrida. En **Resultados → Historial**, las corridas con video muestran ▶ y el enlace *Ver video de la corrida*.

## PDF

Los informes usan tipografía **Poppins** (sistema de diseño FCA), no Times por defecto. Descarga en cada demo o en el historial.

## Demo 5 · Entidades ficticias

Slugs coherentes con la alianza: `alcaldia-santa-marta` y `gobernacion-atlantico`. La nota por demo está en `notas/Demo-5_Agentes-aislados-por-entidad.md`.

## Responsable

Anuar Harb · mediciones en equipo local documentado en cada `informe.json`.
