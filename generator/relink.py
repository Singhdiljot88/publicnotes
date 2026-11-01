import os,re,sys
root=sys.argv[1]
for d,_,fs in os.walk(root):
    for f in fs:
        if not f.endswith('.html'): continue
        p=os.path.join(d,f); rel=os.path.relpath(p,root); depth=rel.count('/')
        pre='../'*depth
        s=open(p).read()
        def fix(m):
            attr,q,url=m.group(1),m.group(2),m.group(3)
            if url.startswith('//'): return m.group(0)
            path,_,frag=url[1:].partition('#')
            if path=='' : path='index.html'
            elif path.endswith('/'): path+='index.html'
            out=(pre+path) if path else ''
            return f'{attr}={q}{out}{"#"+frag if frag else ""}{q}'
        s=re.sub(r'(href|src)=(["\'])(/[^"\']*)\2',fix,s)
        open(p,'w').write(s)
