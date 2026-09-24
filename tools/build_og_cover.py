#!/usr/bin/env python3
"""Render the 1200x630 social share cover from the bundled typefaces.

Run locally after a title, subtitle, or palette change, then commit the PNG:

    python3 tools/build_og_cover.py

Requires Pillow. The Pages build only copies the committed PNG.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "pages/assets/fonts"
OUTPUT = ROOT / "pages/assets/og-cover.png"
WIDTH, HEIGHT = 1200, 630

# Palette from pages/assets/book.css :root tokens.
PAPER = "#e7e8ea"
INK = "#172033"
BLUE = "#2447d8"
RED = "#b92d2a"
TRACE = "#6a7180"
WHITE = "#ffffff"


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def _fit(draw: ImageDraw.ImageDraw, text: str, name: str, size: int, width: int) -> ImageFont.FreeTypeFont:
    font = _font(name, size)
    while draw.textlength(text, font=font) > width and size > 12:
        size -= 2
        font = _font(name, size)
    return font


def render(output: Path = OUTPUT) -> Path:
    publication = json.loads((ROOT / "pages/publication.json").read_text(encoding="utf-8"))
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)

    margin = 72
    sheet = (40, 40, WIDTH - 40, HEIGHT - 40)
    draw.rectangle(sheet, fill=WHITE, outline=INK, width=2)

    # Capture strip, echoing the home hero.
    mono = _font("IBMPlexMono-Regular.ttf", 17)
    strip_y = 64
    draw.text((margin, strip_y), "CAPTURE 01", font=mono, fill=RED)
    date = publication["publication_date"]
    draw.text(((WIDTH - draw.textlength(date, font=mono)) / 2, strip_y), date, font=mono, fill=RED)
    label = "PUBLIC SOURCE"
    draw.text((WIDTH - margin - draw.textlength(label, font=mono), strip_y), label, font=mono, fill=RED)
    draw.line((40, 98, WIDTH - 40, 98), fill=RED, width=1)

    kicker = _font("IBMPlexMono-Regular.ttf", 18)
    draw.text((margin, 132), publication["publisher"].upper(), font=kicker, fill=RED)

    title = publication["title"].upper()
    title_font = _fit(draw, title, "BarlowCondensed-SemiBold.ttf", 176, WIDTH - 2 * margin)
    draw.text((margin - 6, 150), title, font=title_font, fill=INK)

    subtitle_font = _fit(
        draw, publication["subtitle"], "BarlowCondensed-SemiBold.ttf", 50, WIDTH - 2 * margin
    )
    draw.text((margin, 356), publication["subtitle"], font=subtitle_font, fill=BLUE)

    author_font = _font("SourceSerif4-Variable.ttf", 38)
    draw.text((margin, 468), publication["author"], font=author_font, fill=INK)
    meta_font = _font("IBMPlexMono-Regular.ttf", 17)
    draw.text((margin, 530), "A FIELD MANUAL FOR FOUNDERS", font=meta_font, fill=TRACE)

    # Triple red rule, echoing .hero::after.
    rule_right = WIDTH - margin
    rule_left = rule_right - 360
    for offset in (0, 13, 26):
        draw.line((rule_left, 510 + offset, rule_right, 510 + offset), fill=RED, width=2)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)
    return output


def main() -> int:
    path = render()
    print(f"wrote {path.relative_to(ROOT)} ({WIDTH}x{HEIGHT})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
