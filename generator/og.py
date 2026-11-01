"""Generate logo, favicons and 1200x630 share cards into assets/."""
import os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import THEMES
from parse import notes
import re, html
SRC, LOGO = sys.argv[1], sys.argv[2]
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'); os.makedirs(A+'/og', exist_ok=True)
F = '/usr/share/fonts/truetype/dejavu/'
serif_b = lambda s: ImageFont.truetype(F+'DejaVuSerif-Bold.ttf', s)
sans_b = lambda s: ImageFont.truetype(F+'DejaVuSans-Bold.ttf', s)
sans = lambda s: ImageFont.truetype(F+'DejaVuSans.ttf', s)
logo = Image.open(LOGO).convert('RGBA')
bbox = logo.getbbox(); logo = logo.crop(bbox)
h = 112; lg = logo.resize((int(logo.width*h/logo.height), h), Image.LANCZOS); lg.save(A+'/logo.png', optimize=True)
# favicon: the book mark = left ~27% of cropped logo
mark = logo.crop((0, 0, int(logo.width*0.25), logo.height)); mb = mark.getbbox(); mark = mark.crop(mb)
side = max(mark.size)+40; sq = Image.new('RGBA', (side, side), (255,253,248,255)); sq.paste(mark, ((side-mark.width)//2, (side-mark.height)//2), mark)
sq.resize((64,64), Image.LANCZOS).save(A+'/favicon.png'); sq.resize((180,180), Image.LANCZOS).save(A+'/apple-touch-icon.png')
mark_small = mark.resize((int(mark.width*90/mark.height), 90), Image.LANCZOS)

NAVY=(15,36,64); TEAL=(15,118,110); PAPER=(247,245,240); SAFF=(234,88,12); GOLD=(251,191,36)
def wrap(draw, text, font, width):
    words = text.split(); lines=[]; cur=''
    for w in words:
        t = (cur+' '+w).strip()
        if draw.textlength(t, font=font) <= width: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines
def card(path, kicker, title, foot):
    im = Image.new('RGB', (1200, 630), PAPER); d = ImageDraw.Draw(im)
    # gradient band left
    for x in range(0, 1200):
        pass
    d.rectangle([0,0,1200,14], fill=SAFF)
    d.rectangle([0,616,1200,630], fill=TEAL)
    im.paste(mark_small, (70, 70), mark_small)
    d.text((70+mark_small.width+24, 78), 'Public Notes', font=serif_b(40), fill=NAVY)
    d.text((70+mark_small.width+26, 128), 'PUBLICNOTES.ORG', font=sans(20), fill=TEAL)
    d.text((70, 215), kicker.upper(), font=sans_b(24), fill=TEAL)
    size = 60
    while True:
        f = serif_b(size); lines = wrap(d, title, f, 1060)
        if len(lines) <= 4 or size <= 38: break
        size -= 4
    lines = lines[:4]
    y = 260
    for ln in lines:
        d.text((70, y), ln, font=f, fill=NAVY); y += int(size*1.22)
    d.text((70, 560), foot, font=sans(24), fill=(91,100,114))
    im.save(path, optimize=True, quality=85)
ns = notes(SRC)
for n in ns:
    th = THEMES[n['theme']]
    card(f"{A}/og/{n['file'][:-5]}.png", f"Note {n['num']:03d} · {th['name']}", n['title'], 'Indian Democracy in 100 Notes · Fact-checked')
for t, th in THEMES.items():
    card(f"{A}/og/theme-{th['slug']}.png", f"Theme {t} of 10 · 10 notes + quiz", th['name'], 'Indian Democracy in 100 Notes')
idx = open(SRC+'/index.html').read()
for m in re.finditer(r'<article class="card">\s*<h3><a href="/posts/([^"]+)\.html">(.*?)</a></h3>\s*<p class="meta">(.*?)</p>', idx, re.S):
    card(f"{A}/og/{m.group(1)}.png", html.unescape(m.group(3)).split('·')[-1].strip()+' · Public Notes', html.unescape(m.group(2)), 'A public notebook by Diljot')
card(f"{A}/og/democracy-100.png", 'Fact-checked series', 'Indian Democracy in 100 Notes', '10 themes · 100 short notes · quizzes and UPSC map')
card(f"{A}/og/default.png", 'A public notebook by Diljot', 'Notes on a new India, in public.', 'History, democracy and civic affairs, in plain words')
from series_data import SERIES_INFO
for sk, info in SERIES_INFO.items():
    nt = len(info['themes'])
    for t, th in info['themes'].items():
        card(f"{A}/og/{sk}-{th[0]}.png", f"{info['name']} · Theme {t} of {nt} · {th[3]}", th[1], info['long'])
    card(f"{A}/og/{sk}.png", info['kicker'], info['long'], f"{nt} themes · {info['count']} short notes · fact-checked")
print('ok', len(os.listdir(A+'/og')))
