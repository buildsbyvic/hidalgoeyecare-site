#!/usr/bin/env python3
"""One-time image pipeline: _src/img-source (not committed) to assets/img (committed)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IN = ROOT / "_src" / "img-source"
OUT = ROOT / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)

PHOTOS = {
    "img-02.jpg": "hero-slit-lamp", "img-03.jpg": "optomap", "img-04.jpg": "frames-browsing",
    "img-05.jpg": "frames-clear", "img-06.jpg": "lab-lensometer", "img-07.jpg": "checkin-forms",
    "img-08.jpg": "dr-hidalgo", "img-09.jpg": "team-group", "img-10.jpg": "carlos", "img-11.jpg": "victor",
    "img-12.jpg": "evelyn", "img-13.jpg": "rachel", "img-14.jpg": "lisandra", "img-15.jpg": "giraldo",
}
for src, name in PHOTOS.items():
    Image.open(IN / src).convert("RGB").save(OUT / f"{name}.webp", quality=80, method=6)

for src, name in {"img-01.png": "logo", "img-16.png": "logo-white"}.items():
    Image.open(IN / src).save(OUT / f"{name}.webp", quality=90, method=6)
Image.open(IN / "img-01.png").save(OUT / "logo.png", optimize=True)  # schema.org logo

fav = Image.open(IN / "favicon-64.png")
fav.save(OUT / "favicon-64.png", optimize=True)
fav.save(ROOT / "favicon.ico", sizes=[(32, 32), (48, 48), (64, 64)])
Image.open(IN / "apple-touch-180.png").save(OUT / "apple-touch-180.png", optimize=True)

# Social share card, 1200x630: logo and phone on white, hero photo on the right.
INK, BRAND = (11, 46, 79), (14, 118, 188)
FONTS = Path("C:/Windows/Fonts")
card = Image.new("RGB", (1200, 630), "white")
hero = Image.open(IN / "img-02.jpg").convert("RGB")
scale = 630 / hero.height
hero = hero.resize((round(hero.width * scale), 630), Image.LANCZOS)
panel = 560
x = (hero.width - (1200 - panel)) // 2
card.paste(hero.crop((x, 0, x + (1200 - panel), 630)), (panel, 0))
logo = Image.open(IN / "img-01.png").convert("RGBA")
logo_w = panel - 110
logo = logo.resize((logo_w, round(logo.height * logo_w / logo.width)), Image.LANCZOS)
card.paste(logo, (55, 135), logo)
d = ImageDraw.Draw(card)
d.rectangle((panel - 6, 0, panel, 630), fill=BRAND)
d.text((55, 300), "Optometrist in Tampa, FL", font=ImageFont.truetype(str(FONTS / "seguisb.ttf"), 34), fill=INK)
d.text((55, 350), "Se habla español", font=ImageFont.truetype(str(FONTS / "segoeui.ttf"), 30), fill=BRAND)
d.text((55, 415), "(813) 373-5873", font=ImageFont.truetype(str(FONTS / "segoeuib.ttf"), 44), fill=BRAND)
card.save(OUT / "og-image.jpg", quality=85, optimize=True, progressive=True)

total = sum(f.stat().st_size for f in OUT.iterdir())
print(f"{len(list(OUT.iterdir()))} files, {total // 1024} KB")
