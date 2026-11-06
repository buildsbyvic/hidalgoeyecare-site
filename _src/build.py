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

# The custom domain is live, so every build keeps the CNAME file.
WRITE_CNAME = True

PAGES = [
    dict(src="home", slug="", nav="home",
         title=f"{NAME} | Optometrist in Tampa, FL",
         title_es=f"{NAME} | Optometrista en Tampa, FL",
         desc="Eye exams, contact lenses, Optomap imaging, Eterna dry eye treatment and a full optical with its own lens lab. "
              "Se habla español. W Hillsborough Ave, Tampa, FL.",
         desc_es="Exámenes de la vista, lentes de contacto, imagen Optomap, tratamiento Eterna para el ojo seco y una óptica "
                 "con laboratorio propio. Doctora bilingüe en W Hillsborough Ave, Tampa, FL."),
    dict(src="services", slug="services/", nav="services",
         title=f"Eye Care Services | {NAME}",
         title_es=f"Servicios de cuidado de la vista | {NAME}",
         desc="Comprehensive eye exams, contact lens fittings, Ortho-K, Optomap imaging and Eterna dry eye treatment with "
              "Dr. Janet Hidalgo, O.D., in Tampa, FL. Se habla español.",
         desc_es="Exámenes completos de la vista, adaptación de lentes de contacto, Orto-K, imagen Optomap y tratamiento "
                 "Eterna para el ojo seco con la Dra. Janet Hidalgo, O.D., en Tampa, FL."),
    dict(src="optomap", slug="optomap/", nav="services",
         title=f"Optomap Retinal Imaging in Tampa | {NAME}",
         title_es=f"Imagen de la retina con Optomap en Tampa | {NAME}",
         desc="Optomap captures a wide view of your retina in one quick, painless flash, and is often an alternative to dilating "
              "drops. A $35 add-on to your eye exam with Dr. Janet Hidalgo, O.D., in Tampa, FL.",
         desc_es="Optomap capta una vista amplia de la retina en un destello rápido y sin dolor, y muchas veces es una alternativa "
                 "a las gotas para dilatar. Un servicio de $35 que se añade a su examen con la Dra. Janet Hidalgo, O.D., en Tampa, FL."),
    dict(src="dry-eye", slug="dry-eye/", nav="services",
         title=f"Dry Eye Treatment in Tampa | {NAME}",
         title_es=f"Tratamiento para el ojo seco en Tampa | {NAME}",
         desc="Dry, burning or gritty eyes? Dr. Janet Hidalgo, O.D., offers in-office Eterna dry eye treatment in Tampa, FL. "
              "About $100 per session. Se habla español.",
         desc_es="¿Ojos secos, con ardor o sensación de arena? La Dra. Janet Hidalgo, O.D., ofrece el tratamiento Eterna para "
                 "el ojo seco en su oficina en Tampa, FL. Unos $100 por sesión."),
    dict(src="contact-lenses", slug="contact-lenses/", nav="services",
         title=f"Contact Lens Exams & Fittings | {NAME}",
         title_es=f"Examen y adaptación de lentes de contacto | {NAME}",
         desc="Contact lens exams and fittings with Dr. Janet Hidalgo, O.D., in Tampa, FL, for first-time wearers and anyone "
              "switching lenses. We check your insurance first. Se habla español.",
         desc_es="Exámenes y adaptación de lentes de contacto con la Dra. Janet Hidalgo, O.D., en Tampa, FL, para quienes los "
                 "usan por primera vez o quieren cambiar. Verificamos su seguro primero."),
    dict(src="ortho-k", slug="ortho-k/", nav="services",
         title=f"Ortho-K (Orthokeratology) in Tampa | {NAME}",
         title_es=f"Orto-K (ortoqueratología) en Tampa | {NAME}",
         desc="Ortho-K lenses worn overnight gently reshape the front of the eye for clear daytime vision without glasses or "
              "daytime contacts. Ask Dr. Janet Hidalgo, O.D., in Tampa, FL.",
         desc_es="Los lentes de Orto-K se usan al dormir y moldean suavemente la parte frontal del ojo para ver bien de día sin "
                 "espejuelos ni lentes de contacto. Consulte con la Dra. Janet Hidalgo, O.D., en Tampa, FL."),
    dict(src="eyewear", slug="eyewear/", nav="eyewear",
         title=f"Eyewear & Lens Lab | {NAME}",
         title_es=f"Espejuelos y laboratorio de lentes | {NAME}",
         desc="Designer and affordable frames, with lenses cut and fit in our own lab on "
              "W Hillsborough Ave in Tampa. Se habla español.",
         desc_es="Monturas de marca y económicas, con lentes cortados y montados en nuestro propio laboratorio "
                 "en W Hillsborough Ave, Tampa."),
    dict(src="insurance", slug="insurance/", nav="insurance",
         title=f"Insurance & Appointments | {NAME}",
         title_es=f"Seguros y citas | {NAME}",
         desc="We accept most vision plans, plus Medicare and Medicaid. Call to confirm yours. Self-pay exams are $60, or $95 with Optomap. "
              "Cash, card or CareCredit. Answers to common questions.",
         desc_es="Aceptamos la mayoría de los planes de visión, además de Medicare y Medicaid. Llame para confirmar el suyo. "
                 "Examen sin seguro: $60, o $95 con Optomap. Efectivo, tarjeta o CareCredit."),
    dict(src="about", slug="about-us/", nav="about",
         title=f"About Us | {NAME}",
         title_es=f"Nosotros | {NAME}",
         desc="Family-owned eye care in Tampa since 2019, founded by Dr. Janet Hidalgo, O.D., and Carlos Hidalgo. "
              "Meet the doctor and the team.",
         desc_es="Cuidado de la vista familiar en Tampa desde 2019, fundado por la Dra. Janet Hidalgo, O.D., y Carlos Hidalgo. "
                 "Conozca a la doctora y al equipo."),
    dict(src="contact", slug="contact-us/", nav="contact",
         title=f"Contact & Location | {NAME}",
         title_es=f"Contacto y ubicación | {NAME}",
         desc="5011 W Hillsborough Ave, Suite F, Tampa, FL 33634. Call (813) 373-5873. "
              "Open Monday to Friday, 9 AM to 5 PM. Walk-ins welcome.",
         desc_es="5011 W Hillsborough Ave, Suite F, Tampa, FL 33634. Llame al (813) 373-5873. "
                 "Abierto de lunes a viernes, de 9 AM a 5 PM. Aceptamos pacientes sin cita."),
]

PRIVACY_SRC = SRC / "pages" / "privacy.html"
if PRIVACY_SRC.exists():
    PAGES.append(dict(src="privacy", slug="privacy/", nav=None,
                      title=f"Notice of Privacy Practices | {NAME}",
                      title_es=f"Aviso de Privacidad | {NAME}",
                      desc="Notice of Privacy Practices for Hidalgo Eye Care & Optical.",
                      desc_es="Aviso de Privacidad de Hidalgo Eye Care & Optical."))

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

UMAMI_ID = "3671e0c4-16dc-490d-964d-3c58b85f0c14"

# English lives at /page/, Spanish at /es/page/. Each built page holds only its own language.
# 404.html is the one page that holds both and switches in place, because GitHub serves the
# same file for every missing address. This runs before first paint on it.
LANG_BOOT = (
    "<script>(function(){var h=document.documentElement,l;"
    "try{l=localStorage.getItem('lang')}catch(e){}"
    "if(l!=='en'&&l!=='es')l=(navigator.language||'').toLowerCase().indexOf('es')===0?'es':'en';"
    "h.setAttribute('data-lang',l);h.lang=l;"
    "document.title=h.getAttribute('data-title-'+l)})()</script>"
)

# Someone who picked a language with the button keeps it: if they land on the other
# language's page (say from a search result), send them to the matching page.
# Only an explicit choice counts, never the browser's language, so search engines see both.
PREF_BOOT = (
    "<script>(function(){var l;try{l=localStorage.getItem('lang')}catch(e){}"
    "var h=document.documentElement;if((l==='en'||l==='es')&&l!==h.lang){"
    "var a=document.querySelector('link[rel=alternate][hreflang='+l+']');"
    "if(a)location.replace(new URL(a.href).pathname+location.search+location.hash)}})()</script>"
)

DROP_TAG = re.compile(r'<(\w+)\b[^>]*?\bclass="(en|es)"[^>]*>')
LANG_ATTR = re.compile(r'\sdata-(aria|alt|title)-es="([^"]*)"')
ATTR_FOR = {"aria": "aria-label", "alt": "alt", "title": "title"}


def keep_language(doc, lang):
    """Remove every element tagged with the other language, and fill in Spanish attributes."""
    drop = "es" if lang == "en" else "en"
    out, pos = [], 0
    while True:
        m = DROP_TAG.search(doc, pos)
        if not m:
            out.append(doc[pos:])
            break
        if m.group(2) != drop:
            out.append(doc[pos:m.end()])
            pos = m.end()
            continue
        tag, depth, i = m.group(1), 1, m.end()
        pair = re.compile(rf'<(/?){tag}\b[^>]*>')
        while depth:
            n = pair.search(doc, i)
            depth += -1 if n.group(1) else 1
            i = n.end()
        out.append(doc[pos:m.start()])
        pos = i
    doc = "".join(out)

    def attrs(m):
        tag = m.group(0)
        if lang == "es":
            for kind, value in LANG_ATTR.findall(tag):
                name = ATTR_FOR[kind]
                tag = re.sub(rf'\s{name}="[^"]*"', f' {name}="{value}"', tag, count=1)
        return LANG_ATTR.sub("", tag)
    return re.sub(r'<[a-zA-Z][^>]*\sdata-(?:aria|alt|title)-es="[^"]*"[^>]*>', attrs, doc)


def page_links_to_spanish(text):
    """Point links to other pages at their /es/ copies. Assets stay shared."""
    return re.sub(r'href="\{\{root\}\}(?!assets/)', 'href="{{root}}es/', text)

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


def layout(page, body, root, flags, year, lang="en", canonical=True):
    """lang is "en" or "es" for a single-language page, or "both" for the 404 page."""
    nav = page.get("nav")
    header = read(SRC / "partials" / "header.html")
    header = re.sub(r'data-page="(\w+)"',
                    lambda m: 'aria-current="page"' if m.group(1) == nav else "", header)
    header = header.replace('<a href', '<a href').replace(' >', '>')
    footer = read(SRC / "partials" / "footer.html")
    es = lang == "es"
    title, desc = (page["title_es"], page["desc_es"]) if es else (page["title"], page["desc"])
    url_en, url_es = f"{SITE}/{page['slug']}", f"{SITE}/es/{page['slug']}"
    url = url_es if es else url_en
    head = ['<meta charset="utf-8">']
    if lang == "both":
        head.append(LANG_BOOT)
    head += [
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f'<title>{e(title)}</title>',
        f'<meta name="description" content="{e(desc)}">',
    ]
    if canonical:
        head += [
            f'<link rel="canonical" href="{url}">',
            f'<link rel="alternate" hreflang="en" href="{url_en}">',
            f'<link rel="alternate" hreflang="es" href="{url_es}">',
            f'<link rel="alternate" hreflang="x-default" href="{url_en}">',
            PREF_BOOT,
        ]
    else:
        head.append('<meta name="robots" content="noindex">')
    head += [
        '<meta name="color-scheme" content="light only">',
        '<meta name="theme-color" content="#0E76BC">',
        f'<link rel="icon" type="image/png" sizes="64x64" href="{root}assets/img/favicon-64.png">',
        f'<link rel="apple-touch-icon" href="{root}assets/img/apple-touch-180.png">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{e(NAME)}">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f'<meta property="og:locale" content="{"es_US" if es else "en_US"}">',
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
    # Privacy-friendly visit and click counts (no cookies). Only counts on the real domain, not previews.
    head.append(f'<script defer src="https://cloud.umami.is/script.js" data-website-id="{UMAMI_ID}" data-domains="hidalgoeyecare.com"></script>')

    if lang == "both":
        html_tag = f'<html lang="en" data-both data-title-en="{e(page["title"])}" data-title-es="{e(page["title_es"])}">'
        alt, alt_lang = "#", "es"
    else:
        html_tag = f'<html lang="{lang}" data-lang="{lang}">'
        alt, alt_lang = (root + page["slug"], "en") if es else (root + "es/" + page["slug"], "es")
    doc = (
        f'<!DOCTYPE html>\n{html_tag}\n<head>\n' + "\n".join(head) + '\n</head>\n<body>\n'
        '<a class="skip" href="#main"><span class="en">Skip to content</span><span class="es" lang="es">Ir al contenido</span></a>\n'
        + header + '\n<main id="main" tabindex="-1">\n' + body + '\n</main>\n\n' + footer + '</body>\n</html>\n'
    )
    doc = conditionals(doc, flags)
    if es:
        doc = page_links_to_spanish(doc)
    doc = (doc.replace("{{alt}}", alt or "./").replace("{{altlang}}", alt_lang)
           .replace("{{root}}", root).replace("{{carousel}}", carousel())
           .replace("{{year}}", str(year)))
    if lang == "both":
        # On 404.html the language control switches in place, so it is a button, not a link
        return re.sub(r'<a class="lang-btn" id="langBtn"[^>]*>(.*?)</a>',
                      r'<button class="lang-btn" id="langBtn" type="button">\1</button>', doc, flags=re.S)
    return keep_language(doc, lang)


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
        depth = page["slug"].count("/")
        write(page["slug"] + "index.html", layout(page, body, "../" * depth or "./", flags, today.year, "en"))
        write("es/" + page["slug"] + "index.html", layout(page, body, "../" * (depth + 1), flags, today.year, "es"))

    notfound = dict(src="404", slug="404.html", nav=None,
                    title=f"Page not found | {NAME}",
         title_es=f"Página no encontrada | {NAME}",
                    desc="This page could not be found. Call Hidalgo Eye Care & Optical at (813) 373-5873.")
    # 404.html is served from any depth, so it alone uses root-absolute paths.
    write("404.html", layout(notfound, read(SRC / "pages" / "404.html"), "/", flags, today.year, "both", canonical=False))

    for path, target in REDIRECTS.items():
        write(path + "index.html", stub(path, target))

    urls = []
    for p in PAGES:
        pair = {"en": f"{SITE}/{p['slug']}", "es": f"{SITE}/es/{p['slug']}"}
        links = "".join(f'<xhtml:link rel="alternate" hreflang="{k}" href="{v}"/>' for k, v in pair.items())
        for loc in pair.values():
            urls.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod>{links}</url>\n")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
          + "".join(urls) + '</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

    cname = ROOT / "CNAME"
    if WRITE_CNAME:
        write("CNAME", "hidalgoeyecare.com\n")
    elif cname.exists():
        cname.unlink()

    print(f"Built {len(PAGES)} pages in English and Spanish, 404, {len(REDIRECTS)} redirect stubs.")
    print("  privacy page: ", "ON" if flags["privacy"] else "MISSING (launch gate still open, footer link hidden)")
    print("  CNAME:        ", "written" if WRITE_CNAME else "not written (test URL stays reachable)")


if __name__ == "__main__":
    main()
