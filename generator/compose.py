"""Turn compact drafts into note HTML files.
Draft format:
  # THEME n
  ## slug | Title
  paragraph (blank-line separated)
  - takeaway
  W: why it matters
  Q: question
  S: Source name | https://url
Usage (from generator/): python3 compose.py upsc-300 drafts/u*.txt  |  python3 compose.py current-affairs-100 drafts/c*.txt
Generic: compose.py SERIES draft1.txt [draft2.txt ...]   (numbers assigned in order across files)
"""
import sys, os, re, html, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from series_data import SERIES_INFO
series = sys.argv[1]; info = SERIES_INFO[series]
DATE = "2 November 2026"
out = os.path.join(HERE, 'src', 'posts', series)
os.makedirs(out, exist_ok=True)
for f in glob.glob(out + '/*.html'): os.remove(f)
e = lambda s: html.escape(s, quote=False)
def inline(s):
    s = e(s)
    return re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
notes = []; theme = None
for fn in sorted(sys.argv[2:]):
    cur = None
    for raw in open(fn, encoding='utf-8').read().split('\n'):
        line = raw.strip()
        if line.startswith('# THEME'):
            theme = int(line.split()[2]); continue
        if line.startswith('## '):
            slug, title = [x.strip() for x in line[3:].split('|', 1)]
            cur = dict(theme=theme, slug=slug, title=title, paras=[], tk=[], why='', q='', src=[], buf=[])
            notes.append(cur); continue
        if cur is None: continue
        def flush():
            if cur['buf']: cur['paras'].append(' '.join(cur['buf'])); cur['buf'] = []
        if not line: flush(); continue
        if line.startswith('- '): flush(); cur['tk'].append(line[2:])
        elif line.startswith('W:'): flush(); cur['why'] = line[2:].strip()
        elif line.startswith('Q:'): flush(); cur['q'] = line[2:].strip()
        elif line.startswith('S:'): flush(); n_, u_ = [x.strip() for x in line[2:].split('|', 1)]; cur['src'].append((n_, u_))
        else: cur['buf'].append(line)
    if cur and cur['buf']: cur['paras'].append(' '.join(cur['buf']))
errs = []
slugs = set()
for i, n in enumerate(notes, 1):
    th = info['themes'][n['theme']]
    if n['slug'] in slugs: errs.append(f'dup slug {n["slug"]}')
    slugs.add(n['slug'])
    if len(n['tk']) < 3 or not n['why'] or not n['q'] or len(n['paras']) < 2: errs.append(f'{i} {n["slug"]} incomplete')
    if series == 'current-affairs-100' and len(n['src']) < 1: errs.append(f'{i} {n["slug"]} no sources')
    body = ''.join(f'<p>{inline(p)}</p>' for p in n['paras'])
    tk = ''.join(f'<li>{inline(t)}</li>' for t in n['tk'])
    src = ''
    if n['src']:
        src = '<div class="sources"><h2>Sources checked</h2><ul>' + ''.join(f'<li><a href="{html.escape(u)}" rel="noopener">{e(nm)}</a></li>' for nm, u in n['src']) + '</ul></div>'
    foot = ('Fact-checked copy, ' + DATE + '. Facts were checked against the sources listed; moving stories should be re-checked at the time of reading.') if n['src'] else \
           ('Fact-checked copy, ' + DATE + '. Standard facts are checked against official and textbook sources; always confirm against the current official syllabus and standard texts.')
    doc = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(n['title'])} — {e(info['name'])}</title></head><body>
<p class="nav"><a href="/">← Public Notes</a> · <a href="{info['hub']}">← {e(info['name'])} hub</a></p>
<h1>{e(n['title'])}</h1>
<p class="meta">Note {i:03d} · Theme {n['theme']}: {e(th[1])} · Fact-checked {DATE}</p>
{body}
<div class="takeaways"><h2>Key takeaways</h2><ul>{tk}</ul>
<p><strong>{info['why_label']}:</strong> {inline(n['why'])}</p>
<p><strong>{info['q_label']}:</strong> {inline(n['q'])}</p></div>
{src}
<p><em>{foot}</em></p>
</body></html>
'''
    open(f'{out}/{i:03d}-{n["slug"]}.html', 'w', encoding='utf-8').write(doc)
from collections import Counter
c = Counter(n['theme'] for n in notes)
print(len(notes), 'notes;', dict(c))
words = [len(' '.join(n['paras']).split()) for n in notes]
if words: print('words/note min', min(words), 'avg', sum(words)//len(words))
print('\n'.join(errs) or 'no errors')
