"""Localizacion de FFmpeg (con filtro whisper) y utilidades de subproceso."""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def subprocess_kwargs() -> dict:
    kw: dict = {}
    if os.name == "nt":
        kw["creationflags"] = CREATE_NO_WINDOW
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kw["startupinfo"] = si
    return kw


def _app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def find_ffmpeg(override: str = "") -> str | None:
    if override and Path(override).is_file():
        return override
    app = _app_dir()
    cands = [app / "ffmpeg.exe", app / "_internal" / "ffmpeg.exe", app / "bin" / "ffmpeg.exe"]
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        cands.append(Path(meipass) / "ffmpeg.exe")
    local = os.environ.get("LOCALAPPDATA", "")
    if local:
        winget = Path(local) / "Microsoft" / "WinGet" / "Packages"
        if winget.is_dir():
            cands.extend(winget.glob("Gyan.FFmpeg*/**/bin/ffmpeg.exe"))
    for c in cands:
        try:
            if c.is_file():
                return str(c)
        except OSError:
            continue
    return shutil.which("ffmpeg")


def has_whisper(ffmpeg_path: str) -> bool:
    try:
        out = subprocess.run([ffmpeg_path, "-hide_banner", "-filters"],
                             capture_output=True, text=True, timeout=20,
                             **subprocess_kwargs()).stdout
        return "whisper" in out
    except (OSError, subprocess.SubprocessError):
        return False


_DUR_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)")


def get_duration(ffmpeg_path: str, media_path: str) -> float:
    """Duracion en segundos (parseando la salida de ffmpeg). 0 si no se sabe."""
    try:
        proc = subprocess.run([ffmpeg_path, "-hide_banner", "-i", media_path],
                              capture_output=True, text=True, timeout=30,
                              **subprocess_kwargs())
    except (OSError, subprocess.SubprocessError):
        return 0.0
    m = _DUR_RE.search((proc.stderr or "") + (proc.stdout or ""))
    if not m:
        return 0.0
    h, mm, ss = m.groups()
    try:
        return int(h) * 3600 + int(mm) * 60 + float(ss)
    except ValueError:
        return 0.0
