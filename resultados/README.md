# Mediciones locales (no se suben al repositorio)

Por tratamiento de datos sensibles, **todo lo que grabes o midas en la interfaz se guarda solo aquí**
(informes, historial, turnos de voz, calificaciones, videos `.webm`). No se sube al repositorio.

En un clon sin esta carpeta, la interfaz muestra la **medición base del equipo** en
`ejemplo/resultados/` (ver `/medicion-base` en el servidor local).

## Generar datos en tu equipo

| Demo | Comando / acción |
|------|------------------|
| 1 | Voz en `/demos/1` o importar `filas.json` / `turnos.jsonl` |
| 2 | Sesión por voz con el router sin internet |
| 3 | `demo3_comparacion/correr.py` y calificación en `/calificar` |
| 4 | `python -m demo4_wer.calcular`, traducción `python -m demo4_wer.traduccion` |
| 5 | `python -m demo5_agentes.en_vivo` o pruebas en el informe |

Notas técnicas con medición real: `python -m interfaz.entregar` (lee esta carpeta).
