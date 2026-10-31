#!/usr/bin/env python3
import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
BRAND = json.loads((ROOT / "content" / "brand.json").read_text(encoding="utf-8"))
POSTS = json.loads((ROOT / "content" / "posts.json").read_text(encoding="utf-8"))
REELS = json.loads((ROOT / "content" / "reels.json").read_text(encoding="utf-8"))
MONTHS = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")


def esc(value):
    return html.escape(str(value), quote=True)


def date_label(value):
    date = datetime.strptime(value, "%Y-%m-%d")
    return f"{date.day} {MONTHS[date.month - 1]} {date.year}"


def post_markup(post):
    return f"""<article class="article" id="{esc(post['id'])}">
      <div class="article-meta"><span>{esc(post['category'])}</span><span>{post['readMinutes']} min</span></div>
      <h3>{esc(post['title'])}</h3>
      <p class="excerpt">{esc(post['excerpt'])}</p>
      <a class="read-link" href="posts/{esc(post['id'])}.html">Leer la nota <span aria-hidden="true">↗</span></a>
    </article>"""


def post_page(post):
    paragraphs = "\n".join(f"<p>{esc(p)}</p>" for p in post["paragraphs"])
    url = BRAND["siteUrl"] + "posts/" + post["id"] + ".html"
    title = post["title"] + " — " + BRAND["name"]
    return f"""<!doctype html>
<html lang="es-MX">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f3efe5">
  <meta name="description" content="{esc(post['excerpt'])}">
  <link rel="canonical" href="{esc(url)}">
  <link rel="stylesheet" href="../assets/styles.css">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(post['excerpt'])}">
  <meta property="og:url" content="{esc(url)}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(post['excerpt'])}">
  <title>{esc(title)}</title>
</head>
<body>
  <a class="skip-link" href="#contenido">Saltar al contenido</a>
  <header class="shell topbar">
    <a class="brand" href="../" aria-label="{esc(BRAND['name'])}, inicio">
      <span class="brand-mark" aria-hidden="true">D/C</span><span>{esc(BRAND['name'])}</span>
    </a>
    <nav class="nav" aria-label="Navegación principal"><a href="../#notas">Todas las notas</a></nav>
  </header>
  <main class="shell post-layout" id="contenido">
    <a class="post-back" href="../#notas">← Volver a las notas</a>
    <article class="post">
      <div class="article-meta"><span>{esc(post['category'])}</span><span>{date_label(post['date'])} · {post['readMinutes']} min</span></div>
      <h1>{esc(post['title'])}</h1>
      <p class="post-excerpt">{esc(post['excerpt'])}</p>
      <div class="post-byline">Por {esc(BRAND['byline'])}</div>
      <div class="post-body">{paragraphs}</div>
    </article>
    <div class="post-end"><span>Disonancia Cognitiva</span><a href="../#notas">Seguir leyendo las notas →</a></div>
  </main>
</body>
</html>
"""


def create_social_card():
    path = SITE / "assets" / "og.png"
    image = Image.new("RGB", (1200, 630), "#171b1c")
    draw = ImageDraw.Draw(image)
    serif_path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    sans_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    serif = ImageFont.truetype(serif_path, 74)
    label = ImageFont.truetype(sans_path, 24)
    draw.line((74, 82, 1126, 82), fill="#464a46", width=2)
    draw.text((76, 110), "DISONANCIA COGNITIVA", font=label, fill="#e38366")
    draw.text((76, 210), "Ideas en", font=serif, fill="#f3efe5")
    draw.text((76, 300), "tensión.", font=serif, fill="#f3efe5")
    draw.text((78, 430), "PREGUNTAS QUE SIGUEN ABIERTAS", font=label, fill="#a6aaa3")
    draw.line((74, 548, 1126, 548), fill="#464a46", width=2)
    image.save(path, "PNG", optimize=True)


SITE.mkdir(parents=True, exist_ok=True)
assets = SITE / "assets"
assets.mkdir(parents=True, exist_ok=True)
(assets / "styles.css").write_text((ROOT / "styles.css").read_text(encoding="utf-8"), encoding="utf-8")
create_social_card()

reel_dir = SITE / "reels"
if reel_dir.exists():
    shutil.rmtree(reel_dir)
reel_dir.mkdir(parents=True)
source_reels = ROOT / "media" / "reels"
for reel in REELS:
    for suffix in (".mp4", ".jpg"):
        source = source_reels / f"{reel['id']}{suffix}"
        if source.exists():
            shutil.copy2(source, reel_dir / source.name)

post_sections = "\n".join(post_markup(post) for post in POSTS)
reel_sections = "\n".join(f"""<article class="reel">
      <video controls playsinline preload="none" poster="reels/{esc(reel['id'])}.jpg" aria-label="Video: {esc(reel['title'])}">
        <source src="reels/{esc(reel['id'])}.mp4" type="video/mp4">
        Tu navegador no puede reproducir este video.
      </video>
      <div class="reel-copy"><span>Guion {esc(reel['id'][:2])}</span><h3>{esc(reel['title'])}</h3>
      <p>{esc(reel['caption'])}</p></div>
    </article>""" for reel in REELS)
topics = " · ".join(esc(t) for t in BRAND["topics"])
site_url = esc(BRAND["siteUrl"])

page = f"""<!doctype html>
<html lang="es-MX">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f3efe5">
  <meta name="description" content="{esc(BRAND['description'])}">
  <link rel="canonical" href="{site_url}">
  <link rel="alternate" type="application/rss+xml" title="{esc(BRAND['name'])}" href="feed.xml">
  <link rel="stylesheet" href="assets/styles.css">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(BRAND['name'])} — {esc(BRAND['tagline'])}">
  <meta property="og:description" content="{esc(BRAND['description'])}">
  <meta property="og:url" content="{site_url}">
  <meta property="og:image" content="{site_url}assets/og.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(BRAND['name'])} — {esc(BRAND['tagline'])}">
  <meta name="twitter:description" content="{esc(BRAND['description'])}">
  <meta name="twitter:image" content="{site_url}assets/og.png">
  <title>{esc(BRAND['name'])} — {esc(BRAND['tagline'])}</title>
</head>
<body>
  <a class="skip-link" href="#contenido">Saltar al contenido</a>
  <header class="shell topbar">
    <a class="brand" href="#inicio" aria-label="{esc(BRAND['name'])}, inicio">
      <span class="brand-mark" aria-hidden="true">D/C</span><span>{esc(BRAND['name'])}</span>
    </a>
    <nav class="nav" aria-label="Navegación principal">
      <a href="#notas">Notas</a><a href="#videos">Videos</a><a href="#acerca">Acerca</a>
    </nav>
  </header>
  <main id="contenido">
    <section class="shell hero" id="inicio">
      <div>
        <span class="kicker">Un cuaderno personal · {topics}</span>
        <h1>Pensar también <em>es cambiar.</em></h1>
        <p class="hero-copy">{esc(BRAND['description'])}</p>
        <div class="hero-actions">
          <a class="button primary" href="#notas">Leer las notas</a>
          <a class="button" href="#videos">Ver los videos</a>
        </div>
      </div>
      <aside class="hero-note">
        <p>Una idea que nunca se pone en duda puede terminar pareciéndose demasiado a una costumbre.</p>
        <span>La pregunta antes de la respuesta</span>
      </aside>
    </section>

    <div class="shell rule"></div>
    <section class="shell" id="notas" aria-labelledby="notes-title">
      <div class="section-head">
        <div><span class="section-kicker">Notas de campo</span><h2 id="notes-title">Ideas en revisión.</h2></div>
        <p>Sobre lo que creemos, lo que hacemos y las señales que nos invitan a mirar otra vez.</p>
      </div>
      <div class="articles">{post_sections}</div>
    </section>

    <section class="reels-band" id="videos" aria-labelledby="videos-title">
      <div class="shell">
        <div class="section-head">
          <div><span class="section-kicker">En movimiento</span><h2 id="videos-title">Una pregunta, en video breve.</h2></div>
          <p>Videos breves, texto en pantalla y una idea para seguir conversando.</p>
        </div>
        <div class="reel-grid">{reel_sections}</div>
      </div>
    </section>

    <section class="shell about" id="acerca">
      <div><span class="section-kicker">Acerca del proyecto</span><h2>Un poco menos de certeza automática.</h2></div>
      <div class="about-copy">
        <p>Disonancia Cognitiva es un espacio personal para pensar en voz alta, cambiar de opinión cuando haga falta y dejar preguntas abiertas.</p>
        <p>Las notas y los videos exploran ideas de pensamiento, trabajo, tecnología y vida cotidiana. No buscan ganar una discusión: buscan hacer visible qué creemos y qué evidencia nos ayudaría a verlo distinto.</p>
        <span class="about-byline">Por {esc(BRAND['byline'])}</span>
      </div>
    </section>
  </main>
  <footer class="shell footer"><strong>Disonancia Cognitiva</strong><span>Ideas en tensión. Preguntas que siguen abiertas.</span><span>© 2026</span></footer>
</body>
</html>
"""
(SITE / "index.html").write_text(page, encoding="utf-8")

post_output = SITE / "posts"
post_output.mkdir(exist_ok=True)
for post in POSTS:
    (post_output / f"{post['id']}.html").write_text(post_page(post), encoding="utf-8")

(SITE / ".nojekyll").write_text("", encoding="utf-8")
(SITE / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + site_url + "sitemap.xml\n", encoding="utf-8")
urls = [BRAND["siteUrl"]] + [BRAND["siteUrl"] + "posts/" + post["id"] + ".html" for post in POSTS]
(SITE / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{esc(url)}</loc></url>\n" for url in urls)
    + "</urlset>\n",
    encoding="utf-8",
)

rss = ET.Element("rss", {"version": "2.0"})
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = BRAND["name"]
ET.SubElement(channel, "link").text = BRAND["siteUrl"]
ET.SubElement(channel, "description").text = BRAND["description"]
for post in POSTS:
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = post["title"]
    ET.SubElement(item, "link").text = BRAND["siteUrl"] + "posts/" + post["id"] + ".html"
    ET.SubElement(item, "guid").text = BRAND["siteUrl"] + "posts/" + post["id"] + ".html"
    ET.SubElement(item, "description").text = post["excerpt"]
    published = datetime.strptime(post["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    ET.SubElement(item, "pubDate").text = published.strftime("%a, %d %b %Y 00:00:00 GMT")
ET.indent(rss, space="  ")
(SITE / "feed.xml").write_bytes(ET.tostring(rss, encoding="utf-8", xml_declaration=True))

print(f"Sitio generado: {len(POSTS)} notas, {len(REELS)} videos.")
print(f"Salida: {SITE}")
