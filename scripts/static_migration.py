"""Convert the preserved Work capture to the approved static site. No site crawl.
Run from repository root after gallery assets have been recovered.
Original captures under _chatgpt/outputs are never modified.
"""
from pathlib import Path
from bs4 import BeautifulSoup as B
from urllib.parse import urlsplit, unquote, quote
from xml.etree import ElementTree as ET
import json, re, os, csv, hashlib, html
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
SOURCE=ROOT/'_chatgpt/outputs/edge-of-liberty.com'
galleries=json.loads((ROOT/'_chatgpt/work/gallery-config.json').read_text())
gallery_assets=json.loads((ROOT/'_chatgpt/work/gallery-assets.json').read_text())
CAL='ea21prdeldsriijnm23ccavkag@group.calendar.google.com'
MAP='https://www.google.com/maps/search/?api=1&query=606+N+Calumet+Ave+Valparaiso+IN+46383'

def fragment(markup):return B(markup,'html.parser')
def local(path, dest):return os.path.relpath(ROOT/path.lstrip('/'), dest.parent) + ('/' if not Path(path).suffix else '')
def insert(w,markup):
 target=w.select_one('section') or w
 target.append(fragment(markup))
def block(title,body):return '<section class="static-content"><h1>'+title+'</h1>'+body+'</section>'
def configs(s):
 out=[]
 for script in s.select('script[src]'):
  p=ROOT/'assets'/Path(script['src']).name
  if not p.exists():continue
  for m in re.finditer(r'JSON.parse\(("(?:\\.|[^"\\])*")\)',p.read_text()):
   try:out.append(json.loads(json.loads(m[1])))
   except (ValueError,TypeError):pass
 return out

def convert(source,dest):
 s=B(source.read_text(),'html.parser')
 service={}
 for scr in s.select('script'):
  if scr.string and scr.string.startswith('window._OLA_DATA='):
   service=json.loads(scr.string.split('=',1)[1].rstrip(';'))['service']
 # Keep captured styling and content. Replace only executable GoDaddy runtime.
 for e in s.select('script'):
  if e.get('type')!='application/ld+json':e.decompose()
 for e in s.select('link'):
  if any(r in e.get('rel',[]) for r in ['manifest','preconnect','dns-prefetch','preload']):e.decompose()
 for e in s.select('meta[name="generator"]'):e.decompose()
 for e in s.select('*'):
  for a in list(e.attrs):
   if a.startswith('on') or a in ('data-tccl','data-edit-interactive'):del e[a]
 # Accounts and booking engines intentionally retired; page URLs retained below.
 for e in s.select('[data-ux="UtilitiesMenu"], [data-ux="Membership"], .membership-sign-in, .membership-sign-out, .widget-popup, .widget-messaging, .widget-cookie-banner, .widget-trustedsite'):
  e.decompose()
 for e in s.select('a[href]'):
  if 'godaddy.com/websites' in e['href']:
   holder=e.find_parent(attrs={'data-aid':re.compile('POWERED',re.I)})
   (holder or e).decompose()
 for e in s.find_all(string=lambda t:t and t.strip()=='Powered by'):e.extract()
 for more in s.select('[data-aid="NAV_MORE"]'):
  item=more.find_parent('li')
  if item:item.decompose()
 # Remove stale body attributes tied to the removed runtime.
 for e in s.select('iframe[srcdoc]'):
  embedded=B(e['srcdoc'],'html.parser')
  for scr in embedded.select('script'):scr.decompose()
  wrapper=s.new_tag('div',attrs={'class':'static-embed'})
  body=embedded.body or embedded
  for child in list(body.contents):wrapper.append(child.extract())
  e.replace_with(wrapper)
 for e in s.select('iframe'):
  e['loading']='lazy';e['title']=e.get('title') or ('Craft fair information' if 'edgeofliberty' in e.get('src','') else 'Embedded content')
 # Galleries: retain section headings, use all original photos with accessible carousel.
 for w in s.select('.widget-gallery'):
  cfg=galleries.get(w.get('id'))
  if not cfg:raise ValueError('Unmapped gallery '+str(w.get('id')))
  old=w.select_one('[data-ux="Carousel"]')
  if not old:old=w.select_one('[data-test-radpack="bootstrap2"]')
  gallery=s.new_tag('div',attrs={'class':'static-gallery','role':'region','aria-label':cfg.get('title') or 'Photo gallery'})
  frames=s.new_tag('div',attrs={'class':'static-slides'})
  for n,item in enumerate(cfg['galleryImages']):
   imgcfg=item['image'];src=local(gallery_assets['https:'+imgcfg['image']],dest)
   a=s.new_tag('a',href=src,attrs={'class':'static-slide','aria-label':f'Open photo {n+1} full size'})
   img=s.new_tag('img',src=src,alt=item.get('alt') or imgcfg.get('alt') or f'{cfg.get("title") or "The Edge of Liberty gallery"} — photo {n+1}',loading='lazy',width=str(imgcfg.get('oWidth',1200)),height=str(imgcfg.get('oHeight',800)))
   a.append(img);frames.append(a)
  gallery.append(frames)
  gallery.append(fragment('<div class="gallery-controls" hidden><button type="button" data-gallery-step="-1" aria-label="Previous photo">← Previous</button><span aria-live="polite" class="gallery-position"></span><button type="button" data-gallery-step="1" aria-label="Next photo">Next →</button></div>'))
  if old:old.replace_with(gallery)
  else:insert(w,str(gallery))
 for e in s.select('[data-lazybg]'):
  e['class']=[c for c in e.get('class',[]) if c!='d-none']
  e['style']=e.get('style','')+';display:block;'
  del e['data-lazybg']
 # Existing contact addresses; no invented form backend or mailing-list service.
 for form in s.select('.widget-contact form'):
  form.replace_with(fragment('<div class="static-contact"><p><a class="static-button" href="mailto:info@edge-of-liberty.com">Email us</a></p><p><a href="mailto:info@edge-of-liberty.com">info@edge-of-liberty.com</a><br><a href="tel:+12192428320">219-242-8320</a></p></div>'))
 for e in s.find_all(string=lambda t:t and 'using this form' in t):e.replace_with(str(e).replace('using this form','by email'))
 for e in s.select('button'):
  if e.get_text(strip=True)=='Get directions':e.name='a';e['href']=MAP;e['target']='_blank';e['rel']='noopener'
 # Use the same public calendar directly, without GoDaddy's proxy.
 for w in s.select('.widget-calendar'):
  insert(w,f'<div class="static-calendar"><iframe title="The Edge of Liberty events calendar" src="https://calendar.google.com/calendar/embed?src={quote(CAL)}&ctz=America%2FChicago&mode=AGENDA" loading="lazy"></iframe><p><a href="https://calendar.google.com/calendar/u/0/r?cid={quote(CAL)}" target="_blank" rel="noopener">Open calendar in Google Calendar</a></p></div>')
 # FAQ is usable without JS. Preserve answers, amend obsolete booking directions.
 for n,button in enumerate(s.select('.accordion-question')):
  answer=button.parent.select_one('.accordion-answer')
  if answer:
   answer['id']='faq-answer-'+str(n);button['id']='faq-question-'+str(n);button['aria-controls']=answer['id'];button['aria-expanded']='true';answer['aria-labelledby']=button['id']
   answer['style']='display:block'
 for w in s.select('.widget-appointments'):
  if '/ola/' in str(dest):
   slug=dest.parent.name
   title={'tour':'Guided Tour of Our Farm','craft-fair-vendor-orientation':'Craft Fair Vendor Orientation','bcf-eol-mid-week-farm-stand':'BCF / EOL Mid-week Farm Stand'}[slug]
   email='tours@edge-of-liberty.com' if slug=='tour' else 'info@edge-of-liberty.com'
   description=html.escape(service.get('description',''))
   cost=html.escape(service.get('custom_cost_text') or '')
   insert(w,block(title,f'<p>{description}</p><p>{cost}</p><p>Online appointment booking is no longer available on this site.</p><p><a href="mailto:{email}">Contact us: {email}</a></p>'))
  else:w.decompose()
 for answer in s.select('.accordion-answer'):
  text=answer.get_text(' ',strip=True)
  if 'Online Appointments' in text:
   inner=answer.select_one('[data-ux="Text"]') or answer
   inner.clear();inner.append(fragment('<p>Online appointment booking is no longer available on this site. For tour questions, email <a href="mailto:tours@edge-of-liberty.com">tours@edge-of-liberty.com</a>.</p>'))
  elif 'book consecutive hours' in text:
   for node in answer.find_all(string=True):
    if 'book consecutive hours' in node:node.replace_with(str(node).replace('just book consecutive hours','contact us about additional time'))
 for w in s.select('.widget-membership'):
  w.clear();insert(w,block('Account services',f'<p>Online accounts, sign-in, and bookings are no longer available on this site.</p><p><a href="{local("contact",dest)}">Contact The Edge of Liberty</a></p>'))
 # Existing PayPal handoff remains direct; preview return URLs follow the current page.
 for inp in s.select('input[name="return"],input[name="cancel_return"]'):inp['value']='https://edge-of-liberty.com/pay/'
 # FAQ/book links may target preserved service information, never a fake booking action.
 for a in s.select('a[href]'):
  if a['href'].endswith(('/ols/products/edge-of-liberty-craft-fair-food-truck','/ols/products/edge-of-liberty-craft-fair-sweet-truck')):a['href']='https://edgeofliberty.us/book'
  u=urlsplit(a['href'])
  if u.hostname in ('edge-of-liberty.com','www.edge-of-liberty.com'):
   a['href']=local(unquote(u.path).strip('/') or '.',dest)+('?' + u.query if u.query else '')+('#'+u.fragment if u.fragment else '')
  if a.get('target')=='_blank':a['rel']='noopener noreferrer'
  if 'docs.google.com/forms/d/e/1FAIpQLSd5WPj6MKzZLHIUFycwlwg8LZPAGZ03nUMX9puwpwwqtQTQiQ' in a.get('href',''):
   a.insert_after(s.new_string(' (historical registration form; public access unavailable)'))
 # Social metadata images can point at their already-downloaded counterpart.
 for meta in s.select('meta[content]'):
  u=meta['content']
  if 'wsimg.com' in u:
   candidates=list((ROOT/'assets').glob(hashlib.sha256(u.encode()).hexdigest()[:24]+'.*'))
   if candidates:meta['content']='https://edge-of-liberty.com/assets/'+candidates[0].name
   else:meta.decompose()
 for a in s.select('[data-aid="HAMBURGER_MENU_LINK"], [data-ux="NavLinkDropdown"], [data-ux="CloseIcon"]'):
  a['tabindex']='0';a['role']='button'
 for e in s.select('svg[viewbox]'):e['viewBox']=e['viewbox'];del e['viewbox']
 css=s.new_tag('link',rel='stylesheet',href=local('assets/static-site.css',dest));s.head.append(css)
 js=s.new_tag('script',src=local('assets/static-site.js',dest),defer=True);s.body.append(js)
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(str(s))
 return s

for source in SOURCE.rglob('index.html'):
 convert(source,ROOT/source.relative_to(SOURCE))

# Missing historic routes retain their URL with an honest notice, not fabricated articles.
missing=[]
with open('_chatgpt/outputs/URL inventory.csv') as fp:
 for row in csv.DictReader(fp):
  if '500 Server Error' in row['Migration result']:missing.append(urlsplit(row['Source URL']).path.strip('/'))
missing += ['about-bella-lena','crafters:-bella-lena','open-farm-vendors','ols/products','m/account','m/bookings']
for route in missing:
 dest=ROOT/route/'index.html'
 # Start from the existing About layout, rebase its local paths for the new location.
 s=B((ROOT/'about/index.html').read_text(),'html.parser')
 for e in s.select('[href], [src]'):
  for key in ['href','src']:
   v=e.get(key)
   if v and not urlsplit(v).scheme and not v.startswith(('#','//')):
    target=(ROOT/'about'/urlsplit(v).path).resolve()
    e[key]=os.path.relpath(target,dest.parent)+('/' if v.endswith('/') else '')
 for img in s.select('[srcset]'):
  img['srcset']=re.sub(r'\.\./assets/([^,\s]+)',lambda m:local('assets/'+m[1],dest),img['srcset'])
 for style in s.select('style'):
  if style.string:style.string=re.sub(r'url\("(\.\./assets/[^\"]+)"\)',lambda m:'url("'+local('assets/'+Path(m[1]).name,dest)+'")',style.string)
 widgets=s.select('.widget')
 content=[w for w in widgets if not any(c in w.get('class',[]) for c in ['widget-header','widget-footer'])]
 title='Article unavailable' if route.startswith('blog/f/') else ('Account services' if route.startswith('m/') else 'Page unavailable')
 message='This archived article has not yet been recovered.' if route.startswith('blog/f/') else ('Online accounts, sign-in, and bookings are no longer available on this site.' if route.startswith('m/') else 'The original content for this page is not currently available.')
 new=fragment(block(title,f'<p>{message}</p><p><a href="{local("blog" if route.startswith("blog/") else "contact",dest)}">'+('Browse available articles' if route.startswith('blog/') else 'Contact The Edge of Liberty')+'</a></p>'))
 if content:
  content[0].replace_with(new)
  for w in content[1:]:w.decompose()
 s.title.string=title+' | The Edge of Liberty'
 for e in s.select('link[rel="canonical"]'):e['href']='https://edge-of-liberty.com/'+quote(route,safe='/')+'/'
 s.head.append(s.new_tag('meta',attrs={'name':'robots','content':'noindex'}))
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(str(s))

# Supply the existing RSS areas with the recovered articles, without a hosted feed.
posts=sorted((ROOT/'blog/f').glob('*/index.html'))
posts=[f for f in posts if f.parent.relative_to(ROOT).as_posix() not in missing]
for f in [ROOT/'index.html',ROOT/'blog/index.html',*list((ROOT/'ola').rglob('index.html'))]:
 s=B(f.read_text(),'html.parser')
 for w in s.select('.widget-rss'):
  for ul in w.select('ul'):ul.decompose()
  for loader in w.select('[data-ux=Loader]'):
   container=loader.find_parent(id=re.compile(r'^bs-'))
   (container or loader).decompose()
  links='<ul class="static-posts">'+''.join('<li><a href="'+local(p.parent.relative_to(ROOT).as_posix(),f)+'">'+B(p.read_text(),'html.parser').title.get_text()+'</a></li>' for p in reversed(posts))+'</ul>'
  insert(w,links)
 f.write_text(str(s))
# A custom 404 preserves navigation at either preview or custom-domain base URL.
s=B((ROOT/'about/index.html').read_text(),'html.parser')
for w in s.select('.widget'):
 if 'widget-header' not in w.get('class',[]) and 'widget-footer' not in w.get('class',[]):w.decompose()
footer=s.select_one('.widget-footer');footer.insert_before(fragment(block('Page not found','<p>Please use the navigation to find a page, or <a href="contact/">contact us</a>.</p>')))
for e in s.select('[href], [src]'):
 for key in ['href','src']:
  if e.get(key,'').startswith('../'):e[key]=e[key][3:]
for img in s.select('[srcset]'):img['srcset']=img['srcset'].replace('../assets/','assets/')
for st in s.select('style'):
 if st.string:st.string=st.string.replace('../assets/','assets/')
s.title.string='Page not found | The Edge of Liberty'
s.head.insert(0,s.new_tag('base',href='/edge-of-liberty.com/'))
s.head.append(s.new_tag('meta',attrs={'name':'robots','content':'noindex'}))
(ROOT/'404.html').write_text(str(s))
ns='http://www.sitemaps.org/schemas/sitemap/0.9';doc=ET.Element('urlset',xmlns=ns)
for f in sorted(ROOT.rglob('index.html')):
 if any(p.startswith('.') or p=='_chatgpt' for p in f.relative_to(ROOT).parts):continue
 if 'name="robots" content="noindex"' in f.read_text() or B(f.read_text(),'html.parser').select_one('meta[name="robots"][content="noindex"]'):continue
 path=f.parent.relative_to(ROOT).as_posix();ET.SubElement(ET.SubElement(doc,'url'),'loc').text='https://edge-of-liberty.com/'+('' if path=='.' else quote(path,safe='/')+'/')
ET.ElementTree(doc).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
print('Converted 21 captured pages; retained',len(missing),'additional historic URLs with explicit notices.')
