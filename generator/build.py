#!/usr/bin/env python3
"""Build the Public Notes static site.

Usage: python3 build.py SRC_DIR OUT_DIR [--email you@example.com] [--images-base https://publicnotes.org]

SRC_DIR holds the original site (index.html, democracy-100.html, posts/...).
OUT_DIR receives a complete static site ready for Vercel.
"""
import argparse, html, json, os, re, shutil, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import THEMES, QUIZZES, GLOSSARY, SYLLABUS
from parse import notes as parse_notes
from series_data import SERIES_INFO

SITE = "https://publicnotes.org"
AUTHOR = "Diljot"
PUB_DATE = datetime(2026, 11, 1, 9, 0, tzinfo=timezone.utc)
DATE_TEXT = "1 November 2026"
SERIES = "Indian Democracy in 100 Notes"

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--email", default="")
ap.add_argument("--images-base", default="")
ap.add_argument("--gsc", default="", help="Google Search Console verification token")
A = ap.parse_args()
EMAIL = A.email
IMG_BASE = A.images_base.rstrip("/")

e = lambda s: html.escape(s, quote=True)
def strip_tags(s): return html.unescape(re.sub(r"<[^>]+>", " ", s))
def words(s): return len(strip_tags(s).split())
def read_min(s): return max(1, round(words(s) / 200))
def trunc(s, n=155):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0].rstrip(",;:—-") + "…"
def mailto(subject, body=""):
    from urllib.parse import quote
    q = "subject=" + quote(subject) + (("&body=" + quote(body)) if body else "")
    return f"mailto:{EMAIL}?{q}" if EMAIL else f"/subscribe.html"

def fix_imgs(s):
    if IMG_BASE:
        s = s.replace('src="/images/', f'src="{IMG_BASE}/images/')
    return s

# ---------------------------------------------------------------- content
NOTES = parse_notes(A.src)
for n in NOTES:
    c = n["content"]
    c = re.sub(r"<p>\s*(##\s*)?Key takeaways:?\s*</p>\s*", "", c)   # stray duplicate headings
    c = c.replace("is weak.The formula", "is weak. The formula")
    c = re.sub(r"\n\s*\n", "\n", c)
    n["content"] = c
    n["slug"] = n["file"][:-5]
    n["path"] = f"/posts/democracy-100/{n['file']}"
    n["desc"] = trunc(n["first"])
    n["mins"] = read_min(c)
    n["tslug"] = THEMES[n["theme"]]["slug"]
BYNUM = {n["num"]: n for n in NOTES}
assert len(NOTES) == 100, len(NOTES)

# Newer series (UPSC 300, Current Affairs 100): same note format, own hubs and theme pages
EXTRA = {}
for sk, info in SERIES_INFO.items():
    ns = parse_notes(A.src, sk)
    for n in ns:
        n["content"] = re.sub(r"\n\s*\n", "\n", n["content"])
        n["slug"] = n["file"][:-5]
        n["path"] = f"/posts/{sk}/{n['file']}"
        n["desc"] = trunc(n["first"])
        n["mins"] = read_min(n["content"])
        n["series"] = sk
        n["tslug"] = info["themes"][n["theme"]][0]
    if len(ns) != info["count"]:
        print(f"warning: {sk} has {len(ns)} of {info['count']} notes", file=sys.stderr)
    EXTRA[sk] = ns

# posts: metadata from the old homepage cards, body from each post file
idx = open(os.path.join(A.src, "index.html"), encoding="utf-8").read()
POSTS = []
for m in re.finditer(r'<article class="card">\s*<h3><a href="(/posts/[^"]+)">(.*?)</a></h3>\s*<p class="meta">(.*?)</p>\s*<p>(.*?)</p>', idx, re.S):
    path, title, meta, excerpt = m.groups()
    kind = html.unescape(meta.split("·")[-1].strip())
    f = os.path.join(A.src, path.lstrip("/"))
    t = open(f, encoding="utf-8").read()
    b = t.split("<body>", 1)[1]
    b = re.sub(r"</body>.*", "", b, flags=re.S)
    b = re.sub(r'<p><a href="/">← All public notes</a></p>', "", b)
    mm = re.search(r'<p class="meta">(.*?)</p>', b, re.S)
    content = b[mm.end():].strip()
    if 'class="wrap"' in b:  # how-public-notes-works wraps its body in a div
        content = re.sub(r"</div>\s*$", "", content).strip()
    POSTS.append(dict(path=path, slug=os.path.basename(path)[:-5], title=html.unescape(title),
                      kind=kind, excerpt=html.unescape(excerpt), meta=html.unescape(mm.group(1)),
                      content=content, mins=read_min(content)))
assert len(POSTS) == 7, len(POSTS)
for p in POSTS:
    img = re.search(r'<img src="(/images/[^"]+)"', p["content"])
    p["image"] = img.group(1) if img else None

# ---------------------------------------------------------------- layout
NAV = [("/democracy-100.html", "100 Notes"), ("/upsc-300.html", "UPSC 300"), ("/current-affairs-100.html", "Current Affairs"),
       ("/themes.html", "Themes"), ("/upsc-syllabus-map.html", "UPSC map"),
       ("/glossary.html", "Glossary"), ("/quizzes.html", "Quizzes"), ("/subscribe.html", "Subscribe")]

def page(path, title, desc, body, *, og=None, kind="website", jsonld=None, crumbs=None, active=None, wide=False):
    url = SITE + path if path != "/index.html" else SITE + "/"
    full_title = title if title.startswith("Public Notes") else f"{title} — Public Notes"
    og_img = SITE + (og or "/assets/og/default.png")
    nav = "".join(f'<a href="{h}"{" aria-current=\"page\"" if active == h else ""}>{t}</a>' for h, t in NAV)
    ld = []
    if jsonld: ld.append(jsonld)
    if crumbs:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": nm, "item": SITE + hr} for i, (nm, hr) in enumerate(crumbs)]})
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    crumb_html = ""
    if crumbs and len(crumbs) > 1:
        crumb_html = '<nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(
            f'<a href="{hr}">{e(nm)}</a>' for nm, hr in crumbs[:-1]) + f' / <span>{e(crumbs[-1][0])}</span></nav>'
    gsc = f'<meta name="google-site-verification" content="{e(A.gsc)}">' if A.gsc else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="Public Notes">
<meta property="og:type" content="{kind}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og_img}">
<meta name="theme-color" content="#0f2440">
{gsc}
<link rel="icon" href="/assets/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="Public Notes" href="/feed.xml">
<link rel="stylesheet" href="/assets/site.css">
{ld_html}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="top-inner">
<a class="brand" href="/" aria-label="Public Notes home"><img src="/assets/logo.png" alt="Public Notes" width="168" height="56"></a>
<button class="menu-btn" aria-expanded="false" aria-controls="sitenav">Menu</button>
<nav id="sitenav" class="sitenav">{nav}</nav>
</div></header>
<main id="main" class="{'wide' if wide else 'narrow'}">
{crumb_html}
{body}
</main>
<footer class="foot"><div class="foot-inner">
<div><strong>Public Notes</strong> · a public notebook by {AUTHOR}. History, democracy and civic affairs, in plain words.</div>
<div class="foot-links"><a href="/democracy-100.html">100 Notes</a><a href="/upsc-300.html">UPSC 300</a><a href="/current-affairs-100.html">Current Affairs 100</a><a href="/themes.html">Themes</a><a href="/upsc-syllabus-map.html">UPSC map</a><a href="/glossary.html">Glossary</a><a href="/quizzes.html">Quizzes</a><a href="/subscribe.html">Get new notes</a><a href="/feed.xml">RSS</a><a href="/posts/how-public-notes-works.html">About</a></div>
<div class="small">General information, fact-checked on {DATE_TEXT}. Not legal advice. publicnotes.org</div>
</div></footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""

def share_bar(title, path):
    url = SITE + path
    from urllib.parse import quote
    t, u = quote(title), quote(url)
    return f"""<div class="share" data-title="{e(title)}" data-url="{url}">
<span class="share-label">Share this note</span>
<button class="btn share-native" type="button">Share…</button>
<button class="btn share-copy" type="button">Copy link</button>
<a class="btn" href="https://twitter.com/intent/tweet?text={t}&amp;url={u}" target="_blank" rel="noopener">X</a>
<a class="btn" href="https://www.linkedin.com/sharing/share-offsite/?url={u}" target="_blank" rel="noopener">LinkedIn</a>
<a class="btn" href="mailto:?subject={t}&amp;body={u}">Email</a>
</div>"""

def email_box(title=None):
    sub = mailto("Subscribe to Public Notes", "Please add me to the Public Notes weekly email.")
    corr = mailto(f"Correction or question: {title}" if title else "A question for Public Notes")
    corr_line = f'<p class="small">Spotted an error or want a topic covered? <a href="{corr}">Email me</a>. Corrections are credited in a monthly note.</p>' if title else ""
    return f"""<aside class="signup">
<h2>Get new notes by email</h2>
<p>One short email on Sundays: three new notes, one from the archive, and one question to think about. No newsletter service, no tracking. It comes from my own inbox.</p>
<p><a class="btn btn-primary" href="{sub}">Email me to join</a> <a class="btn" href="/feed.xml">RSS feed</a></p>
{corr_line}
</aside>"""

def note_card(n, show_theme=True):
    badge = "🖼️ Image" if n["has_img"] else "📝 Text"
    th = f' · <a href="/themes/{n["tslug"]}.html">{e(THEMES[n["theme"]]["name"])}</a>' if show_theme else ""
    return f"""<article class="card note-card" data-theme="{n['theme']}" data-search="{e((n['title'] + ' ' + n['first']).lower())}">
<p class="kicker">Note {n['num']:03d}{th}</p>
<h3><a href="{n['path']}">{e(n['title'])}</a></h3>
<p>{e(n['desc'])}</p>
<p class="meta">{n['mins']} min read · {badge}</p>
</article>"""

# ---------------------------------------------------------------- pages
pages = {}

# Notes
for i, n in enumerate(NOTES):
    th = THEMES[n["theme"]]
    prev_n = NOTES[i - 1] if i > 0 else None
    next_n = NOTES[i + 1] if i < 99 else None
    same = [x for x in NOTES if x["theme"] == n["theme"] and x["num"] != n["num"]]
    after = [x for x in same if x["num"] > n["num"]] + [x for x in same if x["num"] < n["num"]]
    related = "".join(f'<li><a href="{x["path"]}">Note {x["num"]:03d}: {e(x["title"])}</a></li>' for x in after[:3])
    nxt = (f'<a class="next-big" href="{next_n["path"]}"><span>Next note →</span><strong>Note {next_n["num"]:03d}: {e(next_n["title"])}</strong></a>'
           if next_n else '<a class="next-big" href="/quizzes.html"><span>You finished all 100 →</span><strong>Test yourself with the theme quizzes</strong></a>')
    prv = f'<a class="prev" href="{prev_n["path"]}">← Note {prev_n["num"]:03d}</a>' if prev_n else '<a class="prev" href="/democracy-100.html">← All 100 notes</a>'
    pct = n["num"]
    body = f"""<article class="note">
<p class="kicker"><a href="/democracy-100.html">{SERIES}</a> · <a href="/themes/{th['slug']}.html">{th['icon']} Theme {n['theme']}: {e(th['name'])}</a></p>
<h1>{e(n['title'])}</h1>
<p class="meta">Note {n['num']:03d} of 100 · {n['mins']} min read · Fact-checked {DATE_TEXT} · Not legal advice</p>
<div class="progress" role="img" aria-label="Note {n['num']} of 100"><span style="width:{pct}%"></span></div>
<div class="prose">
{fix_imgs(n['content'])}
</div>
{n['footer']}
{share_bar(n['title'], n['path'])}
<nav class="pager" aria-label="Series navigation">{nxt}<div class="pager-row">{prv}<a href="/democracy-100.html">All 100</a><a href="/quizzes/{th['slug']}.html">Theme quiz</a></div></nav>
<section class="related"><h2>More in {e(th['name'])}</h2><ul>{related}</ul><p><a href="/themes/{th['slug']}.html">See all 10 notes in this theme →</a></p></section>
{email_box(n['title'])}
</article>"""
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": n["title"], "description": n["desc"],
          "datePublished": PUB_DATE.isoformat(), "dateModified": PUB_DATE.isoformat(),
          "author": {"@type": "Person", "name": AUTHOR}, "publisher": {"@type": "Organization", "name": "Public Notes", "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo.png"}},
          "image": SITE + f"/assets/og/{n['slug']}.png", "mainEntityOfPage": SITE + n["path"],
          "isPartOf": {"@type": "CreativeWorkSeries", "name": SERIES, "url": SITE + "/democracy-100.html"}, "position": n["num"],
          "articleSection": th["name"]}
    pages[n["path"]] = page(n["path"], n["title"], n["desc"], body, og=f"/assets/og/{n['slug']}.png", kind="article", jsonld=ld,
                            crumbs=[("Home", "/"), (SERIES, "/democracy-100.html"), (th["name"], f"/themes/{th['slug']}.html"), (f"Note {n['num']:03d}", n["path"])])

# Posts
for i, p in enumerate(POSTS):
    nxt = POSTS[i + 1] if i + 1 < len(POSTS) else None
    nxt_html = (f'<a class="next-big" href="{nxt["path"]}"><span>Next entry →</span><strong>{e(nxt["title"])}</strong></a>' if nxt
                else f'<a class="next-big" href="/democracy-100.html"><span>Keep reading →</span><strong>{SERIES}</strong></a>')
    body = f"""<article class="note post">
<p class="kicker">{e(p['kind'])} · <a href="/">Public Notes</a></p>
<h1>{e(p['title'])}</h1>
<p class="meta">{e(p['meta'])} · {p['mins']} min read</p>
<div class="prose">
{fix_imgs(p['content'])}
</div>
{share_bar(p['title'], p['path'])}
<nav class="pager">{nxt_html}<div class="pager-row"><a href="/">← All entries</a><a href="/democracy-100.html">100 Notes</a></div></nav>
{email_box(p['title'])}
</article>"""
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": p["title"], "description": p["excerpt"],
          "datePublished": PUB_DATE.isoformat(), "author": {"@type": "Person", "name": AUTHOR},
          "image": SITE + f"/assets/og/{p['slug']}.png", "mainEntityOfPage": SITE + p["path"]}
    pages[p["path"]] = page(p["path"], p["title"], trunc(p["excerpt"]), body, og=f"/assets/og/{p['slug']}.png", kind="article", jsonld=ld,
                            crumbs=[("Home", "/"), (p["title"], p["path"])])

# Theme hubs
theme_cards = ""
for t, th in THEMES.items():
    ns = [n for n in NOTES if n["theme"] == t]
    theme_cards += f"""<a class="card theme-card" href="/themes/{th['slug']}.html"><span class="icon">{th['icon']}</span>
<span class="kicker">Theme {t} · Notes {ns[0]['num']:03d}–{ns[-1]['num']:03d}</span><strong>{e(th['name'])}</strong><span class="small">{e(trunc(th['intro'], 110))}</span></a>"""
    prev_t = THEMES.get(t - 1); next_t = THEMES.get(t + 1)
    tn = "".join(
        ([f'<a href="/themes/{prev_t["slug"]}.html">← {e(prev_t["name"])}</a>'] if prev_t else []) +
        ([f'<a href="/themes/{next_t["slug"]}.html">{e(next_t["name"])} →</a>'] if next_t else []))
    body = f"""<header class="page-head">
<p class="kicker"><a href="/democracy-100.html">{SERIES}</a> · Theme {t} of 10</p>
<h1>{th['icon']} {e(th['name'])}</h1>
<p class="lede">{e(th['intro'])}</p>
<p><a class="btn btn-primary" href="{ns[0]['path']}">Start with Note {ns[0]['num']:03d} →</a> <a class="btn" href="/quizzes/{th['slug']}.html">Take the 5-question quiz</a></p>
</header>
<ol class="theme-list">{''.join(f'<li>{note_card(n, False)}</li>' for n in ns)}</ol>
<nav class="pager-row spaced">{tn}</nav>
{email_box()}"""
    path = f"/themes/{th['slug']}.html"
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": th["name"], "description": th["intro"],
          "hasPart": [{"@type": "Article", "headline": n["title"], "url": SITE + n["path"]} for n in ns]}
    pages[path] = page(path, f"{th['name']}: 10 notes on Indian democracy", th["intro"], body, og=f"/assets/og/theme-{th['slug']}.png",
                       jsonld=ld, crumbs=[("Home", "/"), (SERIES, "/democracy-100.html"), (th["name"], path)], active="/themes.html", wide=True)

pages["/themes.html"] = page("/themes.html", "Browse the 10 themes", "Ten themes, ten notes each: the Constitution, elections, Parliament, courts, parties, media, protest, economy, foreign policy and youth.",
    f"""<header class="page-head"><h1>Browse by theme</h1><p class="lede">{SERIES} is organised into ten themes of ten notes each. Pick the one you need, or start at Theme 1 and read in order.</p></header>
<div class="theme-grid">{theme_cards}</div>""", crumbs=[("Home", "/"), ("Themes", "/themes.html")], active="/themes.html", wide=True)

# Hub
chips = '<button class="chip active" data-filter="all">All 100</button>' + "".join(
    f'<button class="chip" data-filter="{t}">{th["icon"]} {e(th["name"])}</button>' for t, th in THEMES.items())
hub_body = f"""<header class="page-head">
<p class="kicker">Public Notes · Fact-checked series</p>
<h1>{SERIES}</h1>
<p class="lede">Current affairs and civics for young readers, in 100 short notes across 10 themes. Every note ends with key takeaways, why it matters, and a question to discuss. Fact-checked on {DATE_TEXT}; disputed claims are attributed in the text.</p>
<p><a class="btn btn-primary" href="{NOTES[0]['path']}">Start at Note 001 →</a> <a class="btn" href="/upsc-syllabus-map.html">Find notes by UPSC topic</a> <a class="btn" href="/quizzes.html">Quizzes</a></p>
</header>
<h2 class="section-title">The 10 themes</h2>
<div class="theme-grid">{theme_cards}</div>
<h2 class="section-title" id="all">All 100 notes</h2>
<div class="filters"><label class="search"><span class="sr">Search notes</span><input type="search" id="note-search" placeholder="Search 100 notes, for example: collegium, MSP, Form 6"></label>
<div class="chips" role="group" aria-label="Filter by theme">{chips}</div><p class="small" id="result-count" aria-live="polite">Showing 100 notes</p></div>
<div class="grid" id="note-grid">{''.join(note_card(n) for n in NOTES)}</div>
<p class="small spaced">Moving topics such as SIR, delimitation, FCRA 2026, One Nation One Election and trade or tariffs should be re-checked at the time of reading.</p>
{email_box()}"""
pages["/democracy-100.html"] = page("/democracy-100.html", SERIES, "100 short, fact-checked notes on Indian democracy for young civil studies and UPSC readers, across 10 themes from the Constitution to youth and the future.",
    hub_body, og="/assets/og/democracy-100.png",
    jsonld={"@context": "https://schema.org", "@type": "CreativeWorkSeries", "name": SERIES, "url": SITE + "/democracy-100.html", "author": {"@type": "Person", "name": AUTHOR}},
    crumbs=[("Home", "/"), (SERIES, "/democracy-100.html")], active="/democracy-100.html", wide=True)

# Newer series: notes, theme pages, hubs
def x_card(n, info, show_theme=True):
    th = info["themes"][n["theme"]]
    tl = f' · <a href="/{n["series"]}/themes/{th[0]}.html">{e(th[1])}</a>' if show_theme else ""
    return f"""<article class="card note-card" data-theme="{n['theme']}" data-search="{e((n['title'] + ' ' + n['first'] + ' ' + th[1]).lower())}">
<p class="kicker">Note {n['num']:03d}{tl}</p>
<h3><a href="{n['path']}">{e(n['title'])}</a></h3>
<p>{e(n['desc'])}</p>
<p class="meta">{n['mins']} min read · {th[3]}</p>
</article>"""

X_THEME_CARDS = {}
for sk, info in SERIES_INFO.items():
    ns_all = EXTRA[sk]
    if not ns_all: continue
    total = len(ns_all); name = info["name"]; hub = info["hub"]; ntheme = len(info["themes"])
    def tpath(t): return f"/{sk}/themes/{info['themes'][t][0]}.html"
    for i, n in enumerate(ns_all):
        th = info["themes"][n["theme"]]
        prev_n = ns_all[i - 1] if i > 0 else None
        next_n = ns_all[i + 1] if i + 1 < total else None
        same = [x for x in ns_all if x["theme"] == n["theme"] and x["num"] != n["num"]]
        after = [x for x in same if x["num"] > n["num"]] + [x for x in same if x["num"] < n["num"]]
        related = "".join(f'<li><a href="{x["path"]}">Note {x["num"]:03d}: {e(x["title"])}</a></li>' for x in after[:3])
        nxt = (f'<a class="next-big" href="{next_n["path"]}"><span>Next note →</span><strong>Note {next_n["num"]:03d}: {e(next_n["title"])}</strong></a>'
               if next_n else f'<a class="next-big" href="{hub}"><span>You reached the end →</span><strong>Back to the {e(name)} hub</strong></a>')
        prv = f'<a class="prev" href="{prev_n["path"]}">← Note {prev_n["num"]:03d}</a>' if prev_n else f'<a class="prev" href="{hub}">← All {total} notes</a>'
        pct = round(100 * n["num"] / info["count"])
        body = f"""<article class="note">
<p class="kicker"><a href="{hub}">{e(name)}</a> · <a href="{tpath(n['theme'])}">{th[2]} Theme {n['theme']}: {e(th[1])}</a> · {th[3]}</p>
<h1>{e(n['title'])}</h1>
<p class="meta">Note {n['num']:03d} of {info['count']} · {n['mins']} min read · Fact-checked 2 November 2026</p>
<div class="progress" role="img" aria-label="Note {n['num']} of {info['count']}"><span style="width:{pct}%"></span></div>
<div class="prose">
{n['content']}
</div>
{n['footer']}
{share_bar(n['title'], n['path'])}
<nav class="pager" aria-label="Series navigation">{nxt}<div class="pager-row">{prv}<a href="{hub}">All {total}</a><a href="{tpath(n['theme'])}">This theme</a></div></nav>
<section class="related"><h2>More in {e(th[1])}</h2><ul>{related}</ul><p><a href="{tpath(n['theme'])}">See all notes in this theme →</a></p></section>
{email_box(n['title'])}
</article>"""
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": n["title"], "description": n["desc"],
              "datePublished": PUB_DATE.isoformat(), "dateModified": PUB_DATE.isoformat(),
              "author": {"@type": "Person", "name": AUTHOR}, "publisher": {"@type": "Organization", "name": "Public Notes", "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo.png"}},
              "image": SITE + f"/assets/og/{sk}-{th[0]}.png", "mainEntityOfPage": SITE + n["path"],
              "isPartOf": {"@type": "CreativeWorkSeries", "name": info["long"], "url": SITE + hub}, "position": n["num"],
              "articleSection": th[1]}
        pages[n["path"]] = page(n["path"], n["title"], n["desc"], body, og=f"/assets/og/{sk}-{th[0]}.png", kind="article", jsonld=ld,
                                crumbs=[("Home", "/"), (name, hub), (th[1], tpath(n["theme"])), (f"Note {n['num']:03d}", n["path"])])
    cards = ""
    for t, th in info["themes"].items():
        ns = [n for n in ns_all if n["theme"] == t]
        if not ns: continue
        cards += f"""<a class="card theme-card" href="{tpath(t)}"><span class="icon">{th[2]}</span>
<span class="kicker">Theme {t} · {th[3]} · Notes {ns[0]['num']:03d}–{ns[-1]['num']:03d}</span><strong>{e(th[1])}</strong><span class="small">{e(trunc(th[4], 110))}</span></a>"""
        prev_t = info["themes"].get(t - 1); next_t = info["themes"].get(t + 1)
        tn = "".join(([f'<a href="{tpath(t - 1)}">← {e(prev_t[1])}</a>'] if prev_t else []) +
                     ([f'<a href="{tpath(t + 1)}">{e(next_t[1])} →</a>'] if next_t else []))
        body = f"""<header class="page-head">
<p class="kicker"><a href="{hub}">{e(name)}</a> · Theme {t} of {ntheme} · {th[3]}</p>
<h1>{th[2]} {e(th[1])}</h1>
<p class="lede">{e(th[4])}</p>
<p><a class="btn btn-primary" href="{ns[0]['path']}">Start with Note {ns[0]['num']:03d} →</a> <a class="btn" href="{hub}">All {total} notes</a></p>
</header>
<ol class="theme-list">{''.join(f'<li>{x_card(n, info, False)}</li>' for n in ns)}</ol>
<nav class="pager-row spaced">{tn}</nav>
{email_box()}"""
        ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": th[1], "description": th[4],
              "hasPart": [{"@type": "Article", "headline": n["title"], "url": SITE + n["path"]} for n in ns]}
        pages[tpath(t)] = page(tpath(t), f"{th[1]}: {len(ns)} notes · {name}", th[4], body, og=f"/assets/og/{sk}-{th[0]}.png",
                               jsonld=ld, crumbs=[("Home", "/"), (name, hub), (th[1], tpath(t))], active=hub, wide=True)
    X_THEME_CARDS[sk] = cards
    chips = f'<button class="chip active" data-filter="all">All {total}</button>' + "".join(
        f'<button class="chip" data-filter="{t}">{th[2]} {e(th[1])}</button>' for t, th in info["themes"].items())
    ex = "for example: Harappan, monsoon, repo rate, GST" if sk == "upsc-300" else "for example: Budget, BRICS, SIR, T20"
    body = f"""<header class="page-head">
<p class="kicker">Public Notes · {e(info['kicker'])}</p>
<h1>{e(info['long'])}</h1>
<p class="lede">{e(info['lede'])}</p>
<p><a class="btn btn-primary" href="{ns_all[0]['path']}">Start at Note 001 →</a> <a class="btn" href="/upsc-syllabus-map.html">UPSC syllabus map</a> <a class="btn" href="/democracy-100.html">Indian Democracy in 100 Notes</a></p>
</header>
<h2 class="section-title">The {ntheme} themes</h2>
<div class="theme-grid">{cards}</div>
<h2 class="section-title" id="all">All {total} notes</h2>
<div class="filters"><label class="search"><span class="sr">Search notes</span><input type="search" id="note-search" placeholder="Search {total} notes, {ex}"></label>
<div class="chips" role="group" aria-label="Filter by theme">{chips}</div><p class="small" id="result-count" aria-live="polite">Showing {total} notes</p></div>
<div class="grid" id="note-grid">{''.join(x_card(n, info) for n in ns_all)}</div>
{email_box()}"""
    pages[hub] = page(hub, info["long"], trunc(info["lede"]), body, og=f"/assets/og/{sk}.png",
                      jsonld={"@context": "https://schema.org", "@type": "CreativeWorkSeries", "name": info["long"], "url": SITE + hub, "author": {"@type": "Person", "name": AUTHOR}},
                      crumbs=[("Home", "/"), (name, hub)], active=hub, wide=True)

# Quizzes
quiz_index = ""
for t, th in THEMES.items():
    qs = QUIZZES[t]
    items = ""
    for qi, (q, opts, ans, num, expl) in enumerate(qs):
        o = "".join(f'<li><button type="button" class="opt" data-correct="{1 if k == ans else 0}">{e(op)}</button></li>' for k, op in enumerate(opts))
        nn = BYNUM[num]
        items += f"""<li class="q"><p class="q-text"><strong>Q{qi + 1}.</strong> {e(q)}</p><ul class="opts">{o}</ul>
<p class="explain" hidden>{e(expl)} <a href="{nn['path']}">Read Note {num:03d} →</a></p></li>"""
    next_t = THEMES.get(t + 1)
    nxt = f'<a class="btn" href="/quizzes/{next_t["slug"]}.html">Next quiz: {e(next_t["name"])} →</a>' if next_t else '<a class="btn" href="/quizzes.html">All quizzes</a>'
    body = f"""<header class="page-head"><p class="kicker"><a href="/quizzes.html">Quizzes</a> · Theme {t}</p>
<h1>{th['icon']} Quiz: {e(th['name'])}</h1><p class="lede">Five questions drawn from the ten notes in this theme. Tap an answer to check it; each answer links to the note that explains it.</p></header>
<ol class="quiz" data-total="{len(qs)}">{items}</ol>
<div class="quiz-score" aria-live="polite" hidden><p><strong class="score-text"></strong></p>
{share_bar('Quiz: ' + th['name'] + ' — Public Notes', f'/quizzes/{th["slug"]}.html').replace('Share this note', 'Challenge a friend')}</div>
<p class="spaced"><a class="btn btn-primary" href="/themes/{th['slug']}.html">Read the 10 notes</a> {nxt}</p>
{email_box()}"""
    path = f"/quizzes/{th['slug']}.html"
    pages[path] = page(path, f"Quiz: {th['name']}", f"Five quick questions on {th['name'].lower()} in India, with answers linked to fact-checked notes.", body,
                       og=f"/assets/og/theme-{th['slug']}.png", crumbs=[("Home", "/"), ("Quizzes", "/quizzes.html"), (th["name"], path)], active="/quizzes.html")
    quiz_index += f'<a class="card theme-card" href="{path}"><span class="icon">{th["icon"]}</span><span class="kicker">Theme {t} · 5 questions</span><strong>{e(th["name"])}</strong></a>'
pages["/quizzes.html"] = page("/quizzes.html", "Quizzes on Indian democracy", "Ten short quizzes, one per theme, to test what you know about the Constitution, elections, Parliament, courts and more.",
    f"""<header class="page-head"><h1>Quizzes</h1><p class="lede">Fifty questions in ten short quizzes, one per theme. No sign-up and no scores stored: your answers stay in your browser. Good for revision, class starters, or a quick challenge with friends.</p></header>
<div class="theme-grid">{quiz_index}</div>""", crumbs=[("Home", "/"), ("Quizzes", "/quizzes.html")], active="/quizzes.html", wide=True)

# Glossary
def note_links(nums):
    return ", ".join(f'<a href="{BYNUM[x]["path"]}">Note {x:03d}</a>' for x in nums)
gl_sorted = sorted(GLOSSARY, key=lambda g: g[0].lower())
letters = sorted({g[0][0].upper() for g in gl_sorted})
gl_items, cur = "", None
for term, defin, nums in gl_sorted:
    L = term[0].upper()
    if L != cur:
        gl_items += f'<h2 class="letter" id="letter-{L}">{L}</h2>'; cur = L
    anchor = re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")
    links = note_links(nums) if nums else '<a href="/posts/lahore-1929-purna-swaraj.html">Lahore, 1929</a>'
    gl_items += f'<div class="term" id="{anchor}" data-search="{e((term + " " + defin).lower())}"><dt>{e(term)}</dt><dd>{e(defin)} <span class="small">Read: {links}</span></dd></div>'
gl_ld = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "Public Notes glossary of Indian democracy",
         "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t, "description": d} for t, d, _ in gl_sorted]}
pages["/glossary.html"] = page("/glossary.html", "Glossary of Indian democracy terms", "Plain-language definitions of key terms in Indian polity and current affairs, from Article 324(5) and SIR to the collegium, MSP and FCRA.",
    f"""<header class="page-head"><h1>Glossary</h1><p class="lede">{len(gl_sorted)} terms that come up again and again in Indian polity, each in one or two plain sentences, with links to the notes that explain them properly.</p>
<label class="search"><span class="sr">Search the glossary</span><input type="search" id="gl-search" placeholder="Search terms"></label>
<p class="az">{' '.join(f'<a href="#letter-{L}">{L}</a>' for L in letters)}</p></header>
<dl class="glossary">{gl_items}</dl>""", jsonld=gl_ld, crumbs=[("Home", "/"), ("Glossary", "/glossary.html")], active="/glossary.html")

# UPSC map
post_by_slug = {p["slug"]: p for p in POSTS}
sy_html = ""
for paper, topics in SYLLABUS:
    rows = ""
    for topic, nums, posts in topics:
        links = [f'<a href="{BYNUM[x]["path"]}">{x:03d} · {e(BYNUM[x]["title"])}</a>' for x in nums]
        links += [f'<a href="{post_by_slug[s]["path"]}">{e(post_by_slug[s]["title"])}</a>' for s in posts]
        rows += f'<tr><th scope="row">{e(topic)}</th><td><ul>{"".join(f"<li>{l}</li>" for l in links)}</ul></td></tr>'
    sy_html += f'<h2>{e(paper)}</h2><div class="table-wrap"><table class="syllabus"><thead><tr><th>Syllabus topic</th><th>Read these notes</th></tr></thead><tbody>{rows}</tbody></table></div>'
x_rows = {}
for sk, info in SERIES_INFO.items():
    for t, th in info["themes"].items():
        ns = [n for n in EXTRA[sk] if n["theme"] == t]
        if not ns: continue
        x_rows.setdefault(th[3], []).append(f'<tr><th scope="row"><a href="/{sk}/themes/{th[0]}.html">{th[2]} {e(th[1])}</a><br><span class="small">{e(info["name"])}</span></th><td><ul>' +
            "".join(f'<li><a href="{n["path"]}">{n["num"]:03d} · {e(n["title"])}</a></li>' for n in ns) + '</ul></td></tr>')
if x_rows:
    sy_html += '<h2 id="upsc-300">UPSC 300 and Current Affairs 100, by paper</h2>'
    for paper in sorted(x_rows):
        sy_html += f'<h3>{e(paper)}</h3><div class="table-wrap"><table class="syllabus"><thead><tr><th>Theme</th><th>Notes</th></tr></thead><tbody>{"".join(x_rows[paper])}</tbody></table></div>'
pages["/upsc-syllabus-map.html"] = page("/upsc-syllabus-map.html", "UPSC syllabus map: Indian polity and current affairs notes", "Find Public Notes by UPSC Civil Services Mains syllabus topic: GS I history and society, GS II polity and IR, GS III economy, environment and security.",
    f"""<header class="page-head"><h1>UPSC syllabus map</h1><p class="lede">Every note mapped to the UPSC Civil Services Mains General Studies syllabus, so you can revise by topic. The topic wording is paraphrased; always check the current official syllabus. Notes are background reading, not a substitute for standard texts.</p></header>
{sy_html}
<p class="spaced"><a class="btn btn-primary" href="/posts/democracy-100/098-how-to-become-civil-servant.html">How the UPSC exam works (Note 098) →</a></p>
{email_box()}""", crumbs=[("Home", "/"), ("UPSC syllabus map", "/upsc-syllabus-map.html")], active="/upsc-syllabus-map.html", wide=True)

# Subscribe
sub_btn = f'<a class="btn btn-primary" href="{mailto("Subscribe to Public Notes", "Please add me to the Public Notes weekly email.")}">Email me to join</a>' if EMAIL else '<span class="btn btn-primary" aria-disabled="true">Email link coming soon</span>'
pages["/subscribe.html"] = page("/subscribe.html", "Get new notes", "Follow Public Notes by email or RSS. One short email on Sundays, sent from a personal inbox, with no newsletter service and no tracking.",
    f"""<header class="page-head"><h1>Get new notes</h1><p class="lede">Two ways to follow Public Notes. Neither needs an account.</p></header>
<div class="two">
<section class="card"><h2>📬 By email</h2><p>Send one email and you are on the list. Every Sunday you get a short note: three new entries, one from the archive, and one question to think about. It is sent by hand from my own inbox, with everyone in BCC, so your address is never shared or sold. Reply "stop" at any time.</p><p>{sub_btn}</p></section>
<section class="card"><h2>📡 By RSS</h2><p>Use any feed reader (for example Feedly, Inoreader or NetNewsWire) and add this address:</p><p><code>{SITE}/feed.xml</code></p><p><a class="btn" href="/feed.xml">Open the feed</a></p></section>
</div>
<section class="card spaced"><h2>✍️ Write back</h2><p>There are no comments here, on purpose. If you spot an error, want a topic covered, or use these notes in a class, {('<a href="' + mailto("A note for Public Notes") + '">email me</a>') if EMAIL else 'email me'}. Corrections and reader questions are collected in a monthly note, credited by first name.</p></section>""",
    crumbs=[("Home", "/"), ("Get new notes", "/subscribe.html")], active="/subscribe.html")

# Home
post_cards = "".join(f"""<article class="card">
<p class="kicker">{e(p['kind'])} · {DATE_TEXT}</p>
<h3><a href="{p['path']}">{e(p['title'])}</a></h3><p>{e(p['excerpt'])}</p><p class="meta">{p['mins']} min read</p></article>""" for p in POSTS)
start_here = [1, 7, 13, 18, 33, 46, 55, 61, 81, 91]
home = f"""<section class="hero"><div class="hero-inner">
<p class="eyebrow">Public Notes · In my own words</p>
<h1>Notes on a new India, in public.</h1>
<p>Short notes, history, and analysis, posted as they are written. No login, no comments, no clutter. Just the note, and the story behind it.</p>
<div class="meta-line"><span class="pill">📖 7 entries + 500 notes in three series</span><span class="pill">🕰️ History: Lahore 1929 → Dandi 1930</span><span class="pill">⚖️ Today: the vote, the law, the debate</span></div>
</div></section>
<section class="feature"><div>
<p class="kicker">Fact-checked series</p>
<h2>{SERIES}</h2>
<p>Current affairs for young civil studies and UPSC readers: 10 themes, 100 short notes, each with key takeaways and a question to discuss.</p>
<p><a class="btn btn-primary" href="/democracy-100.html">Explore all 100 notes →</a> <a class="btn" href="/upsc-syllabus-map.html">UPSC syllabus map</a> <a class="btn" href="/quizzes.html">Try a quiz</a></p>
</div></section>
<section class="feature"><div>
<p class="kicker">Exam-ready series</p>
<h2>UPSC 300</h2>
<p>The Civil Services syllabus in 300 short notes: history, geography, society, polity, economy, science, environment, security and ethics, each with a practice question.</p>
<p><a class="btn btn-primary" href="/upsc-300.html">Explore UPSC 300 →</a></p>
</div></section>
<section class="feature"><div>
<p class="kicker">Current affairs series</p>
<h2>Current Affairs 100: India in 2026</h2>
<p>A hundred short notes on the year's laws, elections, economy, trade deals, diplomacy, science and sport, each with the sources it was checked against.</p>
<p><a class="btn btn-primary" href="/current-affairs-100.html">Explore Current Affairs 100 →</a></p>
</div></section>
<section class="purpose" aria-label="Purpose of this site">
<div><h2>What this is</h2><p>A public notebook. Short notes, in my own words, posted as they are written. No login, no comments, no clutter.</p></div>
<div><h2>What it is not</h2><p>Not a news site, not a shop, and not a social feed. Each entry stands on its own, with its own link you can share.</p></div>
<div><h2>How to read it</h2><p>Browse the entries below, open one to read it in full, and share that single link. New entries appear here first.</p></div>
</section>
<h2 class="section-title">Latest entries</h2>
<div class="grid">{post_cards}</div>
<h2 class="section-title">New here? Start with these ten</h2>
<ol class="start-list">{''.join(f'<li><a href="{BYNUM[x]["path"]}"><span>Note {x:03d}</span> {e(BYNUM[x]["title"])}</a></li>' for x in start_here)}</ol>
<h2 class="section-title">Browse by theme</h2>
<div class="theme-grid">{theme_cards}</div>
{email_box()}"""
pages["/index.html"] = page("/index.html", "Public Notes — Notes on a new India, in public", "A public notebook by Diljot: short notes on Indian history and democracy, Indian Democracy in 100 Notes, UPSC 300 and Current Affairs 100, fact-checked series for civil studies and UPSC readers.",
    home, jsonld={"@context": "https://schema.org", "@type": "WebSite", "name": "Public Notes", "url": SITE + "/", "author": {"@type": "Person", "name": AUTHOR}}, wide=True)

pages["/404.html"] = page("/404.html", "Page not found", "This page does not exist.", """<header class="page-head"><h1>That page isn't here</h1>
<p class="lede">The link may be old or mistyped. Try the <a href="/">home page</a>, the <a href="/democracy-100.html">100 Notes</a>, or the <a href="/glossary.html">glossary</a>.</p></header>""")

# ---------------------------------------------------------------- write
if os.path.exists(A.out): shutil.rmtree(A.out)
for path, h in pages.items():
    f = os.path.join(A.out, path.lstrip("/"))
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, "w", encoding="utf-8").write(h)

here = os.path.dirname(os.path.abspath(__file__))
shutil.copytree(os.path.join(here, "assets"), os.path.join(A.out, "assets"))
src_img = os.path.join(A.src, "images")
if os.path.isdir(src_img):
    shutil.copytree(src_img, os.path.join(A.out, "images"))

# RSS
items = [(p["title"], p["path"], p["excerpt"], p["kind"]) for p in POSTS] + \
        [(f"Note {n['num']:03d}: {n['title']}", n["path"], n["desc"], THEMES[n["theme"]]["name"]) for n in reversed(NOTES)] + \
        [(f"{SERIES_INFO[sk]['name']} · Note {n['num']:03d}: {n['title']}", n["path"], n["desc"], SERIES_INFO[sk]["themes"][n["theme"]][1]) for sk in EXTRA for n in reversed(EXTRA[sk])]
rfc = PUB_DATE.strftime("%a, %d %b %Y %H:%M:%S +0000")
rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Public Notes</title>
<link>{SITE}/</link>
<atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
<description>Short notes on Indian history and democracy, Indian Democracy in 100 Notes, UPSC 300 and Current Affairs 100.</description>
<language>en-in</language>
<lastBuildDate>{rfc}</lastBuildDate>
""" + "".join(f"""<item><title>{e(t)}</title><link>{SITE}{pth}</link><guid isPermaLink="true">{SITE}{pth}</guid><pubDate>{rfc}</pubDate><category>{e(c)}</category><description>{e(d)}</description></item>
""" for t, pth, d, c in items) + "</channel>\n</rss>\n"
open(os.path.join(A.out, "feed.xml"), "w", encoding="utf-8").write(rss)

# Sitemap + robots
urls = sorted(p for p in pages if p != "/404.html")
def prio(p): return "1.0" if p == "/index.html" else "0.9" if p in ("/democracy-100.html", "/upsc-300.html", "/current-affairs-100.html") else "0.8" if "/themes/" in p or p.endswith("map.html") else "0.7"
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"<url><loc>{SITE + ('/' if p == '/index.html' else p)}</loc><lastmod>{PUB_DATE.date().isoformat()}</lastmod><priority>{prio(p)}</priority></url>\n" for p in urls) + "</urlset>\n"
open(os.path.join(A.out, "sitemap.xml"), "w").write(sm)
open(os.path.join(A.out, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

vercel = {
    "cleanUrls": False, "trailingSlash": False,
    "redirects": [
        {"source": "/:path*", "has": [{"type": "host", "value": "www.publicnotes.org"}], "destination": "https://publicnotes.org/:path*", "permanent": True},
        {"source": "/feed", "destination": "/feed.xml", "permanent": True},
        {"source": "/rss", "destination": "/feed.xml", "permanent": True},
    ],
    "headers": [
        {"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=604800"}]},
        {"source": "/feed.xml", "headers": [{"key": "Content-Type", "value": "application/rss+xml; charset=utf-8"}]},
    ],
}
open(os.path.join(A.out, "vercel.json"), "w").write(json.dumps(vercel, indent=2) + "\n")
print(f"built {len(pages)} pages into {A.out}")
