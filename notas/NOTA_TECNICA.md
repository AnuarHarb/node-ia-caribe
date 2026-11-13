# Entrega del laboratorio · Nodo IA Caribe (TRL 3)

## Qué se entrega

Cinco demos miden el punto de partida del nodo. La especificación pide, por cada demo:

- **Nota técnica** de 2 a 3 páginas en PDF, con seis secciones: objetivo, montaje, procedimiento, resultados, limitaciones y enlaces.
- **Video** de 2 a 3 minutos, sin editar de más, subido como no listado. En el demo 4 es opcional.
- **Enlace** al código y a los datos.
- **Consentimientos** escritos de las personas cuya voz se graba. Se guardan; no se suben.

Las cinco notas van en un ZIP de máximo 10 MB. Los resultados y los enlaces se copian en el documento técnico, en la sección de antecedentes y punto de partida del TRL.

## Dónde está cada cosa

| Qué | Dónde |
| --- | --- |
| Nota de cada demo en PDF | `entregables/notas/` |
| ZIP con las cinco notas | `entregables/Nodo-IA-Caribe_Notas-tecnicas.zip` |
| Texto para el documento técnico | `entregables/RESUMEN-PARA-DOCUMENTO-TECNICO.md` |
| Nota de cada demo en Markdown | `notas/Demo-N_….md` |
| Enlaces a los videos | `entregables/enlaces.json` |
| Guion de cada video | `entregables/VIDEO-LABORATORIO.md` |
| Datos medidos | `resultados/demoN/` |
| Repositorio | https://github.com/AnuarHarb/node-ia-caribe |

## Cómo se generan las notas

Cada nota se arma sola a partir del informe medido de su demo (`resultados/demoN/informe.json`). El mismo contenido sale en tres formas: el PDF, la vista para imprimir y la pestaña **Resultados** de cada demo. Ninguna cifra se escribe a mano: si un dato no se midió, la nota dice «sin medir».

Para armar el paquete completo:

```bash
.venv/bin/python -m interfaz.entregar
```

El comando escribe los cinco PDF, el ZIP y el resumen, y al final lista lo que falta: demos sin medir, notas fuera de 2 a 3 páginas, videos sin enlace o un ZIP de más de 10 MB.

## Qué significa el estado de cada nota

- **Criterio cumplido:** se midió y se cumple el criterio de éxito de la especificación.
- **Evidencia parcial:** hay medición, pero falta una parte del criterio. La nota dice cuál.
- **Criterio no cumplido:** se midió y el resultado no alcanza el criterio.
- **Sin medición:** todavía no se ha corrido. La nota trae el montaje y el procedimiento.

## Lo que solo puede hacer una persona

- Grabar y subir el video de cada demo, y pegar su enlace en `entregables/enlaces.json`.
- Demo 1: grabar a 3 o 4 personas, 10 frases cada una, con consentimiento escrito.
- Demo 2: hacer la sesión con 3 o 4 teléfonos y el router sin internet, y anotar la lectura del medidor de consumo.
- Demo 3: confirmar la tarifa vigente del servicio de referencia en `demo3_comparacion/tarifa_referencia.json` para que el costo por tarea salga en dólares. Sin tarifa confirmada, la nota reporta los tokens medidos.
- Demo 4: reunir de 30 a 50 frases por variedad. En palenquero, con grabaciones públicas o una persona hablante designada por la Fundación Chano y Chalole, con consentimiento y aval.

## Cómo reproducir

- Entorno: `python3 -m venv .venv` y `.venv/bin/pip install -r requirements.txt`.
- Interfaz: `.venv/bin/python -m interfaz` y abrir `http://127.0.0.1:8765/`.
- Demos 1 a 4: necesitan Ollama con el modelo `qwen2.5:3b`. El demo 3 pide además la clave del servicio de referencia al correr; no se guarda en disco.
- Demo 5: no usa red ni modelo. `.venv/bin/python -m demo5_agentes.en_vivo`.
- Pruebas: `.venv/bin/python -m unittest interfaz.test_notas demo5_agentes.test_aislamiento demo3_comparacion.test_metodo demo4_wer.test_wer`.

## Responsable

Anuar Harb. El equipo y la fecha de cada medición quedan escritos en la nota de cada demo.
