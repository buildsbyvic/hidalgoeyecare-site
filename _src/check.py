#!/usr/bin/env python3
"""Pre-push checks: every local link resolves, images have sizes and alt text,
each page has its metadata, and nothing on the private word list is in a file
that would be committed. The word list lives in _private/ and is never committed."""
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "_private", "img-source", "__pycache__"}
SKIP_FILES = {"check.py"}
TEXT = {".html", ".css", ".js", ".json", ".py", ".xml", ".txt", ".md"}
problems = []


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.imgs, self.heads, self.meta = [], set(), [], [], {}
        self.title = ""
        self._in_title = False
        self.h1 = 0
        self.canonical = None
        self.ld = []
        self._in_ld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k) and not (tag == "link" and a.get("rel") in ("canonical", "preconnect")):
                self.refs.append(a[k])
        if tag == "img":
            self.imgs.append(a)
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            self.meta[a.get("name") or a.get("property") or a.get("http-equiv")] = a.get("content")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag == "h1":
            self.h1 += 1
        if re.fullmatch(r"h[1-6]", tag):
            self.heads.append(int(tag[1]))
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "script":
            self._in_ld = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_ld:
            self.ld.append(data)


def tracked():
    """Files git would commit: tracked, plus new files that no ignore rule covers."""
    try:
        out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.splitlines()
        files = [ROOT / line for line in out]
    except (OSError, subprocess.CalledProcessError):
        files = [p for p in ROOT.rglob("*") if not (set(p.relative_to(ROOT).parts) & SKIP_DIRS)]
    for p in files:
        if p.is_file() and p.name not in SKIP_FILES:
            yield p


def resolves(url_path):
    p = ROOT / url_path.lstrip("/")
    return p.is_file() or (p / "index.html").is_file()


parsed = {}
for f in ROOT.rglob("*.html"):
    rel = f.relative_to(ROOT)
    if set(rel.parts) & SKIP_DIRS or rel.parts[0].startswith("_"):
        continue
    pg = Page()
    html_text = f.read_text(encoding="utf-8")
    pg.feed(html_text)
    parsed[rel.as_posix()] = pg
    for leftover in ("{{", "<!--if", "<!--else", "<!--end", "data:image/"):
        if leftover in html_text:
            problems.append(f"{rel.as_posix()}: leftover {leftover!r}")

for rel, pg in parsed.items():
    base = "/" + rel
    for ref in pg.refs:
        u = urlparse(ref)
        if u.scheme or u.netloc:
            continue
        if ref == "#":
            problems.append(f"{rel}: dead link #")
            continue
        target = urlparse(urljoin(base, ref))
        if target.path != base and not resolves(target.path):
            problems.append(f"{rel}: broken {ref}")
        if u.fragment:
            key = next((k for k in parsed if "/" + k in (target.path, target.path + "index.html")), None)
            if key and u.fragment not in parsed[key].ids:
                problems.append(f"{rel}: missing anchor {ref}")
    is_stub = "refresh" in pg.meta
    if is_stub:
        if not pg.canonical:
            problems.append(f"{rel}: stub has no canonical")
        continue
    if pg.h1 != 1:
        problems.append(f"{rel}: {pg.h1} h1 tags")
    for prev, cur in zip(pg.heads, pg.heads[1:]):
        if cur > prev + 1:
            problems.append(f"{rel}: heading jumps h{prev} to h{cur}")
    for img in pg.imgs:
        if not img.get("alt"):
            problems.append(f"{rel}: img without alt {img.get('src')}")
        if not (img.get("width") and img.get("height")):
            problems.append(f"{rel}: img without size {img.get('src')}")
    for key in ("description", "og:title", "og:image", "og:url"):
        if not pg.meta.get(key):
            problems.append(f"{rel}: missing {key}")
    if rel != "404.html" and not pg.canonical:
        problems.append(f"{rel}: missing canonical")
    for block in pg.ld:
        if "rating" in json.dumps(json.loads(block)).lower():
            problems.append(f"{rel}: rating markup in JSON-LD")
    # Each page except 404.html holds one language; Spanish pages link to Spanish pages
    if rel != "404.html":
        raw = (ROOT / rel).read_text(encoding="utf-8")
        lang = "es" if rel.startswith("es/") else "en"
        other = "en" if lang == "es" else "es"
        if f'<html lang="{lang}"' not in raw:
            problems.append(f"{rel}: html lang is not {lang}")
        if f'class="{other}"' in raw or re.search(r'data-(aria|alt|title)-es=', raw):
            problems.append(f"{rel}: still holds {other} text or Spanish attributes")
        for a in re.finditer(r'<a\b[^>]*\bhref="([^"]+)"[^>]*>', raw):
            ref, tag = a.group(1), a.group(0)
            if 'id="langBtn"' in tag or re.match(r"(https?:|tel:|mailto:|#)", ref) or "assets/" in ref:
                continue
            path = urlparse(urljoin("/" + rel, ref)).path
            if (lang == "es") != path.startswith("/es/"):
                problems.append(f"{rel}: links to the other language: {ref}")

titles = [p.title for r, p in parsed.items() if "refresh" not in p.meta]
if len(set(titles)) != len(titles):
    problems.append("duplicate page titles")

words_file = ROOT / "_private" / "do-not-publish.txt"
words = [w for w in words_file.read_text(encoding="utf-8").splitlines() if w] if words_file.exists() else []
if not words:
    problems.append("no word list at _private/do-not-publish.txt")
for f in tracked():
    if f.suffix in TEXT:
        text = f.read_text(encoding="utf-8")
        for w in words:
            if w in text:
                problems.append(f"{f.relative_to(ROOT).as_posix()}: contains {w!r}")

print(f"{len(parsed)} HTML files checked")
print("\n".join(problems) if problems else "All clean")
sys.exit(1 if problems else 0)
