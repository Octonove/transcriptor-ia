# TranscriptorIA

Aplicación de escritorio para **Windows** que transcribe **audio y vídeo a texto** y genera **subtítulos (.srt)** usando IA (Whisper de OpenAI), **100% en tu PC**.

## ⬇️ Descargar (Windows 10/11)

### ➡️ [**Descargar TranscriptorIA (instalador .exe)**](https://github.com/Octonove/transcriptor-ia/releases/latest/download/TranscriptorIA-Setup.exe)

Descarga **directa** del instalador, sin registro (el modelo de IA se descarga al primer uso). También puedes ver la [última versión y notas](https://github.com/Octonove/transcriptor-ia/releases/latest).

> Si Windows muestra *"Windows protegió tu PC"* (es normal en programas nuevos sin firma): pulsa **Más información → Ejecutar de todas formas**. Se instala sin permisos de administrador.

## Por qué es diferente
- **Privado**: tus archivos **no se suben a internet**. Ideal para entrevistas, reuniones y grabaciones confidenciales (RGPD).
- **Sin límite de minutos** ni marca de agua.
- **Funciona sin conexión** una vez descargado el modelo.

## Funciones
- Transcribe MP3, WAV, M4A, MP4, MKV, etc.
- Elige modelo (Tiny / Base / Small) según rapidez vs. precisión.
- Idioma automático o fijo (Español, Inglés, …).
- Edita la transcripción y exporta a **TXT** o **SRT**.

## Cómo funciona
Usa el motor **Whisper integrado en FFmpeg** (filtro `whisper` / whisper.cpp), por lo que no necesita instalar PyTorch ni librerías de IA pesadas. El **modelo Whisper se descarga la primera vez** (Tiny ~75 MB, Base ~142 MB, Small ~466 MB) y se guarda en `%APPDATA%\TranscriptorIA\models\`.

> Detalle técnico: el filtro de FFmpeg no admite rutas absolutas de Windows en su parser; por eso se ejecuta con el directorio de trabajo en la carpeta del modelo y rutas relativas.

## Ejecutar en desarrollo
```powershell
./run.ps1
```

## Construir el ejecutable / instalador
```powershell
./build/build.ps1            # dist\TranscriptorIA\TranscriptorIA.exe (FFmpeg incluido)
./build/build-installer.ps1  # installer\TranscriptorIA-Setup-1.0.0.exe
```

## Stack
Python 3.14 + Tkinter + FFmpeg (filtro whisper) + PyInstaller + Inno Setup.
