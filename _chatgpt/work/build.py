import requests,re,os,hashlib,json,concurrent.futures as cf
from bs4 import BeautifulSoup as BS
from pathlib import Path
from urllib.parse import urljoin,urlsplit,unquote
from xml.etree import ElementTree as ET
base='https://edge-of-liberty.com'
root=Path('outputs/edge-of-liberty.com'); root.mkdir(parents=True,exist_ok=True)
(root/'assets').mkdir(exist_ok=True)
urls={urlsplit(e.text).path or '/' for f in Path('work').glob('*.xml') for e in ET.parse(f).findall('.//{*}loc')}
pages={}; errors={}; assets={}
def fetch(p):
 try:
  r=requests.get(base+p,timeout=30);r.raise_for_status();return BS(r.content,'html.parser')
 except Exception as e: errors[p]=str(e)
pool=cf.ThreadPoolExecutor(12)
while todo:=sorted(urls-pages.keys()-errors.keys()):
 for p,s in zip(todo,pool.map(fetch,todo)):
  if not s:continue
  pages[p]=s
  for a in s.select('a[href]'):
   u=urlsplit(urljoin(base+p,a['href']))
   if u.hostname in ('edge-of-liberty.com','www.edge-of-liberty.com') and not u.path.startswith(('/m/','/api/')) and '.' not in u.path:urls.add(u.path.rstrip('/') or '/')
print('pages',len(pages),errors,flush=True)
def file(p):return root/p.strip('/')/'index.html'
pattern=re.compile(r"""url\(\s*['"]?([^)'"]+)['"]?\s*\)""")
jobs=[]
for p,s in pages.items():
 dest=file(p);dest.parent.mkdir(parents=True,exist_ok=True)
 def asset(v):
  u=urljoin(base+p,v)
  if urlsplit(u).hostname and ('wsimg.com' in urlsplit(u).hostname or urlsplit(u).hostname=='edge-of-liberty.com'):
   key='ASSET'+hashlib.sha256(u.encode()).hexdigest()[:24];assets[key]=u;return key
  return v
 for a in s.select('a[href]'):
  u=urlsplit(urljoin(base+p,a['href']));path=u.path.rstrip('/') or '/'
  if a['href'].startswith('#'):continue
  if u.hostname in ('www.edge-of-liberty.com','edge-of-liberty.com'):
   a['href']=(os.path.relpath(file(path).parent,dest.parent)+'/'+('?' + u.query if u.query else '')+('#'+u.fragment if u.fragment else '')) if path in pages else u.geturl()
 for el in s.select('img,source,video,script[src],link[rel~=icon]'):
  for attr in ('src','poster','href','srcset'):
   v=el.get({'src':'data-srclazy','srcset':'data-srcsetlazy'}.get(attr,'')) or el.get(attr)
   if not v:continue
   el[attr]=re.sub(r'(?:https?:)?//[^\s]+?(?=\s+\d+[wx]|,\s+|$)',lambda m:asset(m[0]),v) if attr=='srcset' else asset(v)
  for attr in ('data-lazyimg','data-srclazy','data-srcsetlazy'):el.attrs.pop(attr,None)
 for el in s.select('style'):
  if el.string:el.string=pattern.sub(lambda m:'url("'+asset(m[1])+'")',el.string)
 jobs.append((dest,str(s)))
def download(pair):
 key,u=pair
 try:
  r=requests.get(u,timeout=45);r.raise_for_status();typ=r.headers.get('content-type','').split(';')[0]
  ext={'image/jpeg':'jpg','image/svg+xml':'svg','application/javascript':'js','text/javascript':'js'}.get(typ,typ.split('/')[-1].split('+')[0] or 'bin')
  path=root/'assets'/(key[5:]+'.'+ext);path.write_bytes(r.content);return key,path
 except Exception as e:errors[u]=str(e);return key,None
print('assets',len(assets),flush=True)
paths=dict(pool.map(download,assets.items()))
for dest,html in jobs:
 html=re.sub(r'ASSET[a-f0-9]{24}',lambda m:os.path.relpath(paths[m[0]],dest.parent) if paths[m[0]] else assets[m[0]],html)
 dest.write_text(html)
(root/'.nojekyll').touch()
Path('work/report.json').write_text(json.dumps(dict(pages=sorted(pages),errors=errors),indent=2))
print(len(paths),errors,flush=True)
