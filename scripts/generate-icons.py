#!/usr/bin/env python3
"""Generate US Elevation Map home-screen icons."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
BG = (15, 20, 25)
SURFACE = (26, 35, 50)
LAND = (58, 92, 72)
LAND_LIGHT = (88, 128, 96)
ACCENT = (61, 156, 245)
FEET = (74, 222, 128)
METERS = (245, 158, 11)

# Simplified US outline (normalized 0..1, lon/lat-ish)
US_POINTS = [
    (0.12, 0.28), (0.18, 0.18), (0.30, 0.14), (0.42, 0.12), (0.56, 0.14),
    (0.72, 0.18), (0.86, 0.24), (0.90, 0.34), (0.88, 0.48), (0.82, 0.58),
    (0.74, 0.66), (0.64, 0.72), (0.52, 0.76), (0.40, 0.78), (0.28, 0.74),
    (0.20, 0.64), (0.16, 0.52), (0.14, 0.40),
]


def scale_points(points: list[tuple[float, float]], box: tuple[int, int, int, int]) -> list[tuple[int, int]]:
    x0, y0, x1, y1 = box
    return [
        (int(x0 + (x1 - x0) * px), int(y0 + (y1 - y0) * py))
        for px, py in points
    ]


def build_icon(size: int) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), BG + (255,))
    draw = ImageDraw.Draw(canvas)

    map_box = (int(size * 0.12), int(size * 0.18), int(size * 0.88), int(size * 0.84))
    draw.rounded_rectangle(map_box, radius=size // 18, fill=SURFACE)

    us = scale_points(US_POINTS, map_box)
    draw.polygon(us, fill=LAND)
    inset = scale_points([(0.5 + (p[0] - 0.5) * 0.92, 0.5 + (p[1] - 0.5) * 0.92) for p in US_POINTS], map_box)
    draw.polygon(inset, fill=LAND_LIGHT)

    for y in range(map_box[1], map_box[3], max(10, size // 18)):
        draw.line((map_box[0] + 8, y, map_box[2] - 8, y), fill=(255, 255, 255, 10), width=1)

    pin_x = int(size * 0.58)
    pin_y = int(size * 0.46)
    pin_h = int(size * 0.18)
    draw.ellipse((pin_x - pin_h // 3, pin_y - pin_h // 3, pin_x + pin_h // 3, pin_y + pin_h // 3), fill=ACCENT)
    draw.polygon(
        [
            (pin_x, pin_y + pin_h // 2),
            (pin_x - pin_h // 4, pin_y),
            (pin_x + pin_h // 4, pin_y),
        ],
        fill=ACCENT,
    )

    badge_y = int(size * 0.78)
    draw.rounded_rectangle((int(size * 0.18), badge_y, int(size * 0.44), badge_y + int(size * 0.1)), radius=8, fill=(*FEET, 220))
    draw.rounded_rectangle((int(size * 0.56), badge_y, int(size * 0.82), badge_y + int(size * 0.1)), radius=8, fill=(*METERS, 220))

    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((pin_x - 20, pin_y - 20, pin_x + 20, pin_y + 20), fill=(*ACCENT, 40))
    canvas = Image.alpha_composite(canvas, glow.filter(ImageFilter.GaussianBlur(radius=6)))
    return canvas.convert("RGB")


def save_icons() -> None:
    icon_512 = build_icon(512)
    icon_512.save(ROOT / "icon-512.png", "PNG")
    icon_512.resize((180, 180), Image.Resampling.LANCZOS).save(ROOT / "apple-touch-icon.png", "PNG")
    print(f"Wrote icons in {ROOT}")


if __name__ == "__main__":
    save_icons()