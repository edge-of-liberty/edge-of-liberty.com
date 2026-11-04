from bs4 import BeautifulSoup as B
from pathlib import Path
import json,html,requests,hashlib,concurrent.futures as cf
from urllib.parse import urljoin
from xml.etree import ElementTree as ET
e=lambda x:html.escape(str(x),quote=True)
root=Path('outputs/edge-of-liberty.com')
def local(u):
 u=urljoin('https://edge-of-liberty.com',u); k=hashlib.sha256(u.encode()).hexdigest()[:24];f=root/'assets'/(k+'.jpg')
 try:
  if not f.exists():
   r=requests.get(u,timeout=25);r.raise_for_status();f.write_bytes(r.content)
  return '../../../assets/'+f.name
 except requests.RequestException:return u
def walk(x):
 if isinstance(x,dict):
  if 'fullContent' in x:return x
  for v in x.values():
   y=walk(v)
   if y:return y
for f in [Path('work/sept'),*Path('work').glob('*.archive')]:
 s=B(f.read_bytes(),'html.parser')
 raw=next(t.get_text() for t in s.select('script') if 'window._BLOG_DATA=' in t.get_text()); d=walk(json.JSONDecoder().raw_decode(raw.split('window._BLOG_DATA=')[1])[0]);j=json.loads(d['fullContent']); parts=['<h1>'+e(d['title'])+'</h1><time>'+e(d['publishedDate'][:10])+'</time>']
 imgs=[v['data']['src'] for v in j['entityMap'].values() if v['type']=='IMAGE'];paths=dict(zip(imgs,cf.ThreadPoolExecutor(8).map(local,imgs)))
 for b in j['blocks']:
  t=b['text'];content='';pos=0
  for rr in sorted(b['entityRanges'],key=lambda x:x['offset']):
   i=rr['offset'];n=rr['length'];v=j['entityMap'][str(rr['key'])];data=v['data'];content+=e(t[pos:i]);pos=i+n
   if v['type']=='LINK':content+='<a href="'+e(data['href'])+'">'+e(t[i:i+n])+'</a>'
   if v['type']=='DIVIDER':content+='<hr>'
   if v['type']=='IMAGE':content+='<img style="max-width:100%;height:auto" src="'+e(paths[data['src']])+'" alt="'+e(data.get('alt',''))+'">'+e(data.get('caption',''))
  tag={'header-four':'h4','header-two':'h2','unordered-list-item':'li'}.get(b['type'],'p');parts+=['<'+tag+'>'+content+e(t[pos:])+'</'+tag+'>']
 template=B((root/'blog/index.html').read_bytes(),'html.parser')
 for x in template.select('script:not([type="application/ld+json"])'):x.decompose()
 for x in template.select('[src],[href],[srcset],style'):
  for a in ('src','href','srcset'):
   if x.get(a,'').startswith('../'):x[a]=x[a].replace('../','../../../')
  if x.name=='style' and x.string:x.string=x.string.replace('../assets','../../../assets')
 template.title.string=d['title'];canonical='https://edge-of-liberty.com/blog/f/'+d['slug'];template.select_one('link[rel=canonical]')['href']=canonical
 for meta in template.select('meta[property],meta[name]'):
  k=meta.get('property',meta.get('name'))
  source=next((m['value'] for m in json.JSONDecoder().raw_decode(raw.split('window._BLOG_DATA=')[1])[0]['head']['meta'] if m['key']==k),None)
  if source:meta['content']=source
 template.select_one('.widget-rss').replace_with(B('<article style="max-width:760px;margin:2em auto;padding:0 18px">'+''.join(parts)+'</article>','html.parser'))
 dest=root/'blog/f'/d['slug'];dest.mkdir(parents=True,exist_ok=True);(dest/'index.html').write_text(str(template))
 print(d['slug'],len(j['blocks']),flush=True)
