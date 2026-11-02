"""Import Public Notes study text and build the learning website.

First import: python generator/upgrade_website.py --reference PATH_TO_DOCX
Rebuild:      python generator/upgrade_website.py

The optional reference is read only. Normal rebuilds use library-notes.json.
"""
from pathlib import Path
from xml.etree import ElementTree as ET
from urllib.parse import quote
import argparse, html, json, re, unicodedata, zipfile

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
DATA=ROOT/'generator'/'library-notes.json'
E=html.escape
parser=argparse.ArgumentParser()
parser.add_argument('--reference')
parser.add_argument('--output',default=str(SITE))
args=parser.parse_args()
SITE=Path(args.output).resolve()

def slug(text):
    text=unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower()
    return re.sub('[^a-z0-9]+','-',text).strip('-')[:85].rstrip('-')

if args.reference:
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(args.reference) as z:
        tree=ET.fromstring(z.read('word/document.xml'))
    notes=[]; series=None; theme=''; current=None; started=False
    for p in tree.findall('./w:body/w:p',ns):
        text=''.join(t.text or '' for t in p.findall('.//w:t',ns)).strip()
        style=p.find('w:pPr/w:pStyle',ns)
        sty=style.get('{'+ns['w']+'}val','') if style is not None else ''
        if sty=='Heading1' and text=='UPSC 300':
            started=True;series='upsc';continue
        if not started:continue
        if sty=='Heading1' and text=='Current Affairs 100':
            series='current-affairs';current=None;continue
        if sty=='Heading2' and text.startswith('Theme '):
            theme=re.sub(r'^Theme \d+:\s*','',text);current=None;continue
        if sty=='Heading3':
            current={'series':series,'theme':theme,'title':text,'number':None,'syllabus':'','paragraphs':[],'takeaways':[],'relevance':'','question':''}
            notes.append(current);continue
        if current is None or not text:continue
        m=re.match(r'Note (\d+)\s*[·-]',text)
        if m:current['number']=int(m.group(1));continue
        if text.startswith(('UPSC syllabus:','Syllabus topics touched')):
            current['syllabus']=text.split(':',1)[-1].strip();continue
        if sty=='Heading4' or text=='Key takeaways':continue
        if text.startswith('Why it matters for civil studies:'):
            current['relevance']=text.split(':',1)[1].strip();continue
        if text.startswith('Discussion question:'):
            current['question']=text.split(':',1)[1].strip();continue
        if text.startswith(('Suggested picture','No suitable open-source picture','←','Fact-checked copy')):continue
        if 'Source: Wikimedia Commons' in text or re.search(r'\.(jpg|png|jpeg|svg)\s*[—-]',text,re.I):continue
        if sty=='ListBullet':current['takeaways'].append(text)
        elif not text.startswith('Not published as legal advice'):current['paragraphs'].append(text)
    for n in notes:
        assert n['number'] is not None and n['paragraphs'],n['title']
        n['path']=f'/study/{n["series"]}/{n["number"]:03}-{slug(n["title"])}.html'
    assert len(notes)==400,len(notes)
    assert len([n for n in notes if n['series']=='upsc'])==300
    assert len(set(n['path'] for n in notes))==400
    DATA.write_text(json.dumps(notes,ensure_ascii=False,indent=2),encoding='utf-8')
else:
    notes=json.loads(DATA.read_text(encoding='utf-8'))

base=(SITE/'index.html').read_text(encoding='utf-8')
head=base.split('<body>',1)[0]
header=base.split('<body>',1)[1].split('<main',1)[0]
footer='<footer'+base.split('<footer',1)[1]
nav='''<nav id="sitenav" class="sitenav"><a href="/study-library.html">Study library</a><a href="/democracy-100.html">Democracy 100</a><a href="/quizzes.html">Quizzes</a><a href="/support.html">For classrooms</a><a href="/subscribe.html">Subscribe</a></nav>'''
header=re.sub(r'<nav id="sitenav".*?</nav>',nav,header,flags=re.S)
footer=re.sub(r'<div class="foot-links">.*?</div>','''<div class="foot-links"><a href="/study-library.html">Study library</a><a href="/democracy-100.html">Democracy 100</a><a href="/themes.html">Themes</a><a href="/upsc-syllabus-map.html">UPSC map</a><a href="/glossary.html">Glossary</a><a href="/quizzes.html">Quizzes</a><a href="/subscribe.html">Subscribe</a><a href="/support.html">Classroom enquiries</a><a href="/editorial-policy.html">Editorial policy</a><a href="/privacy.html">Privacy</a><a href="/feed.xml">RSS</a><a href="/about.html">About</a></div>''',footer,flags=re.S)
footer=footer.replace('a public notebook by Diljot. History, democracy and civic affairs, in plain words.','Independent study notes by Diljot. Indian history, democracy and public affairs, in plain words.')
footer=footer.replace('General information, fact-checked on 1 November 2026. Not legal advice. publicnotes.org','Educational reading · Check each note’s date and context · publicnotes.org')
footer=re.sub(r'<script src="/assets/learning.js[^\"]*" defer></script>','',footer)
footer=footer.replace('</body>','<script src="/assets/learning.js?v=20261101" defer></script></body>')

def page(path,title,desc,body,wide=False,article=False):
    h=re.sub(r'<title>.*?</title>','<title>'+E(title)+' | Public Notes</title>',head)
    h=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+E(desc,quote=True)+'">',h)
    for attr,key,val in [('property','og:title',title),('property','og:description',desc),('property','og:url','https://publicnotes.org'+('/' if path=='index.html' else '/'+path)),('name','twitter:title',title),('name','twitter:description',desc)]:
        h=re.sub('<meta '+attr+'="'+key+'" content="[^"]*">','<meta '+attr+'="'+key+'" content="'+E(val,quote=True)+'">',h)
    h=re.sub(r'<link rel="canonical" href="[^"]*">','<link rel="canonical" href="https://publicnotes.org'+('/' if path=='index.html' else '/'+path)+'">',h)
    h=re.sub(r'<script type="application/ld\+json">.*?</script>','',h,flags=re.S)
    h=re.sub(r'<link rel="stylesheet" href="/assets/learning.css[^\"]*">','',h)
    h=h.replace('</head>','<link rel="stylesheet" href="/assets/learning.css?v=20261101"></head>')
    if article:
        h=h.replace('content="website"','content="article"')
        ld={'@context':'https://schema.org','@type':'Article','headline':title,'description':desc,'author':{'@type':'Person','name':'Diljot'},'datePublished':'2026-11-01','mainEntityOfPage':'https://publicnotes.org/'+path}
        h=h.replace('</head>','<script type="application/ld+json">'+json.dumps(ld).replace('</',r'<\/')+'</script></head>')
    f=SITE/path;f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(h+'<body>'+header+'<main id="main" class="'+('wide' if wide else 'narrow')+'">'+body+'</main>'+footer,encoding='utf-8')

def series_name(n):return 'UPSC foundations' if n['series']=='upsc' else 'Current affairs explainers'
def excerpt(n,size=170):
    t=n['paragraphs'][0]
    return t if len(t)<=size else t[:size].rsplit(' ',1)[0]+'…'
def btn(url,label,primary=False):return '<a class="btn'+(' btn-primary' if primary else '')+'" href="'+E(url,quote=True)+'">'+E(label)+'</a>'
def signup():return '''<aside class="signup"><p class="kicker">A little reading each week</p><h2>Keep learning with Public Notes</h2><p>New notes, a useful read from the archive and a question to think about. Follow by email or RSS.</p><p>'''+btn('/subscribe.html','Get new notes',True)+' '+btn('/feed.xml','Follow RSS')+'</p></aside>'

for index,n in enumerate(notes):
    body='<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/study-library.html">Study library</a> / '+E(series_name(n))+'</nav>'
    body+='<article class="note"><p class="kicker">'+E(series_name(n))+' · Note '+f'{n["number"]:03}'+'</p><h1>'+E(n['title'])+'</h1><p class="meta">'+E(n['theme'])+' · Reference edition 1 November 2026 · '+str(max(1,round(len(' '.join(n['paragraphs']).split())/200)))+' min read</p>'
    if n['syllabus']:body+='<p class="study-syllabus"><strong>Study context:</strong> '+E(n['syllabus'])+'</p>'
    if n['series']=='current-affairs':body+='<p class="small">Background explainer from the November 2026 study collection. Events discussed may predate the collection; this is not a monthly news update.</p>'
    body+='<div class="prose">'+''.join('<p>'+E(p)+'</p>' for p in n['paragraphs'])+'</div>'
    if n['takeaways']:body+='<section class="takeaways"><h2>Key takeaways</h2><ul>'+''.join('<li>'+E(t)+'</li>' for t in n['takeaways'])+'</ul></section>'
    if n['relevance']:body+='<h2>Why it matters for civil studies</h2><p>'+E(n['relevance'])+'</p>'
    if n['question']:body+='<h2>Think it through</h2><p>'+E(n['question'])+'</p>'
    body+='<p class="small">From the Public Notes companion study collection. <a href="/editorial-policy.html">Editorial context and corrections</a>.</p></article>'
    url='https://publicnotes.org'+n['path']
    body+='<div class="share" data-url="'+E(url,quote=True)+'" data-title="'+E(n['title'],quote=True)+'"><span class="share-label">Share this note</span><button class="btn share-copy" type="button">Copy link</button><a class="btn" target="_blank" rel="noopener" href="https://wa.me/?text='+quote(n['title']+' '+url,safe='')+'">WhatsApp</a></div>'
    peers=[x for x in notes if x['series']==n['series'] and x['theme']==n['theme']]
    j=peers.index(n)
    body+='<nav class="study-pager" aria-label="Reading navigation">'+(btn(peers[j-1]['path'],'← Previous note') if j>0 else '')+btn('/study-library.html?series='+n['series']+'&theme='+quote(n['theme']),'Back to this theme')+(btn(peers[j+1]['path'],'Next note →') if j+1<len(peers) else '')+'</nav>'
    body+=signup()
    page(n['path'].lstrip('/'),n['title'],excerpt(n,155),body,article=True)

themes=sorted(set(n['theme'] for n in notes),key=str.casefold)
controls='''<form class="library-controls" id="library-filters" role="search"><div class="library-query"><label for="library-query">Search notes</label><input id="library-query" type="search" name="q" placeholder="Try inflation, Constitution or climate" autocomplete="off"></div><div><label for="library-series">Collection</label><select id="library-series" name="series"><option value="all">All collections</option><option value="upsc">UPSC foundations · 300</option><option value="current-affairs">Current affairs explainers · 100</option></select></div><div><label for="library-theme">Theme</label><select id="library-theme" name="theme"><option value="all">All themes</option>'''+''.join('<option>'+E(t)+'</option>' for t in themes)+'''</select></div><button class="btn" type="reset">Clear filters</button></form>'''
cards=''
for n in notes:
    search=' '.join([n['title'],n['theme'],n['syllabus'],*n['takeaways']]).lower()
    cards+='<article class="card library-card" data-series="'+n['series']+'" data-theme="'+E(n['theme'],quote=True)+'" data-query="'+E(search,quote=True)+'"><p class="kicker">'+E(series_name(n))+' · '+f'{n["number"]:03}'+'</p><h2><a href="'+n['path']+'">'+E(n['title'])+'</a></h2><p>'+E(excerpt(n))+'</p><p class="meta">'+E(n['theme'])+'</p></article>'
library='''<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Study library</nav><header class="page-head"><p class="kicker">400 companion notes · 40 subject themes</p><h1>Find your next study note</h1><p class="lede">Explore 300 UPSC foundation notes and 100 current affairs explainers, organised by subject. Start with a concept, read the takeaways, then try the discussion question.</p><p class="small">Reference edition 1 November 2026. Current affairs explainers include earlier events and are not a monthly digest.</p></header>'''+controls+'''<p id="library-count" role="status" aria-live="polite">400 notes in the companion library</p><p id="library-empty" hidden>No notes match these filters. Try a broader term or clear the filters.</p><div class="library-grid" id="library-grid">'''+cards+'''</div><button class="btn" id="library-more" type="button" hidden>Show more notes</button><noscript><p>All notes are listed below. Use your browser’s Find command to search this page.</p></noscript><section class="spaced"><h2>More ways to learn</h2><p><a href="/democracy-100.html">Indian Democracy in 100 Notes</a> · <a href="/upsc-syllabus-map.html">Democracy series syllabus map</a> · <a href="/glossary.html">Glossary</a> · <a href="/quizzes.html">Topic quizzes</a></p></section>'''+signup()
page('study-library.html','UPSC Study Library and Current Affairs Explainers','Search 300 UPSC foundation notes and 100 current affairs explainers by subject, with key takeaways and discussion questions.',library,wide=True)

# Homepage retains the existing identity, giving the learning collections priority.
featured=[notes[0],next(n for n in notes if n['number']==172 and n['series']=='upsc'),next(n for n in notes if n['number']==235 and n['series']=='upsc')]
homebody='''<section class="hero learning-hero"><div class="hero-inner"><p class="eyebrow">Public Notes · Read. Understand. Revise.</p><h1>Understand India.<br>One clear note at a time.</h1><p>Plain-English study notes on history, democracy, the economy and public affairs. Built for curious readers, UPSC and State PCS preparation.</p><div class="hero-actions">'''+btn('/study-library.html','Explore the study library',True)+' '+btn('/quizzes.html','Try a free quiz')+'''</div><p class="hero-small">Free to read. No account needed.</p></div></section><section class="learning-stats" aria-label="Study collections"><a href="/study-library.html?series=upsc"><strong>300</strong><span>UPSC foundation notes</span></a><a href="/study-library.html?series=current-affairs"><strong>100</strong><span>Current affairs explainers</span></a><a href="/democracy-100.html"><strong>100</strong><span>Notes on democracy</span></a></section><form action="/study-library.html" class="home-search" role="search"><label for="home-query">What would you like to understand?</label><div><input id="home-query" type="search" name="q" placeholder="Search the companion library" required><button class="btn btn-primary" type="submit">Find notes</button></div></form><section><div class="section-heading"><h2>Choose where to begin</h2><a href="/study-library.html">Browse all subjects →</a></div><div class="grid"><article class="card pathway"><p class="kicker">Build your foundations</p><h3>UPSC study notes</h3><p>History, geography, society, governance, economy, science, environment and ethics in 30 themes.</p>'''+btn('/study-library.html?series=upsc','Explore 300 notes')+'''</article><article class="card pathway"><p class="kicker">Connect ideas to events</p><h3>Current affairs explained</h3><p>Background on policy, courts, trade, science and society. Context to help you make sense of the headlines.</p>'''+btn('/study-library.html?series=current-affairs','Explore 100 explainers')+'''</article><article class="card pathway"><p class="kicker">Know your institutions</p><h3>Indian democracy</h3><p>Constitution, elections, Parliament, courts and citizenship, supported by a syllabus map and topic quizzes.</p>'''+btn('/democracy-100.html','Read Democracy 100')+'''</article></div></section><section><div class="section-heading"><h2>A few useful starting points</h2><a href="/glossary.html">Open the glossary →</a></div><div class="grid">'''+''.join('<article class="card"><p class="kicker">'+E(n['theme'])+'</p><h3><a href="'+n['path']+'">'+E(n['title'])+'</a></h3><p>'+E(excerpt(n))+'</p></article>' for n in featured)+'''</div></section><section class="practice-strip"><div><p class="kicker">Check your understanding</p><h2>Read a note. Take a quiz.</h2><p>Fifty questions across ten democracy themes, with explanations and links back to the notes.</p></div>'''+btn('/quizzes.html','Choose a quiz',True)+'''</section>'''+signup()+'''<section class="classroom-strip"><div><p class="kicker">For teachers and learning groups</p><h2>Bring Public Notes into your classroom</h2><p>Enquire about classroom use, tailored reading selections and revision packs.</p></div>'''+btn('/support.html','Discuss classroom use')+'''</section><section><div class="section-heading"><h2>From the public notebook</h2><a href="/about.html">About Public Notes →</a></div><p class="section-intro">Personal essays, history and analysis by Diljot, alongside the study collections.</p><div class="grid">'''
for title,path,desc in [('Lahore 1929 and the Purna Swaraj resolution','/posts/lahore-1929-purna-swaraj.html','How a resolution, a public pledge and a historical moment connected.'),('How the protests started after Lahore','/posts/how-protests-started-after-lahore.html','From the Dandi March to Dharasana: the people and organisation behind the movement.'),('Daring to think there is scope to improve','/posts/daring-to-think-there-is-scope-to-improve.html','A personal reflection from the public notebook.')]:
    homebody+='<article class="card"><h3><a href="'+path+'">'+E(title)+'</a></h3><p>'+E(desc)+'</p></article>'
homebody+='</div></section>'
page('index.html','Public Notes Study Notes for UPSC and State PCS','Explore 500 free notes across UPSC foundations, current affairs explainers and Indian democracy. Plain English, key takeaways, topic quizzes and classroom enquiries.',homebody,wide=True)

page('subscribe.html','Get New Study Notes by Email or RSS','Follow Public Notes study notes by email or RSS. Send a subscription request directly to Diljot.', '''<nav class="crumbs"><a href="/">Home</a> / Subscribe</nav><header class="page-head"><p class="kicker">Stay curious</p><h1>A little reading each week</h1><p class="lede">New notes, a useful read from the archive and one question to think about.</p></header><section class="card"><h2>Join by email</h2><p>The weekly email is sent personally by Diljot. Use the button to open an email request, then send it from your email app. There is no account to create.</p><p>'''+btn('mailto:ds@publicnotes.org?subject=Subscribe%20to%20Public%20Notes&body=Please%20add%20me%20to%20the%20Public%20Notes%20weekly%20email.','Open subscription email',True)+'''</p><p class="small">Prefer webmail? Email <a href="mailto:ds@publicnotes.org">ds@publicnotes.org</a> with the subject “Subscribe to Public Notes”. Reply “stop” to leave the list.</p></section><section class="card spaced"><h2>Follow by RSS</h2><p>Read new entries in your preferred feed reader.</p><p><a href="/feed.xml">https://publicnotes.org/feed.xml</a></p><button class="btn" type="button" id="copy-feed">Copy feed address</button><span id="feed-status" role="status"></span></section><section class="spaced"><h2>What interests you?</h2><p><a href="/study-library.html?series=upsc">UPSC foundations</a> · <a href="/study-library.html?series=current-affairs">Current affairs explainers</a> · <a href="/democracy-100.html">Indian democracy</a></p><p>For teaching or learning groups, <a href="/support.html">ask about classroom use</a>.</p><p class="small"><a href="/privacy.html">How email and privacy work</a></p></section>''')

page('support.html','Classroom Use and Partnerships','Enquire about Public Notes classroom reading selections, revision packs and clearly labelled sponsorship.', '''<nav class="crumbs"><a href="/">Home</a> / For classrooms</nav><header class="page-head"><p class="kicker">For teachers and learning groups</p><h1>Make the notes part of your teaching</h1><p class="lede">Discuss classroom use, reading selections and revision packs built around the subjects your learners need.</p></header><div class="two"><section class="card"><h2>Classroom editions</h2><p>Tell us the exam or course, language, group size and how you want to use the material. We can discuss an appropriate selection and distribution terms.</p><p>'''+btn('mailto:ds@publicnotes.org?subject=Public%20Notes%20classroom%20enquiry&body=Exam%20or%20course%3A%0ALanguage%3A%0AGroup%20size%3A%0AIntended%20use%3A%0A','Send a classroom enquiry',True)+'''</p></section><section class="card"><h2>Revision packs</h2><p>Enquire about a focused selection for your learning group, with a reading sequence, discussion prompts and revision priorities.</p><p>'''+btn('mailto:ds@publicnotes.org?subject=Public%20Notes%20revision%20pack%20enquiry','Discuss a reading pack')+'''</p></section></div><section class="spaced"><h2>Partnerships and sponsorship</h2><p>Relevant education partners can contact Diljot with a proposed placement and audience. Any sponsored placement must be clearly labelled and must not determine editorial conclusions.</p><p>'''+btn('mailto:ds@publicnotes.org?subject=Public%20Notes%20partnership%20enquiry','Discuss a partnership')+'''</p></section><p class="small">Public articles are free to read. Enquiries do not place an order or create a paid subscription. Any paid proposal will specify scope, price and delivery terms before agreement. No payments are collected on this website.</p>''')

page('editorial-policy.html','Editorial Context and Corrections','Understand the scope, dates and editorial approach of Public Notes study material.', '''<h1>Editorial context and corrections</h1><p>Public Notes is an independent educational publication by Diljot. It combines study notes, public affairs explainers and separately labelled personal essays.</p><h2>The companion study collection</h2><p>The 300 UPSC foundation notes and 100 current affairs explainers come from the Public Notes companion study collection dated 1 November 2026. The website preserves their explanations, key takeaways, syllabus context and discussion questions. The collection date is not necessarily the date of the events discussed.</p><p>These notes are background reading. They do not replace the official syllabus, primary documents or standard textbooks. Current affairs explainers include earlier events and should be read with their stated context; they are not a live news service or a monthly digest. A displayed collection date does not mean every changing claim has been independently rechecked on that date.</p><h2>Facts and interpretation</h2><p>Readers should distinguish historical facts, attributed claims, interim decisions and analysis. Personal reflections and historical comparisons belong to the public notebook. Policy announcements, implementation and measured results are different stages.</p><h2>Images</h2><p>Existing pages identify their images and credits. AI illustrations are illustrations, not photographic evidence. The companion text collection is published here without the reference document’s image material.</p><h2>Corrections</h2><p>Send the page link, disputed statement and a supporting source to <a href="mailto:ds@publicnotes.org?subject=Public%20Notes%20correction">ds@publicnotes.org</a>. A correction should identify what changed and preserve any necessary context.</p><h2>Independent educational material</h2><p>UPSC and State PCS references describe the intended study audience. They do not imply endorsement by a commission or examination authority.</p>''')

page('privacy.html','Privacy and Email','How Public Notes handles email requests and browser interactions.', '''<h1>Privacy and email</h1><p>Public Notes can be read without an account. The study library searches notes in your browser and does not send search terms to a search service. A shared library URL can contain the search term and selected filters.</p><h2>Email requests</h2><p>Subscription and enquiry buttons open your email application. Nothing is sent until you send the message. Your email provider handles that message under its own terms. Subscription requests go to ds@publicnotes.org and are managed personally by Diljot. Weekly emails use BCC; reply “stop” to leave the list.</p><h2>Quizzes and sharing</h2><p>Quiz answers are handled in your browser. Copy buttons copy the public page or feed address to your clipboard when you activate them. External sharing links open the destination service, which has its own privacy practices.</p><h2>Hosting</h2><p>The site is hosted on Vercel. Hosting and network providers may process request information as part of serving and protecting the website. This update adds no advertising trackers or third-party analytics scripts.</p><h2>Contact</h2><p>For privacy questions, email <a href="mailto:ds@publicnotes.org?subject=Public%20Notes%20privacy%20question">ds@publicnotes.org</a>.</p>''')

page('about.html','About Public Notes','Independent educational notes by Diljot on India, history, democracy and public affairs.', '''<header class="page-head"><p class="kicker">By Diljot</p><h1>Public Notes</h1><p class="lede">A place to understand India through clear explanations, useful context and questions worth thinking about.</p></header><p>I started Public Notes as a public notebook: short notes in my own words, each with a link a reader could share. The study collections extend that idea to history, geography, governance, economy, science and society.</p><h2>Choose your way in</h2><p>Use the <a href="/study-library.html">companion library</a> for 300 UPSC foundation notes and 100 current affairs explainers. Read <a href="/democracy-100.html">Indian Democracy in 100 Notes</a> for institutions and citizenship, or use the <a href="/quizzes.html">topic quizzes</a> to test your understanding.</p><h2>The public notebook</h2><p>The original essays, history and reflections remain available alongside the study material.</p><ul>'''+''.join('<li><a href="'+path+'">'+E(title)+'</a></li>' for title,path in [('A New India Is Building','/posts/a-new-india-is-building.html'),('Lahore 1929 and Purna Swaraj','/posts/lahore-1929-purna-swaraj.html'),('How the protests started after Lahore','/posts/how-protests-started-after-lahore.html'),('Parallel analysis of Lahore 1929 and a new India','/posts/parallel-analysis-lahore-1929-new-india.html'),('Analysed summary of the public impeachment','/posts/analysed-summary-public-impeachment.html'),('Daring to think there is scope to improve','/posts/daring-to-think-there-is-scope-to-improve.html'),('How Public Notes began','/posts/how-public-notes-works.html')])+'''</ul><h2>Write to me</h2><p>For corrections, ideas or classroom enquiries, email <a href="mailto:ds@publicnotes.org">ds@publicnotes.org</a>. Read the <a href="/editorial-policy.html">editorial policy</a> for the scope and dates of the study material.</p>''')

# Consistent navigation on all existing pages, preserving their content and URLs.
for file in SITE.rglob('*.html'):
    text=file.read_text(encoding='utf-8')
    text=re.sub(r'<nav id="sitenav".*?</nav>',nav,text,flags=re.S)
    text=re.sub(r'<footer.*',footer,text,flags=re.S)
    if '/assets/learning.css' not in text:
        text=text.replace('</head>','<link rel="stylesheet" href="/assets/learning.css?v=20261101"></head>')
    file.write_text(text,encoding='utf-8')

sm=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
for file in sorted(SITE.rglob('*.html')):
    rel=file.relative_to(SITE).as_posix()
    if rel=='404.html':continue
    u=ET.SubElement(sm,'url');ET.SubElement(u,'loc').text='https://publicnotes.org'+('/' if rel=='index.html' else '/'+rel)
    ET.SubElement(u,'lastmod').text='2026-11-01'
ET.ElementTree(sm).write(SITE/'sitemap.xml',encoding='utf-8',xml_declaration=True)
(SITE/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: https://publicnotes.org/sitemap.xml\n',encoding='utf-8')
import shutil
for name in ('learning.css','learning.js'):
    src=ROOT/'generator'/'assets'/name
    if src.exists():shutil.copyfile(src,SITE/'assets'/name)
print(json.dumps({'imported_notes':len(notes),'foundations':sum(n['series']=='upsc' for n in notes),'current_affairs':sum(n['series']=='current-affairs' for n in notes),'html_pages':len(list(SITE.rglob('*.html')))},indent=2))
