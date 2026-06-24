"""Ventana principal de TranscriptorIA."""

from __future__ import annotations

import logging
import os
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from . import APP_NAME, APP_VERSION
from . import ffmpeg_utils, models, theme, transcribe
from .config import default_output_dir, get_data_dir

logger = logging.getLogger(__name__)

LANGS = [("Detectar automaticamente", "auto"), ("Espanol", "es"), ("Ingles", "en"),
         ("Frances", "fr"), ("Aleman", "de"), ("Italiano", "it"), ("Portugues", "pt")]


def run_async(root, func, on_done):
    box: dict = {}

    def worker():
        try:
            box["value"] = func()
        except Exception as exc:  # noqa: BLE001
            box["error"] = exc

    t = threading.Thread(target=worker, daemon=True)
    t.start()

    def poll():
        if t.is_alive():
            try:
                root.after(150, poll)
            except tk.TclError:
                pass
            return
        on_done(box.get("value"), box.get("error"))

    try:
        root.after(150, poll)
    except tk.TclError:
        pass


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.ffmpeg = ffmpeg_utils.find_ffmpeg()
        self._input = None
        self._srt = ""
        self._busy = False
        self._frac = 0.0
        self._phase = ""
        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        theme.apply(self.root)
        theme.header(self.root, APP_NAME, "Audio/video a texto y subtitulos — 100% en tu PC")

        top = ttk.Frame(self.root, padding=(16, 8))
        top.pack(fill="x")

        row = ttk.Frame(top)
        row.pack(fill="x", pady=4)
        ttk.Button(row, text="Elegir audio o video...", command=self._pick).pack(side="left")
        self.file_lbl = ttk.Label(row, text="Ningun archivo elegido", foreground="#666")
        self.file_lbl.pack(side="left", padx=10)

        opts = ttk.Frame(top)
        opts.pack(fill="x", pady=4)
        ttk.Label(opts, text="Modelo:").pack(side="left")
        self.model_box = ttk.Combobox(opts, width=42, state="readonly",
                                      values=[models.label(k) for k in models.ORDER])
        self.model_box.current(models.ORDER.index("base"))
        self.model_box.pack(side="left", padx=(4, 16))
        ttk.Label(opts, text="Idioma:").pack(side="left")
        self.lang_box = ttk.Combobox(opts, width=24, state="readonly",
                                     values=[l[0] for l in LANGS])
        self.lang_box.current(1)  # Espanol
        self.lang_box.pack(side="left", padx=4)

        act = ttk.Frame(top)
        act.pack(fill="x", pady=6)
        self.go_btn = ttk.Button(act, text="Transcribir", style="Primary.TButton",
                                 command=self._do_transcribe)
        self.go_btn.pack(side="left")
        if not self.ffmpeg or not ffmpeg_utils.has_whisper(self.ffmpeg):
            self.go_btn.state(["disabled"])
        self.bar = ttk.Progressbar(act, length=320, mode="determinate", maximum=100)
        self.bar.pack(side="left", padx=12)

        body = ttk.Frame(self.root, padding=(16, 4))
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Transcripcion (puedes editarla):",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.text = scrolledtext.ScrolledText(body, height=14, wrap="word",
                                              font=("Segoe UI", 10))
        self.text.pack(fill="both", expand=True, pady=4)

        exp = ttk.Frame(body)
        exp.pack(fill="x")
        self.txt_btn = ttk.Button(exp, text="Guardar TXT...", command=self._save_txt)
        self.txt_btn.pack(side="left", padx=(0, 6))
        self.srt_btn = ttk.Button(exp, text="Guardar subtitulos SRT...", command=self._save_srt)
        self.srt_btn.pack(side="left")
        self.txt_btn.state(["disabled"])
        self.srt_btn.state(["disabled"])

        self.status = theme.status_bar(self.root, "Tus archivos no salen de este equipo.")
        if not self.ffmpeg or not ffmpeg_utils.has_whisper(self.ffmpeg):
            self._set_status("FFmpeg con Whisper no disponible: la transcripcion esta desactivada.")

        self.root.update_idletasks()
        w = max(720, self.root.winfo_reqwidth() + 24)
        h = max(560, self.root.winfo_reqheight() + 12)
        self.root.geometry(f"{w}x{h}")
        self.root.minsize(700, 540)

    # --------------------------------------------------------------- acciones
    def _pick(self) -> None:
        f = filedialog.askopenfilename(
            title="Elige audio o video",
            filetypes=[("Audio/Video", "*.mp3 *.wav *.m4a *.aac *.ogg *.flac *.mp4 *.mkv *.mov *.avi *.webm"),
                       ("Todos", "*.*")])
        if f:
            self._input = f
            self.file_lbl.configure(text=Path(f).name)

    def _model_key(self) -> str:
        return models.ORDER[self.model_box.current()]

    def _lang_code(self) -> str:
        return LANGS[self.lang_box.current()][1]

    def _do_transcribe(self) -> None:
        if self._busy:
            return
        if not self._input:
            messagebox.showinfo(APP_NAME, "Elige primero un archivo de audio o video.")
            return
        if not self.ffmpeg:
            messagebox.showerror(APP_NAME, "FFmpeg no esta disponible.")
            return
        self._busy = True
        self.go_btn.state(["disabled"])
        self.txt_btn.state(["disabled"])
        self.srt_btn.state(["disabled"])
        self._frac = 0.0
        self._phase = "Preparando..."
        model_key = self._model_key()
        lang = self._lang_code()
        log = str(get_data_dir() / "ffmpeg_whisper.log")
        out_srt = str(get_data_dir() / "ultima_transcripcion.srt")

        def cb(f):
            self._frac = float(f)

        def work():
            mpath = models.model_path(model_key)
            if not models.is_downloaded(model_key):
                self._phase = f"Descargando modelo '{model_key}' (solo la primera vez)..."
                self._frac = 0.0
                models.download(model_key, progress_cb=cb)
            self._phase = "Transcribiendo... (puede tardar segun la duracion)"
            self._frac = 0.0
            return transcribe.transcribe(self.ffmpeg, str(mpath), self._input,
                                         lang, out_srt, log, progress_cb=cb)

        def done(value, error):
            self._busy = False
            self.go_btn.state(["!disabled"])
            self.bar.configure(value=0)
            if error:
                logger.exception("Transcripcion fallo", exc_info=error)
                self._set_status("La transcripcion fallo.")
                messagebox.showerror(APP_NAME, f"No se pudo transcribir:\n{error}")
                return
            self._srt = value
            self.text.delete("1.0", "end")
            self.text.insert("1.0", transcribe.srt_to_text(value))
            self.txt_btn.state(["!disabled"])
            self.srt_btn.state(["!disabled"])
            self._set_status("Transcripcion lista. Revisala, editala y exporta a TXT o SRT.")

        self._poll_progress()
        run_async(self.root, work, done)

    def _poll_progress(self) -> None:
        if not self._busy:
            return
        try:
            self.bar.configure(value=self._frac * 100)
            if self._phase:
                self._set_status(self._phase)
        except tk.TclError:
            return
        self.root.after(200, self._poll_progress)

    def _save_txt(self) -> None:
        out = filedialog.asksaveasfilename(
            initialdir=str(default_output_dir()), initialfile="transcripcion.txt",
            defaultextension=".txt", filetypes=[("Texto", "*.txt")])
        if not out:
            return
        try:
            Path(out).write_text(self.text.get("1.0", "end").strip() + "\n", encoding="utf-8")
            self._set_status(f"Guardado: {out}")
            self._offer_open(out)
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"No se pudo guardar:\n{exc}")

    def _save_srt(self) -> None:
        out = filedialog.asksaveasfilename(
            initialdir=str(default_output_dir()), initialfile="subtitulos.srt",
            defaultextension=".srt", filetypes=[("Subtitulos SRT", "*.srt")])
        if not out:
            return
        try:
            Path(out).write_text(self._srt, encoding="utf-8")
            self._set_status(f"Guardado: {out}")
            self._offer_open(out)
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"No se pudo guardar:\n{exc}")

    def _offer_open(self, path: str) -> None:
        if messagebox.askyesno(APP_NAME, f"Guardado en:\n{path}\n\n¿Abrir la carpeta?"):
            try:
                subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
            except OSError:
                pass

    def _set_status(self, text: str) -> None:
        try:
            self.status.configure(text=text)
        except tk.TclError:
            pass
