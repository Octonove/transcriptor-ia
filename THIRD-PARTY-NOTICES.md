# Avisos de terceros (Third-Party Notices)

TranscriptorIA empaqueta y/o utiliza los siguientes componentes de terceros:

## FFmpeg — GNU GPL v3
TranscriptorIA incluye **FFmpeg** (https://ffmpeg.org) como programa
independiente que la aplicación invoca para extraer audio y ejecutar el motor de
transcripción Whisper (filtro `whisper`, basado en whisper.cpp). FFmpeg se
distribuye bajo la **GNU General Public License v3**.

- Código fuente de FFmpeg: https://ffmpeg.org/download.html
- Build empaquetada (Gyan.dev): https://www.gyan.dev/ffmpeg/builds/
- Texto de la licencia GPL: https://www.gnu.org/licenses/gpl-3.0.html

## Whisper / whisper.cpp y modelos GGML — MIT
- Modelo Whisper de OpenAI (https://github.com/openai/whisper) — licencia MIT.
- whisper.cpp y modelos GGML (https://github.com/ggerganov/whisper.cpp) — licencia MIT.
- Los modelos se descargan desde https://huggingface.co/ggerganov/whisper.cpp

## Otras dependencias
- **Pillow** (PIL) — licencia HPND/MIT-like — https://python-pillow.org

El resto del código de TranscriptorIA se distribuye bajo licencia MIT (ver `LICENSE`).
Todo el procesamiento es local: TranscriptorIA no envía tus archivos a ningún servidor.
