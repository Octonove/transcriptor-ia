"""Genera build/icon.ico para TranscriptorIA (bocadillo con lineas de texto + IA)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


def make(size: int) -> Image.Image:
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=(99, 91, 255, 255))

    # Bocadillo de dialogo blanco
    m = int(s * 0.22)
    box = [m, int(s * 0.24), s - m, int(s * 0.70)]
    d.rounded_rectangle(box, radius=int(s * 0.08), fill=(255, 255, 255, 255))
    # pico del bocadillo
    px = int(s * 0.36)
    py = box[3]
    d.polygon([(px, py - 2), (px + int(s * 0.10), py - 2), (px, py + int(s * 0.10))],
              fill=(255, 255, 255, 255))

    # Lineas de texto (transcripcion)
    lx0 = box[0] + int(s * 0.08)
    lx1 = box[2] - int(s * 0.08)
    ly = box[1] + int(s * 0.10)
    gap = int(s * 0.11)
    w = max(3, int(s * 0.035))
    col = (99, 91, 255, 255)
    for i, frac in enumerate((1.0, 0.8, 0.55)):
        y = ly + i * gap
        d.line([(lx0, y), (lx0 + (lx1 - lx0) * frac, y)], fill=col, width=w)

    # Chispa de IA (estrella) arriba a la derecha
    cx, cy, r = int(s * 0.74), int(s * 0.30), int(s * 0.07)
    d.polygon([(cx, cy - r), (cx + r * 0.3, cy - r * 0.3), (cx + r, cy),
               (cx + r * 0.3, cy + r * 0.3), (cx, cy + r),
               (cx - r * 0.3, cy + r * 0.3), (cx - r, cy),
               (cx - r * 0.3, cy - r * 0.3)], fill=(255, 214, 90, 255))

    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    out = Path(__file__).with_name("icon.ico")
    sizes = [16, 24, 32, 48, 64, 128, 256]
    imgs = [make(sz) for sz in sizes]
    imgs[-1].save(out, format="ICO", sizes=[(s, s) for s in sizes], append_images=imgs[:-1])
    make(256).save(Path(__file__).with_name("icon_preview.png"))
    print("Icono generado:", out)


if __name__ == "__main__":
    main()
