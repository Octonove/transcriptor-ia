# -*- mode: python ; coding: utf-8 -*-
"""Spec de PyInstaller para TranscriptorIA (onedir, ventana sin consola).

Empaqueta ffmpeg.exe (con filtro whisper) via la variable FFMPEG_SRC (build.ps1).
El modelo Whisper NO se empaqueta: se descarga en el primer uso.
"""

import os

block_cipher = None

binaries = []
ffmpeg_src = os.environ.get("FFMPEG_SRC", "")
if ffmpeg_src and os.path.isfile(ffmpeg_src):
    binaries.append((ffmpeg_src, "."))

icon_path = os.environ.get("APP_ICON", "")
icon_arg = icon_path if (icon_path and os.path.isfile(icon_path)) else None

a = Analysis(
    ['..\\TranscriptorIA.py'],
    pathex=[],
    binaries=binaries,
    datas=[],
    hiddenimports=['PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'scipy', 'pandas', 'matplotlib', 'PyQt5', 'PyQt6', 'PySide6'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='TranscriptorIA',
    debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
    console=False, disable_windowed_traceback=False, target_arch=None,
    codesign_identity=None, entitlements_file=None, icon=icon_arg,
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas,
               strip=False, upx=False, upx_exclude=[], name='TranscriptorIA')
