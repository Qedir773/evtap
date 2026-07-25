"""Locally generated (non-network, non-copyrighted) placeholder photos for demo listings.

These are simple illustrated scenes (not real photographs) — used only so the
demo/showcase data has something more meaningful than a flat colour block.
"""

import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 900

# Azerbaijani text (ə, ö, ü, ş, ğ, ı, ç) needs a Unicode-capable TTF — Pillow's
# built-in bitmap default font only covers basic Latin and renders these as tofu boxes.
_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def _font(size):
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# (wall/sky colour, floor/ground colour, accent colour)
PALETTE = [
    ((235, 224, 201), (181, 136, 99), (15, 76, 58)),
    ((225, 235, 231), (191, 158, 118), (184, 134, 11)),
    ((214, 226, 219), (163, 177, 138), (45, 90, 130)),
    ((230, 220, 210), (150, 120, 100), (120, 70, 70)),
    ((210, 222, 235), (200, 190, 170), (90, 90, 140)),
    ((222, 232, 214), (170, 140, 110), (70, 130, 100)),
]

INTERIOR_LABELS = {"Salon", "Mətbəx", "Yataq otağı", "Eyvan", "Hamam otağı", "Qonaq otağı", "Zal"}
EXTERIOR_LABELS = {"Fasad", "Bağça", "Hovuz", "Ön fasad", "Giriş"}
LAND_LABELS = {"Ümumi görünüş", "Yol tərəfi", "Sahənin küncü"}
STORAGE_LABELS = {"Anbar hissəsi"}


def _label_kind(label):
    if label in LAND_LABELS:
        return "land"
    if label in EXTERIOR_LABELS:
        return "exterior"
    if label in STORAGE_LABELS:
        return "storage"
    return "interior"


def generate_placeholder_photo(label, seed_index):
    """Return a ContentFile with a simple illustrated 1200x900 landscape scene."""
    wall, floor, accent = PALETTE[seed_index % len(PALETTE)]
    kind = _label_kind(label)

    image = Image.new("RGB", (WIDTH, HEIGHT), wall)
    draw = ImageDraw.Draw(image)

    if kind == "land":
        horizon = int(HEIGHT * 0.42)
        draw.rectangle([0, 0, WIDTH, horizon], fill=(196, 222, 234))
        draw.rectangle([0, horizon, WIDTH, HEIGHT], fill=(151, 181, 111))
        draw.line([0, horizon, WIDTH, horizon], fill=(255, 255, 255), width=4)
        draw.line([WIDTH * 0.1, HEIGHT, WIDTH * 0.55, horizon + 40], fill=(210, 200, 150), width=10)
        draw.ellipse([WIDTH - 220, 50, WIDTH - 100, 170], fill=(255, 221, 130))

    elif kind == "exterior":
        horizon = int(HEIGHT * 0.55)
        draw.rectangle([0, 0, WIDTH, horizon], fill=(196, 222, 234))
        draw.ellipse([WIDTH - 210, 55, WIDTH - 90, 175], fill=(255, 221, 130))
        draw.rectangle([0, horizon, WIDTH, HEIGHT], fill=(151, 181, 111))
        hx, hy, hw, hh = WIDTH * 0.30, HEIGHT * 0.28, WIDTH * 0.40, HEIGHT * 0.30
        draw.rectangle([hx, hy + hh * 0.4, hx + hw, hy + hh], fill=accent)
        draw.polygon(
            [(hx - 30, hy + hh * 0.4), (hx + hw / 2, hy), (hx + hw + 30, hy + hh * 0.4)],
            fill=(92, 58, 48),
        )
        draw.rectangle(
            [hx + hw * 0.42, hy + hh * 0.62, hx + hw * 0.58, hy + hh], fill=(250, 245, 235)
        )
        draw.rectangle(
            [hx + hw * 0.14, hy + hh * 0.55, hx + hw * 0.30, hy + hh * 0.85],
            fill=(196, 222, 234),
            outline=(255, 255, 255),
            width=4,
        )

    elif kind == "storage":
        draw.rectangle([0, int(HEIGHT * 0.65), WIDTH, HEIGHT], fill=(120, 120, 120))
        draw.rectangle([0, 0, WIDTH, int(HEIGHT * 0.65)], fill=(200, 200, 205))
        for i in range(4):
            x = WIDTH * (0.15 + i * 0.22)
            draw.rectangle([x, HEIGHT * 0.2, x + WIDTH * 0.12, HEIGHT * 0.62], fill=accent)

    else:  # interior
        floor_top = int(HEIGHT * 0.62)
        draw.rectangle([0, floor_top, WIDTH, HEIGHT], fill=floor)
        draw.line([0, floor_top, WIDTH, floor_top], fill=(255, 255, 255), width=3)
        win_x0, win_y0 = WIDTH * 0.36, HEIGHT * 0.12
        win_x1, win_y1 = WIDTH * 0.64, HEIGHT * 0.5
        draw.rectangle([win_x0, win_y0, win_x1, win_y1], fill=(196, 222, 234), outline=(255, 255, 255), width=6)
        draw.line([(win_x0 + win_x1) / 2, win_y0, (win_x0 + win_x1) / 2, win_y1], fill=(255, 255, 255), width=6)
        draw.line([win_x0, (win_y0 + win_y1) / 2, win_x1, (win_y0 + win_y1) / 2], fill=(255, 255, 255), width=6)
        draw.rounded_rectangle(
            [WIDTH * 0.08, HEIGHT * 0.68, WIDTH * 0.35, HEIGHT * 0.85], radius=20, fill=accent
        )
        draw.rounded_rectangle(
            [WIDTH * 0.68, HEIGHT * 0.7, WIDTH * 0.9, HEIGHT * 0.82], radius=16, fill=(255, 255, 255)
        )

    bar_h = 100
    draw.rectangle([0, HEIGHT - bar_h, WIDTH, HEIGHT], fill=(0, 0, 0))
    font = _font(42)
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((WIDTH - text_w) / 2, HEIGHT - bar_h / 2 - text_h / 2 - bbox[1]),
        label,
        fill="white",
        font=font,
    )

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=88)
    return ContentFile(buffer.getvalue())
