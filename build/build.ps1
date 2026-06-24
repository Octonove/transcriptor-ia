# Construye el ejecutable de TranscriptorIA (onedir) empaquetando FFmpeg (whisper).
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    $py = "C:\Users\Usuario\Desktop\proyectos\Aplicaciones Windows\CapturaPro\.venv\Scripts\python.exe"
}
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "== Localizando FFmpeg (con whisper) ==" -ForegroundColor Cyan
$ff = (Get-Command ffmpeg -ErrorAction SilentlyContinue).Source
if (-not $ff) {
    $winget = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
    if (Test-Path $winget) {
        $cand = Get-ChildItem -Path $winget -Recurse -Filter ffmpeg.exe -ErrorAction SilentlyContinue |
                Where-Object { $_.FullName -like "*Gyan.FFmpeg*" } | Select-Object -First 1
        if ($cand) { $ff = $cand.FullName }
    }
}
if ($ff) { Write-Host "FFmpeg: $ff" -ForegroundColor Green; $env:FFMPEG_SRC = $ff }
else { Write-Host "AVISO: FFmpeg no encontrado." -ForegroundColor Yellow; $env:FFMPEG_SRC = "" }

$icon = Join-Path $PSScriptRoot "icon.ico"
if (Test-Path $icon) { $env:APP_ICON = $icon } else { $env:APP_ICON = "" }

Write-Host "== Compilando TranscriptorIA ==" -ForegroundColor Cyan
Push-Location $root
& $py -m PyInstaller --noconfirm --clean (Join-Path $PSScriptRoot "TranscriptorIA.spec")
$code = $LASTEXITCODE
Pop-Location

if ($code -eq 0) {
    Write-Host "`n== LISTO ==" -ForegroundColor Green
    Write-Host "Ejecutable en: $(Join-Path $root 'dist\TranscriptorIA\TranscriptorIA.exe')"
} else { Write-Host "`nFallo (codigo $code)." -ForegroundColor Red; exit $code }
