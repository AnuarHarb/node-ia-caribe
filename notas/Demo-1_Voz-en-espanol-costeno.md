# Nota técnica · Voz en español costeño

Evidencia TRL 3 · Nodo IA Caribe.

| Responsable | Anuar Harb |
| Frases medidas | 6 |
| WER corpus | 17.39 % |

## Modelos

- **Whisper:** Whisper small (MLX, mlx-community/whisper-small-mlx)
- **LLM (Ollama):** qwen2.5:3b
- **TTS (Piper):** Piper es_MX-ald-medium.onnx (español México, voz masculina medium)

## Referencia vs transcripción

La referencia humana es lo dicho (guion revisado), no la transcripción del ASR. Se corrigieron dos referencias que habían copiado el texto del reconocimiento.

## Alucinaciones del asistente (sin ocultar)

El modelo local inventó requisitos y ubicaciones sin base documental. Eso motiva conectar el asistente a la información oficial de cada entidad (RAG o integración).

- **Frase 692fecb8f526:** El asistente pidió «cédula de residencia»; el ciudadano hablaba de un certificado de residencia. Requisito inventado.
  - Guion: _Buenas, vengo a pedir un certificado de residencia. ¿Qué papeles tengo que traer?_
  - Respuesta: _Tienes que traer tu documento de identidad y tu cédula de residencia._

- **Frase d6c300d069fc:** Inventó que la oficina del predial «está en la avenida principal» sin dato en la petición.
  - Guion: _¿Dónde queda la oficina del predial? Es que me perdí._
  - Respuesta: _El oficinal peredial está en la avenida principal de la ciudad. ¿Cómo te va a llegar?_

## Limitaciones

Muestra corta con un hablante; no sustituye un estudio dialectal. El sí/no de coincidencia exacta es aparte del WER (este último cuenta ediciones palabra a palabra).
