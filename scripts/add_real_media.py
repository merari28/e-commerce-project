"""Replace placeholder media with real product photos, user avatars and a logo.

- Downloads real product photography (DummyJSON + Unsplash) into the exact
  media paths the catalog references, so every product shows a real photo.
- Adds extra gallery images for a few products.
- Downloads real profile photos for every user.
- Generates a clean brand logo and an empty-state illustration.

Usage:
    USE_SQLITE=1 venv/Scripts/python.exe scripts/add_real_media.py
"""
import io
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")

import django  # noqa: E402

django.setup()

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from accounts.models import Account, UserProfile  # noqa: E402
from store.models import Product, ProductGallery  # noqa: E402
from category.models import Category  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = os.path.join(BASE, "media")
PROD_DIR = os.path.join(MEDIA, "photos", "products")
CAT_DIR = os.path.join(MEDIA, "photos", "categories")
PROFILE_DIR = os.path.join(MEDIA, "userprofile")
STATIC_IMG = os.path.join(BASE, "static", "images")
for d in (PROD_DIR, CAT_DIR, PROFILE_DIR, STATIC_IMG):
    os.makedirs(d, exist_ok=True)

DJ = "https://cdn.dummyjson.com/product-images"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()


def to_square(data, size=900, bg=(255, 255, 255)):
    """Contain-fit the image onto a clean white square."""
    img = Image.open(io.BytesIO(data)).convert("RGBA")
    img.thumbnail((size, size), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), bg + (255,))
    canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2), img)
    return canvas.convert("RGB")


def save_product_image(data, filename):
    img = to_square(data)
    path = os.path.join(PROD_DIR, filename)
    if filename.lower().endswith((".jpeg", ".jpg")):
        img.save(path, "JPEG", quality=90)
    else:
        img.save(path, "PNG")
    return path


def font(size, bold=True):
    for c in (
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ):
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


# product_name -> main image URL
PRODUCT_IMAGES = {
    "Headphones": f"{DJ}/mobile-accessories/apple-airpods-max-silver/1.webp",
    "Camisa moderna": f"{DJ}/mens-shirts/man-short-sleeve-shirt/1.webp",
    "Computadora Gamer": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=900&h=900&fit=crop&q=80",
    "Airpods": f"{DJ}/mobile-accessories/apple-airpods/1.webp",
    "Macbook Pro": f"{DJ}/laptops/apple-macbook-pro-14-inch-space-grey/1.webp",
    "Camisa Primavera": f"{DJ}/mens-shirts/man-plaid-shirt/1.webp",
    "Mouse Gamer": "https://images.unsplash.com/photo-1527814050087-3793815479db?w=900&h=900&fit=crop&q=80",
    "Monitor MSI": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=900&h=900&fit=crop&q=80",
    "Silla Gamer": f"{DJ}/furniture/knoll-saarinen-executive-conference-chair/1.webp",
    "Equipo de sonido": f"{DJ}/mobile-accessories/apple-homepod-mini-cosmic-grey/1.webp",
    "Ipad Pro": f"{DJ}/tablets/ipad-mini-2021-starlight/1.webp",
}

# product_name -> list of extra gallery image URLs
GALLERY_IMAGES = {
    "Macbook Pro": [
        f"{DJ}/laptops/apple-macbook-pro-14-inch-space-grey/2.webp",
        f"{DJ}/laptops/apple-macbook-pro-14-inch-space-grey/3.webp",
    ],
    "Ipad Pro": [
        f"{DJ}/tablets/ipad-mini-2021-starlight/2.webp",
        f"{DJ}/tablets/ipad-mini-2021-starlight/3.webp",
    ],
    "Airpods": [
        f"{DJ}/mobile-accessories/apple-airpods/2.webp",
        f"{DJ}/mobile-accessories/apple-airpods/3.webp",
    ],
    "Silla Gamer": [
        f"{DJ}/furniture/knoll-saarinen-executive-conference-chair/2.webp",
    ],
}


def do_products():
    print("Product photos:")
    for prod in Product.objects.all():
        url = PRODUCT_IMAGES.get(prod.product_name)
        if not url:
            print("  [skip]", prod.product_name)
            continue
        fname = os.path.basename(prod.images.name)
        try:
            save_product_image(fetch(url), fname)
            print(f"  [ok] {prod.product_name} -> {fname}")
        except Exception as e:
            print(f"  [ERR] {prod.product_name}: {e}")


def do_gallery():
    print("Gallery images:")
    ProductGallery.objects.all().delete()
    for prod in Product.objects.all():
        urls = GALLERY_IMAGES.get(prod.product_name)
        if not urls:
            continue
        for i, url in enumerate(urls, start=2):
            fname = f"{prod.slug}_g{i}.png"
            try:
                save_product_image(fetch(url), fname)
                ProductGallery.objects.create(
                    product=prod, image=f"photos/products/{fname}"
                )
                print(f"  [ok] {prod.product_name} gallery {fname}")
            except Exception as e:
                print(f"  [ERR] {prod.product_name} gallery: {e}")


def do_profiles():
    print("Profile photos:")
    # (gender, portrait number) per user, deterministic & distinct
    portraits = [
        ("women", 65), ("men", 32), ("men", 11), ("men", 75), ("women", 44),
        ("women", 21), ("men", 53), ("women", 9), ("men", 4), ("women", 33),
    ]
    for idx, acc in enumerate(Account.objects.all().order_by("id")):
        gender, num = portraits[idx % len(portraits)]
        url = f"https://randomuser.me/api/portraits/{gender}/{num}.jpg"
        fname = f"{acc.username}.jpg"
        try:
            img = to_square(fetch(url), size=400)
            img.save(os.path.join(PROFILE_DIR, fname), "JPEG", quality=90)
            profile, _ = UserProfile.objects.get_or_create(user=acc)
            profile.profile_picture = f"userprofile/{fname}"
            if not profile.city:
                profile.city = "Asuncion"
                profile.state = "Central"
                profile.country = "Paraguay"
                profile.address_line_1 = "Avda. Espana 1234"
            profile.save()
            print(f"  [ok] {acc.email} -> {fname}")
        except Exception as e:
            print(f"  [ERR] {acc.email}: {e}")


def do_categories():
    print("Category images:")
    cat_map = {
        "computadoras": "Macbook Pro",
        "ropa-de-verano": "Camisa moderna",
        "musica-y-media": "Equipo de sonido",
        "muebles-para-oficina": "Silla Gamer",
        "accesorios-tech": "Headphones",
    }
    for cat in Category.objects.all():
        src_name = cat_map.get(cat.slug)
        url = PRODUCT_IMAGES.get(src_name)
        if not url or not cat.cat_image:
            continue
        fname = os.path.basename(cat.cat_image.name)
        try:
            img = to_square(fetch(url), size=600)
            path = os.path.join(CAT_DIR, fname)
            img.save(path, "JPEG", quality=88)
            print(f"  [ok] {cat.category_name} -> {fname}")
        except Exception as e:
            print(f"  [ERR] {cat.category_name}: {e}")


def make_logo():
    """Horizontal brand logo: rounded monogram + wordmark."""
    w, h = 520, 140
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # monogram tile
    d.rounded_rectangle([10, 20, 110, 120], radius=24, fill=(13, 110, 253))
    kf = font(64)
    d.text((38, 30), "K", font=kf, fill=(255, 255, 255))
    # wordmark
    wf = font(52)
    d.text((128, 38), "Kcer", font=wf, fill=(17, 24, 39))
    kw = d.textlength("Kcer", font=wf)
    d.text((128 + kw, 38), "Black", font=wf, fill=(13, 110, 253))
    img.save(os.path.join(STATIC_IMG, "logo.png"), "PNG")
    print("  [ok] static/images/logo.png")


def make_empty_cart():
    size = 240
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([20, 20, 220, 220], fill=(241, 245, 249))
    # simple cart glyph
    d.line([(70, 80), (90, 80), (110, 150), (175, 150)], fill=(100, 116, 139), width=8, joint="curve")
    d.line([(90, 80), (185, 80), (172, 150)], fill=(100, 116, 139), width=8, joint="curve")
    d.ellipse([112, 165, 132, 185], outline=(100, 116, 139), width=7)
    d.ellipse([158, 165, 178, 185], outline=(100, 116, 139), width=7)
    img.save(os.path.join(STATIC_IMG, "empty-cart.png"), "PNG")
    print("  [ok] static/images/empty-cart.png")


if __name__ == "__main__":
    do_products()
    do_gallery()
    do_profiles()
    do_categories()
    print("Brand assets:")
    make_logo()
    make_empty_cart()
    print("Done.")
