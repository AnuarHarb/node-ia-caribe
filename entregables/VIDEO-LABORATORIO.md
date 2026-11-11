# Video de presentación del laboratorio (2–3 minutos)

Objetivo de la especificación: una sola pieza de **2 a 3 minutos** donde se vean las pruebas corriendo (pantalla), junto con la nota técnica y el enlace al repositorio.

## Opción A · Desde la interfaz (recomendada)

1. Arranca `.venv/bin/python -m interfaz` y abre `http://127.0.0.1:8765/`.
2. Corré al menos **Demo 5** y **Demo 3** (mitad local basta) desde cada página. Cada corrida guarda un `.webm` en `resultados/demoN/historial/`.
3. Une los fragmentos:

```bash
./scripts/montar-video-laboratorio.sh entregables/video-laboratorio.webm
```

4. Sube `entregables/video-laboratorio.webm` al canal que pida la convocatoria y pon el enlace en `NOTA_TECNICA.md` o en `NODO_VIDEO_LAB_URL`.

## Opción B · Grabación manual de pantalla

1. Misma interfaz; usa QuickTime, OBS o la herramienta que prefieras.
2. Guion sugerido (≈2 min 30 s):
   - 0:00 Portada y tarjetas 1→5.
   - 0:25 Demo 5: dos cajas, bloqueo, pruebas en verde.
   - 1:00 Demo 3: contadores local/referencia.
   - 1:35 Demo 4 WER o Demo 2 carga (si están listos).
   - 2:10 Pestaña Resultados: historial con video ▶ y PDF.
3. Exporta a MP4 y colócalo en `entregables/video-laboratorio.mp4`.

## Demo 5 por terminal (sin interfaz)

```bash
.venv/bin/python -m demo5_agentes.en_vivo
```

Graba la terminal si necesitas evidencia adicional; la especificación pide ver las pruebas en ejecución.
