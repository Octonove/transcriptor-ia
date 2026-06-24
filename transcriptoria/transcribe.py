"""Transcripcion local con el filtro whisper de FFmpeg.

Detalle clave: el parser de filtergraph de FFmpeg no acepta rutas absolutas de
Windows (los dos puntos de C: se confunden con el separador de opciones). Por
eso ejecutamos FFmpeg con el directorio de trabajo en la carpeta del modelo y
usamos nombres RELATIVOS para 'model' y 'destination'. El fichero de entrada se
pasa con -i (fuera del filtergraph), donde su ruta absoluta no da problemas.
"""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from .ffmpeg_utils import get_duration, subprocess_kwargs

logger = logging.getLogger(__name__)


class TranscribeError(Exception):
    pass


def _parse_time(s: str) -> float | None:
    try:
        h, m, rest = s.split(":")
        return int(h) * 3600 + int(m) * 60 + float(rest)
    except (ValueError, AttributeError):
        return None


def transcribe(ffmpeg_path: str, model_file: str, input_file: str, language: str,
               out_srt: str, log_path: str, progress_cb=None) -> str:
    model_dir = str(Path(model_file).parent)
    model_rel = Path(model_file).name
    tmp_name = f".transcript_{os.getpid()}.srt"
    tmp_path = Path(model_dir) / tmp_name
    try:
        tmp_path.unlink(missing_ok=True)
    except OSError:
        pass

    total = get_duration(ffmpeg_path, input_file)
    lang = language or "auto"
    filt = (f"aresample=16000,whisper=model={model_rel}:language={lang}"
            f":use_gpu=false:destination={tmp_name}:format=srt")
    cmd = [ffmpeg_path, "-y", "-hide_banner", "-loglevel", "error",
           "-progress", "pipe:1", "-nostats",
           "-i", input_file, "-af", filt, "-f", "null", "-"]
    logger.info("Whisper (cwd=%s): %s", model_dir, " ".join(cmd))

    log = open(log_path, "wb")
    try:
        proc = subprocess.Popen(cmd, cwd=model_dir, stdout=subprocess.PIPE,
                                stderr=log, text=True, **subprocess_kwargs())
    except OSError as exc:
        log.close()
        raise TranscribeError(f"No se pudo iniciar FFmpeg: {exc}") from exc

    try:
        if proc.stdout is not None:
            for line in proc.stdout:
                line = line.strip()
                if line.startswith("out_time=") and total > 0 and progress_cb:
                    sec = _parse_time(line.split("=", 1)[1])
                    if sec is not None:
                        progress_cb(min(0.99, sec / total))
        proc.wait()
    finally:
        try:
            log.close()
        except OSError:
            pass

    if proc.returncode != 0 or not tmp_path.is_file():
        raise TranscribeError(_tail(log_path) or f"FFmpeg termino con codigo {proc.returncode}.")

    Path(out_srt).parent.mkdir(parents=True, exist_ok=True)
    try:
        Path(out_srt).unlink(missing_ok=True)
    except OSError:
        pass
    os.replace(str(tmp_path), out_srt)
    if progress_cb:
        progress_cb(1.0)
    return Path(out_srt).read_text(encoding="utf-8", errors="replace")


def srt_to_text(srt: str) -> str:
    """Convierte un SRT en texto plano (quita indices y marcas de tiempo)."""
    out = []
    for block in srt.replace("\r\n", "\n").split("\n\n"):
        lines = [ln for ln in block.split("\n") if ln.strip()]
        text_lines = [ln for ln in lines if not ln.strip().isdigit() and "-->" not in ln]
        if text_lines:
            out.append(" ".join(text_lines))
    return "\n".join(out)


def _tail(path: str, n: int = 8) -> str:
    try:
        t = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return "\n".join([ln for ln in t.splitlines() if ln.strip()][-n:])
