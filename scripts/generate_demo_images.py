"""Generate attractive placeholder media images for the demo.

Creates product photos and category banners that match the paths referenced
in data.json, so the seeded catalog renders with real images.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = os.path.join(BASE, "media")
PROD_DIR = os.path.join(MEDIA, "photos", "products")
CAT_DIR = os.path.join(MEDIA, "photos", "categories")
os.makedirs(PROD_DIR, exist_ok=True)
os.makedirs(CAT_DIR, exist_ok=True)


def font(size, bold=True):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(size, top, bottom, diagonal=False):
    w, h = size
    img = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(img)
    if diagonal:
        steps = w + h
        for d in range(steps):
            draw.line([(0, d), (d, 0)], fill=lerp(top, bottom, d / steps))
    else:
        for y in range(h):
            draw.line([(0, y), (w, y)], fill=lerp(top, bottom, y / h))
    return img


def add_texture(img):
    """Soft decorative circles for a modern look."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    w, h = img.size
    for (cx, cy, r, a) in [
        (w * 0.85, h * 0.2, w * 0.35, 26),
        (w * 0.1, h * 0.85, w * 0.28, 22),
        (w * 0.6, h * 0.7, w * 0.18, 18),
    ]:
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, int(a)))
    overlay = overlay.filter(ImageFilter.GaussianBlur(6))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def draw_centered(draw, box, text, fnt, fill, line_gap=8):
    x0, y0, x1, y1 = box
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= (x1 - x0) and len(trial) <= 16:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    asc, desc = fnt.getmetrics()
    lh = asc + desc + line_gap
    total = lh * len(lines)
    y = y0 + (y1 - y0 - total) / 2
    for ln in lines:
        tw = draw.textlength(ln, font=fnt)
        draw.text((x0 + (x1 - x0 - tw) / 2, y), ln, font=fnt, fill=fill)
        y += lh


# (filename, label, top color, bottom color, tag)
PRODUCTS = [
    ("Headphones.jpeg", "Headphones", (99, 102, 241), (29, 27, 86), "AUDIO"),
    ("Imagen_pegada.png", "Camisa Moderna", (244, 114, 182), (131, 24, 67), "MODA"),
    ("Imagen_pegada_2.png", "Computadora Gamer", (16, 185, 129), (6, 78, 59), "GAMING"),
    ("Imagen_pegada_3.png", "Airpods", (56, 189, 248), (12, 74, 110), "AUDIO"),
    ("Imagen_pegada_4.png", "Macbook Pro", (148, 163, 184), (30, 41, 59), "LAPTOP"),
    ("Imagen_pegada_5.png", "Camisa Primavera", (251, 191, 36), (146, 64, 14), "MODA"),
    ("Imagen_pegada_6.png", "Mouse Gamer", (239, 68, 68), (127, 29, 29), "GAMING"),
    ("Imagen_pegada_7.png", "Monitor MSI", (168, 85, 247), (59, 7, 100), "PANTALLA"),
    ("Imagen_pegada_8.png", "Silla Gamer", (45, 212, 191), (19, 78, 74), "OFICINA"),
    ("Imagen_pegada_9.png", "Equipo de Sonido", (250, 204, 21), (113, 63, 18), "AUDIO"),
    ("Imagen_pegada_10.png", "Ipad Pro", (96, 165, 250), (30, 58, 138), "TABLET"),
]

CATEGORIES = [
    ("computadoras.jpeg", "Computadoras", (37, 99, 235), (15, 23, 42)),
    ("ropa.verano.jpeg", "Ropa de Verano", (236, 72, 153), (76, 5, 25)),
    ("equipos.musica.jpeg", "Musica y Media", (139, 92, 246), (30, 27, 75)),
    ("muebles.oficina.jpeg", "Muebles Oficina", (20, 184, 166), (12, 74, 70)),
    ("Gadgets.jpeg", "Accesorios Tech", (249, 115, 22), (67, 20, 7)),
]


def build_product(fn, label, top, bottom, tag):
    size = (800, 800)
    img = add_texture(gradient(size, top, bottom, diagonal=True))
    draw = ImageDraw.Draw(img)
    # framed card
    draw.rounded_rectangle([60, 60, 740, 740], radius=40, outline=(255, 255, 255), width=4)
    # tag chip
    chip_font = font(26)
    tw = draw.textlength(tag, font=chip_font)
    draw.rounded_rectangle([100, 100, 100 + tw + 48, 158], radius=24, fill=(255, 255, 255))
    draw.text((124, 112), tag, font=chip_font, fill=bottom)
    # product name
    draw_centered(draw, (90, 300, 710, 560), label, font(72), (255, 255, 255))
    # footer brand
    bf = font(30, bold=False)
    brand = "MERARI STORE"
    draw.text((400 - draw.textlength(brand, font=bf) / 2, 660), brand, font=bf,
              fill=(255, 255, 255))
    path = os.path.join(PROD_DIR, fn)
    if fn.lower().endswith(".jpeg") or fn.lower().endswith(".jpg"):
        img.save(path, "JPEG", quality=90)
    else:
        img.save(path, "PNG")
    return path


def build_category(fn, label, top, bottom):
    size = (1200, 600)
    img = add_texture(gradient(size, top, bottom, diagonal=True))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 520, 1200, 600], fill=(0, 0, 0))
    draw_centered(draw, (80, 120, 1120, 440), label, font(96), (255, 255, 255))
    sf = font(34, bold=False)
    sub = "Descubri lo mejor en " + label
    draw.text((600 - draw.textlength(sub, font=sf) / 2, 540), sub, font=sf,
              fill=(255, 255, 255))
    path = os.path.join(CAT_DIR, fn)
    img.save(path, "JPEG", quality=90)
    return path


if __name__ == "__main__":
    for p in PRODUCTS:
        print("product:", build_product(*p))
    for c in CATEGORIES:
        print("category:", build_category(*c))
    print("Done. %d products, %d categories." % (len(PRODUCTS), len(CATEGORIES)))
