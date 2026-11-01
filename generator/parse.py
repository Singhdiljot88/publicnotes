import re,glob,os,json,html
def notes(src, series='democracy-100'):
    out=[]
    for f in sorted(glob.glob(src+'/posts/'+series+'/*.html')):
        t=open(f).read()
        b=t.split('<body>',1)[1]
        b=re.sub(r'</body>.*','',b,flags=re.S)
        title=html.unescape(re.search(r'<h1>(.*?)</h1>',b,re.S).group(1))
        meta=re.search(r'<p class="meta">(.*?)</p>',b,re.S).group(1)
        m=re.match(r'Note (\d+) · Theme (\d+): (.*?) · ',html.unescape(meta))
        body=b.split('</p>',2)  # nav, h1.. handled below
        start=b.index(re.search(r'<p class="meta">.*?</p>',b,re.S).group(0))+len(re.search(r'<p class="meta">.*?</p>',b,re.S).group(0))
        end=b.rfind('<p><em>Fact-checked copy')
        content=b[start:end].strip()
        footer=b[end:].strip()
        tk=re.findall(r'<li>(.*?)</li>',re.search(r'<div class="takeaways">.*?</ul>',content,re.S).group(0))
        first=re.search(r'<p>(.*?)</p>',content,re.S).group(1)
        out.append(dict(file=os.path.basename(f),num=int(m.group(1)),theme=int(m.group(2)),theme_name=m.group(3),title=title,content=content,footer=footer,takeaways=[html.unescape(x) for x in tk],first=html.unescape(re.sub('<[^>]+>','',first)),has_img='<figure' in content))
    return out
if __name__=='__main__':
    import sys
    ns=notes('src')
    print(len(ns), sum(n['has_img'] for n in ns))
    for n in ns[:60]:
        print(n['num'],n['title'],'|','; '.join(n['takeaways']))
