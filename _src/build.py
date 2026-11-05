#!/usr/bin/env python3
"""Stamp the shared header and footer onto each page and write the static site.

Run from anywhere:  python _src/build.py
Edit _src/pages/*, _src/partials/*, _src/reviews.json, assets/css, assets/js.
The repo root is the published site, so never hand-edit the generated HTML.
Jekyll on GitHub Pages skips folders starting with "_", so _src is not served.
"""
import datetime
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
SITE = "https://hidalgoeyecare.com"
NAME = "Hidalgo Eye Care & Optical"

# Set True for the final push. While False the github.io test URL stays reachable,
# because a CNAME file makes GitHub redirect that URL to the custom domain.
WRITE_CNAME = False

PAGES = [
    dict(src="home", slug="", nav="home",
         title=f"{NAME} | Optometrist in Tampa, FL",
         title_es=f"{NAME} | Optometrista en Tampa, FL",
         desc="Eye exams, contact lenses, Optomap retinal imaging and a full optical with its own lens lab. "
              "Se habla español. W Hillsborough Ave, Tampa, FL."),
    dict(src="services", slug="services/", nav="services",
         title=f"Eye Care Services | {NAME}",
         title_es=f"Servicios de cuidado de la vista | {NAME}",
         desc="Comprehensive eye exams, contact lens fittings, Ortho-K and Optomap retinal imaging with "
              "Dr. Janet Hidalgo, O.D., in Tampa, FL. Se habla español."),
    dict(src="eyewear", slug="eyewear/", nav="eyewear",
         title=f"Eyewear & Lens Lab | {NAME}",
         title_es=f"Espejuelos y laboratorio de lentes | {NAME}",
         desc="Designer and affordable frames, with lenses cut and fit in our own lab on "
              "W Hillsborough Ave in Tampa. Se habla español."),
    dict(src="insurance", slug="insurance/", nav="insurance",
         title=f"Insurance & Appointments | {NAME}",
         title_es=f"Seguros y citas | {NAME}",
         desc="We accept most vision plans, plus Medicare and Medicaid. Call to confirm yours. Self-pay exams are $60, or $95 with Optomap. "
              "Cash, card or CareCredit. Answers to common questions."),
    dict(src="about", slug="about-us/", nav="about",
         title=f"About Us | {NAME}",
         title_es=f"Nosotros | {NAME}",
         desc="Family-owned eye care in Tampa since 2019, founded by Dr. Janet Hidalgo, O.D., and Carlos Hidalgo. "
              "Meet the doctor and the team."),
    dict(src="contact", slug="contact-us/", nav="contact",
         title=f"Contact & Location | {NAME}",
         title_es=f"Contacto y ubicación | {NAME}",
         desc="5011 W Hillsborough Ave, Suite F, Tampa, FL 33634. Call (813) 373-5873. "
              "Open Monday to Friday, 9 AM to 5 PM. Walk-ins welcome."),
]

PRIVACY_SRC = SRC / "pages" / "privacy.html"
if PRIVACY_SRC.exists():
    PAGES.append(dict(src="privacy", slug="privacy/", nav=None,
                      title=f"Notice of Privacy Practices | {NAME}",
         title_es=f"Aviso de Privacidad | {NAME}",
                      desc="Notice of Privacy Practices for Hidalgo Eye Care & Optical. "
                           "Aviso de Privacidad."))

# Old WordPress URLs and where each one lands now.
REDIRECTS = {
    "why-us/": "",
    "landing/": "",
    "google-reviews/": "",
    "hello-world/": "",
    "category/uncategorized/": "",
    "author/4dmin/": "",
    "gallery/": "about-us/",
}

LD = {
    "@context": "https://schema.org",
    "@type": "Optometrist",
    "@id": f"{SITE}/#practice",
    "name": NAME,
    "url": f"{SITE}/",
    "image": f"{SITE}/assets/img/og-image.jpg",
    "logo": f"{SITE}/assets/img/logo.png",
    "telephone": "+1-813-373-5873",
    "faxNumber": "+1-813-303-0895",
    "email": "hidalgoeyecare@gmail.com",
    "foundingDate": "2019",
    "knowsLanguage": ["en", "es"],
    "paymentAccepted": "Cash, Credit Card, CareCredit",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "5011 W Hillsborough Ave, Suite F",
        "addressLocality": "Tampa",
        "addressRegion": "FL",
        "postalCode": "33634",
        "addressCountry": "US",
    },
    "openingHoursSpecification": [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "opens": "09:00",
        "closes": "17:00",
    }],
    "sameAs": ["https://www.facebook.com/hidalgoeyecare", "https://www.instagram.com/hidalgoeyecare"],
}

# Runs before first paint, so the page never flashes the wrong language.
# Saved choice first, then the browser's language. Without JavaScript both languages show.
LANG_BOOT = (
    "<script>(function(){var h=document.documentElement,l;"
    "try{l=localStorage.getItem('lang')}catch(e){}"
    "if(l!=='en'&&l!=='es')l=(navigator.language||'').toLowerCase().indexOf('es')===0?'es':'en';"
    "h.setAttribute('data-lang',l);h.lang=l;"
    "document.title=h.getAttribute('data-title-'+l)})()</script>"
)

ARROW_L = '<path d="m15 18-6-6 6-6"/>'
ARROW_R = '<path d="m9 18 6-6-6-6"/>'


def read(p):
    return Path(p).read_text(encoding="utf-8")


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def e(s):
    return html.escape(s, quote=True)


def carousel():
    cards = []
    stars = '<span class="stars" role="img" aria-label="5 stars" data-aria-es="5 estrellas">★★★★★</span>'
    for r in json.loads(read(SRC / "reviews.json")):
        if "en" in r:  # written in Spanish: original in Spanish mode, translation in English mode
            body = (f'<blockquote class="en">{e(r["en"])}</blockquote>'
                    f'<blockquote class="es" lang="es">{e(r["text"])}</blockquote>')
            small = ('<span class="en">Google review, translated from Spanish</span>'
                     '<span class="es" lang="es">Reseña de Google</span>')
        else:  # written in English: shown as written in both modes, never machine-translated
            body = f'<blockquote lang="en">{e(r["text"])}</blockquote>'
            small = ('<span class="en">Google review</span>'
                     '<span class="es" lang="es">Reseña de Google, escrita en inglés</span>')
        cards.append(
            f'<figure class="review{" rv-es" if "en" in r else ""}">{stars}<div class="rv-body">{body}</div>'
            f'<figcaption>{e(r["name"])}<small>{small}</small></figcaption></figure>')
    svg = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>')
    return (
        '<div class="rv" data-carousel>\n'
        '      <div class="rv-track" tabindex="0" role="group" aria-label="Patient reviews. Use the arrow keys to scroll." data-aria-es="Reseñas de pacientes. Use las flechas del teclado para desplazarse.">'
        + "".join(cards) + '</div>\n'
        '      <div class="rv-nav">\n'
        f'        <button class="rv-btn" type="button" data-dir="-1" aria-label="Previous reviews" data-aria-es="Reseñas anteriores">{svg % ARROW_L}</button>\n'
        '        <div class="rv-dots" aria-hidden="true"></div>\n'
        f'        <button class="rv-btn" type="button" data-dir="1" aria-label="Next reviews" data-aria-es="Reseñas siguientes">{svg % ARROW_R}</button>\n'
        '      </div>\n'
        '    </div>')


def conditionals(text, flags):
    pattern = re.compile(r"<!--if:(\w+)-->(.*?)(?:<!--else-->(.*?))?<!--end-->", re.S)

    def pick(m):
        return m.group(2) if flags[m.group(1)] else (m.group(3) or "")
    return pattern.sub(pick, text)


def layout(page, body, root, flags, year, canonical=True):
    nav = page.get("nav")
    header = read(SRC / "partials" / "header.html")
    header = re.sub(r'data-page="(\w+)"',
                    lambda m: 'aria-current="page"' if m.group(1) == nav else "", header)
    header = header.replace('<a href', '<a href').replace(' >', '>')
    footer = read(SRC / "partials" / "footer.html")
    url = f"{SITE}/{page['slug']}"
    head = [
        '<meta charset="utf-8">',
        LANG_BOOT,
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f'<title>{e(page["title"])}</title>',
        f'<meta name="description" content="{e(page["desc"])}">',
    ]
    if canonical:
        head.append(f'<link rel="canonical" href="{url}">')
    else:
        head.append('<meta name="robots" content="noindex">')
    head += [
        '<meta name="color-scheme" content="light only">',
        '<meta name="theme-color" content="#0E76BC">',
        f'<link rel="icon" type="image/png" sizes="64x64" href="{root}assets/img/favicon-64.png">',
        f'<link rel="apple-touch-icon" href="{root}assets/img/apple-touch-180.png">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{e(NAME)}">',
        f'<meta property="og:title" content="{e(page["title"])}">',
        f'<meta property="og:description" content="{e(page["desc"])}">',
        f'<meta property="og:image" content="{SITE}/assets/img/og-image.jpg">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{e(NAME)}">',
        f'<meta property="og:url" content="{url}">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&amp;family=Open+Sans:wght@400;500;600&amp;display=swap" rel="stylesheet">',
        f'<link rel="stylesheet" href="{root}assets/css/site.css">',
    ]
    if page.get("src") in ("home", "contact"):
        head.append('<script type="application/ld+json">' + json.dumps(LD, ensure_ascii=False) + '</script>')
    head.append(f'<script src="{root}assets/js/site.js" defer></script>')

    doc = (
        f'<!DOCTYPE html>\n<html lang="en" data-title-en="{e(page["title"])}" data-title-es="{e(page["title_es"])}">\n<head>\n' + "\n".join(head) + '\n</head>\n<body>\n'
        '<a class="skip" href="#main"><span class="en">Skip to content</span><span class="es" lang="es">Ir al contenido</span></a>\n'
        + header + '\n<main id="main" tabindex="-1">\n' + body + '\n</main>\n\n' + footer + '</body>\n</html>\n'
    )
    doc = conditionals(doc, flags)
    return (doc.replace("{{root}}", root).replace("{{carousel}}", carousel())
            .replace("{{year}}", str(year)))


def stub(path, target):
    depth = path.count("/")
    rel = "../" * depth + target
    label_en, label_es = ("About Us", "Nosotros") if target == "about-us/" else ("our home page", "la página principal")
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f'<title>Page moved | {e(NAME)}</title>\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<link rel="canonical" href="{SITE}/{target}">\n'
        f'<meta http-equiv="refresh" content="0; url={rel}">\n</head>\n<body>\n'
        f'<p>This page has moved. <a href="{rel}">Go to {label_en}</a>.</p>\n'
        f'<p lang="es">Esta página se ha movido. <a href="{rel}">Ir a {label_es}</a>.</p>\n'
        '</body>\n</html>\n'
    )


def main():
    today = datetime.date.today()
    flags = {"privacy": PRIVACY_SRC.exists()}

    for page in PAGES:
        body = read(SRC / "pages" / f"{page['src']}.html")
        root = "../" * page["slug"].count("/") or "./"
        write(page["slug"] + "index.html", layout(page, body, root, flags, today.year))

    notfound = dict(src="404", slug="404.html", nav=None,
                    title=f"Page not found | {NAME}",
         title_es=f"Página no encontrada | {NAME}",
                    desc="This page could not be found. Call Hidalgo Eye Care & Optical at (813) 373-5873.")
    # 404.html is served from any depth, so it alone uses root-absolute paths.
    write("404.html", layout(notfound, read(SRC / "pages" / "404.html"), "/", flags, today.year, canonical=False))

    for path, target in REDIRECTS.items():
        write(path + "index.html", stub(path, target))

    urls = "".join(f"  <url><loc>{SITE}/{p['slug']}</loc><lastmod>{today}</lastmod></url>\n" for p in PAGES)
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

    cname = ROOT / "CNAME"
    if WRITE_CNAME:
        write("CNAME", "hidalgoeyecare.com\n")
    elif cname.exists():
        cname.unlink()

    print(f"Built {len(PAGES)} pages, 404, {len(REDIRECTS)} redirect stubs.")
    print("  privacy page: ", "ON" if flags["privacy"] else "MISSING (launch gate still open, footer link hidden)")
    print("  CNAME:        ", "written" if WRITE_CNAME else "not written (test URL stays reachable)")


if __name__ == "__main__":
    main()
