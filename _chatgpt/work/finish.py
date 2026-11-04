from pathlib import Path
import os,json,csv
from bs4 import BeautifulSoup as B
from xml.etree import ElementTree as ET
from urllib.parse import urlsplit
r=Path('outputs/edge-of-liberty.com')
blog=r/'blog/index.html';s=B(blog.read_bytes(),'html.parser')
nav=s.new_tag('ul')
for f in sorted((r/'blog/f').glob('*/index.html'),reverse=True):
 a=s.new_tag('a',href='f/'+f.parent.name+'/');a.string=B(f.read_bytes(),'html.parser').title.string;li=s.new_tag('li');li.append(a);nav.append(li)
s.select_one('.widget-rss').append(nav);blog.write_text(str(s))
for f in r.rglob('index.html'):
 s=B(f.read_bytes(),'html.parser')
 for x in s.select('a[href]'):
  href=x['href'];p=urlsplit(href)
  if not p.scheme and '/m/' in '/'+href and not href.startswith('#'):
   x['href']='https://edge-of-liberty.com/m/'+href.split('m/')[-1]
 script=s.new_tag('script');script.string="""document.addEventListener('click',function(e){const hit=e.target.closest('[data-ux=IconHamburger],[data-ux=CloseIcon],[data-ux=NavLinkDropdown],[data-aid=HAMBURGER_MENU_LINK]');if(!hit)return;const drawer=document.querySelector('[data-ux=NavigationDrawer]');if(hit.matches('[data-ux=NavLinkDropdown]')){const menu=hit.parentElement.parentElement.querySelector('[data-ux=Dropdown]');if(!menu)return;const open=hit.getAttribute('aria-expanded')!=='true';menu.style.setProperty('display',open?'block':'none','important');hit.setAttribute('aria-expanded',open);}else if(drawer){const open=!hit.matches('[data-ux=CloseIcon]');drawer.style.setProperty('transform',open?'translateX(0)':'translateX(-110%)','important');drawer.style.setProperty('left','0','important');drawer.style.setProperty('visibility',open?'visible':'hidden','important');}e.preventDefault();e.stopImmediatePropagation();},true);"""
 s.body.append(script);f.write_text(str(s))
rep=json.load(open('work/report.json')); statuses={p:'Public HTML captured' for p in rep['pages']};statuses.update(rep['errors'])
for f in (r/'blog/f').glob('*/index.html'):statuses['/'+str(f.parent.relative_to(r))]='Recovered from archived article data'
for p in ['/m/account','/m/bookings']:statuses[p]='Hosted account workflow'
with open('outputs/URL inventory.csv','w') as fp:
 w=csv.writer(fp);w.writerow(['Source URL','Migration result']);w.writerows([('https://edge-of-liberty.com'+k,v) for k,v in sorted(statuses.items())])
ns='http://www.sitemaps.org/schemas/sitemap/0.9';doc=ET.Element('urlset',xmlns=ns)
for f in sorted(r.rglob('index.html')):
 path=str(f.parent.relative_to(r));ET.SubElement(ET.SubElement(doc,'url'),'loc').text='https://edge-of-liberty.com/'+('' if path=='.' else path)
ET.ElementTree(doc).write(r/'sitemap.xml',encoding='utf-8',xml_declaration=True)
(r/'robots.txt').write_text('User-agent: *\nSitemap: https://edge-of-liberty.com/sitemap.xml\n')
