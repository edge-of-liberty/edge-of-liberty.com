"""One local-only closeout pass: no browser or network calls."""
from pathlib import Path
from bs4 import BeautifulSoup as B
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
exclude=[json.loads(line.strip()[2:]) for line in (ROOT/'_config.yml').read_text().splitlines() if line.strip().startswith('- ')]
def excluded(path):return any(path==x or path.startswith(x+'/') for x in exclude) or any(p.startswith('.') for p in Path(path).parts)
files=[p for p in ROOT.rglob('*.html') if not excluded(str(p.relative_to(ROOT))) and '_chatgpt' not in p.parts]
errors=[];anchors=set();dependencies=set();embeds=set();seasons=[]
hashes=json.loads((ROOT/'_chatgpt/work/phase1-article-hashes.json').read_text())
for f in files:
 name=str(f.relative_to(ROOT));s=B(f.read_text(),'html.parser');base=ROOT if f.name=='404.html' else f.parent
 article=s.select_one('article.static-article')
 if name in hashes:assert article and hashlib.sha256(str(article).encode()).hexdigest()==hashes[name],name+' article altered'
 nav=s.select_one('[data-ux="Nav"] > ul')
 if nav:
  primary=[a.get_text(strip=True) for a in nav.select(':scope > li > a')]
  if primary!=['Home','Craft Fairs','Farm Stand','Private Tours','Event Details']:errors.append((name,'primary nav',primary))
  if [a.text for a in nav.select('.more-links a')]!=['Our Gardens','Calendar','Blog','About','Contact']:errors.append((name,'secondary nav'))
 refs=[]
 for e in s.select('[src],[href],[srcset]'):
  for attr in ('src','href'):
   if e.get(attr):refs.append((e.get(attr),e.name))
  if e.get('srcset'):refs.extend((v.strip().split()[0],e.name) for v in e['srcset'].split(','))
 for e in s.select('style,[style]'):
  text=e.text if e.name=='style' else e['style'];refs.extend((u,'css') for u in re.findall(r'url\([\"\']?([^\)\"\']+)',text))
 for value,tag in refs:
  u=urlsplit(value)
  if u.scheme or u.netloc:
   if 'wsimg.com' in value or 'godaddysites.com' in value:dependencies.add((name,tag,value))
   continue
  if tag=='base':continue
  target=ROOT/unquote(u.path).lstrip('/') if value.startswith('/') else base/unquote(u.path)
  target=target/'index.html' if target.is_dir() else target
  if not target.exists():errors.append((name,'missing',value));continue
  rel=str(target.resolve().relative_to(ROOT))
  if excluded(rel):errors.append((name,'excluded dependency',value))
  if u.fragment and target.suffix=='.html':
   doc=s if target==f else B(target.read_text(),'html.parser')
   if not doc.find(id=unquote(u.fragment)) and not doc.find(attrs={'name':unquote(u.fragment)}):anchors.add(value)
 for e in s.select('iframe,form'):embeds.add((name,e.name,e.get('src') or e.get('action','')))
 canonical=s.select_one('link[rel="canonical"]')
 if f.name!='404.html' and not s.select_one('meta[http-equiv="refresh"]') and canonical:
  expected='/'+str(f.parent.relative_to(ROOT)).strip('.')+'/'
  if unquote(urlsplit(canonical['href']).path).rstrip('/')!=expected.rstrip('/').replace('//','/'):errors.append((name,'canonical',canonical['href']))
 for e in s.select('script[type="application/ld+json"]'):
  if 'wsimg.com' in e.text:dependencies.add((name,'metadata','wsimg'))
 if not article:
  for e in s.find_all(string=True):
   if e.parent.name not in ('style','script') and not e.find_parent(class_='blog-listing') and re.search('2025 season|2026 Calendar|May 17, 2026|09:00 am|9 am|10 am until 4 pm',e):seasons.append((name,str(e)))
blog=B((ROOT/'blog/index.html').read_text(),'html.parser');assert len(blog.select('.blog-card'))==26
assert len(B((ROOT/'index.html').read_text(),'html.parser').select('.blog-card'))==3
assert all(c.select_one('time') and c.select_one('.continue-reading') and c.select_one('img') for c in blog.select('.blog-card'))
urls=[e.text for e in ET.parse(ROOT/'sitemap.xml').findall('.//{*}loc')];assert len([u for u in urls if '/blog/f/' in u])==26
tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
private=[p for p in tracked if not excluded(p) and re.search(r'contacts_export|Campaigns\.csv|blog-export\.xml|\.pem$|credentials|(^|/)\.env',p,re.I)]
for p in tracked:
 if excluded(p) or Path(p).suffix not in ('.html','.js','.css','.xml','.txt'):continue
 f=ROOT/p
 if f.exists() and re.search(r'-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----|ghp_[A-Za-z0-9]{36}',f.read_text(errors='replace')):private.append(p)
assert not (ROOT/'.nojekyll').exists()
print(json.dumps({'pages_checked':len(files),'preserved_articles':len(hashes),'errors':errors,'known_unresolved_fragments':sorted(anchors),'active_GoDaddy_reference_count':len(dependencies),'active_GoDaddy_examples':sorted(dependencies)[:5],'stale_operational_schedules':seasons,'private_publication_files':private,'integrations':sorted(embeds)},indent=2))
assert not errors and not dependencies and not private and not seasons
print('PASS: local links/assets, header structure, blog metadata/cards, article preservation, canonical URLs, sitemap and publication exclusions.')
