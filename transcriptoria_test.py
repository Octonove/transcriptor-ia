"""Prueba funcional de TranscriptorIA: transcribe la muestra de voz cacheada
(si esta disponible) + comprueba registro de modelos y construccion de UI."""

from __future__ import annotations

import sys
import tempfile
import tkinter as tk
from pathlib import Path

from transcriptoria import ffmpeg_utils, models, transcribe

ok = True


def check(name, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print(f"[{'OK ' if cond else 'FAIL'}] {name} {detail}")


ff = ffmpeg_utils.find_ffmpeg()
check("ffmpeg encontrado", bool(ff), f"-> {ff}")
check("ffmpeg con whisper", bool(ff) and ffmpeg_utils.has_whisper(ff))
check("registro de modelos", set(models.MODELS) == {"tiny", "base", "small"})

# Transcripcion real usando el modelo/muestra ya cacheados del test anterior
cache = Path(tempfile.gettempdir()) / "whispertest"
model = cache / "ggml-base.bin"
sample = cache / "sample.wav"
if ff and model.is_file() and sample.is_file():
    out = str(Path(tempfile.gettempdir()) / "transcriptoria_out.srt")
    log = str(Path(tempfile.gettempdir()) / "transcriptoria_ff.log")
    last = {"f": 0.0}
    text = transcribe.transcribe(ff, str(model), str(sample), "es", out, log,
                                 progress_cb=lambda f: last.__setitem__("f", f))
    plain = transcribe.srt_to_text(text)
    print("--- TEXTO ---"); print(plain)
    check("transcripcion produce texto", len(plain.strip()) > 5)
    check("progreso llego a ~1.0", last["f"] >= 0.9, f"-> {last['f']:.2f}")
    check("contiene palabras esperadas", "prueba" in plain.lower() or "inteligencia" in plain.lower())
else:
    print("(modelo/muestra no cacheados; se omite la transcripcion real)")

# UI
try:
    from transcriptoria.app import App
    root = tk.Tk(); root.withdraw()
    App(root)
    root.update_idletasks()
    root.destroy()
    check("UI construida", True)
except Exception as exc:  # noqa: BLE001
    import traceback
    traceback.print_exc()
    check("UI construida", False, str(exc))

print("\nRESULTADO:", "TODO OK" if ok else "HAY FALLOS")
sys.exit(0 if ok else 1)
