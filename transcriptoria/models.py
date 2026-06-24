"""Registro y descarga de modelos Whisper (GGML, de whisper.cpp)."""

from __future__ import annotations

import logging
import os
import urllib.request
from pathlib import Path

from .config import models_dir

logger = logging.getLogger(__name__)

_BASE_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/"

# clave -> (fichero, MB aprox, descripcion)
MODELS = {
    "tiny":  ("ggml-tiny.bin",  75,  "Rapido · menos preciso"),
    "base":  ("ggml-base.bin",  142, "Equilibrado (recomendado)"),
    "small": ("ggml-small.bin", 466, "Mas preciso · mas lento"),
}
ORDER = ["tiny", "base", "small"]


def model_path(key: str) -> Path:
    return models_dir() / MODELS[key][0]


def is_downloaded(key: str) -> bool:
    p = model_path(key)
    return p.is_file() and p.stat().st_size > 1_000_000


def label(key: str) -> str:
    fname, mb, desc = MODELS[key]
    estado = "descargado" if is_downloaded(key) else f"~{mb} MB a descargar"
    return f"{key.capitalize()} — {desc} ({estado})"


def download(key: str, progress_cb=None) -> str:
    """Descarga el modelo si no esta. progress_cb(fraccion 0..1)."""
    dst = model_path(key)
    if is_downloaded(key):
        return str(dst)
    url = _BASE_URL + MODELS[key][0]
    tmp = str(dst) + ".part"
    logger.info("Descargando modelo %s desde %s", key, url)
    req = urllib.request.Request(url, headers={"User-Agent": "TranscriptorIA"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        got = 0
        with open(tmp, "wb") as f:
            while True:
                chunk = resp.read(1 << 16)
                if not chunk:
                    break
                f.write(chunk)
                got += len(chunk)
                if progress_cb and total:
                    progress_cb(min(0.999, got / total))
    os.replace(tmp, dst)
    return str(dst)
