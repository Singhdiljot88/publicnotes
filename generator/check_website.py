"""Check imported content, generated page structure and internal link targets."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json

root=Path(__file__).resolve().parents[1]
site=root/'site'
notes=json.loads((root/'generator/library-notes.json').read_text(encoding='utf-8'))
assert len(notes)==400
assert sum(n['series']=='upsc' for n in notes)==300
assert sum(n['series']=='current-affairs' for n in notes)==100
assert len({n['path'] for n in notes})==400
assert all(n['paragraphs'] and n['takeaways'] and n['question'] for n in notes)

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.ids=[];self.h1=0;self.main=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if d.get('id'):self.ids.append(d['id'])
        if tag=='h1':self.h1+=1
        if tag=='main':self.main+=1
        u=d.get('href') if tag in ('a','link') else d.get('src')
        if u and u.startswith('/') and not u.startswith('//'):self.links.append(u)

pages={}
for file in site.rglob('*.html'):
    parsed=Page();parsed.feed(file.read_text(encoding='utf-8'))
    assert parsed.h1==1,(file,parsed.h1)
    assert parsed.main==1,(file,parsed.main)
    assert len(set(parsed.ids))==len(parsed.ids),(file,'duplicate IDs')
    pages[file.relative_to(site).as_posix()]=parsed
bad=[]
for name,page in pages.items():
    for link in page.links:
        url=urlsplit(link);target=unquote(url.path).lstrip('/') or 'index.html'
        if not (site/target).exists():bad.append((name,link))
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            bad.append((name,link,'missing fragment'))
assert not bad,bad[:25]
assert not any((site/'digests').glob('*')) if (site/'digests').exists() else True
print(f'PASS: {len(notes)} imported notes; {len(pages)} pages with one heading and main; all internal paths and cross-page fragments exist; no magazine published.')
