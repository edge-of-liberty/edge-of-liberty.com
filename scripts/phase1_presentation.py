"""Bounded presentation updates; never regenerates article bodies."""
from pathlib import Path
from bs4 import BeautifulSoup as B
from xml.etree import ElementTree as E
import os,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
NS={'wp':'http://wordpress.org/export/1.2/','c':'http://purl.org/rss/1.0/modules/content/','e':'http://wordpress.org/export/1.2/excerpt/'}
items=E.parse(ROOT/'_chatgpt/work/published-blog.xml').findall('.//item')
posts=[]
for item in items:
 slug=item.findtext('wp:post_name',namespaces=NS)
 page=ROOT/'blog/f'/slug/'index.html';article=B(page.read_text(),'html.parser').select_one('article')
 image=article.select_one('img[src]')
 posts.append(dict(slug=slug,title=item.findtext('title'),date=item.findtext('wp:post_date',namespaces=NS)[:10],excerpt=B(item.findtext('e:encoded',namespaces=NS) or '', 'html.parser').get_text(' ',strip=True),categories=[c.text for c in item.findall('category')],image=(page.parent/image['src']).resolve() if image else None))
posts.sort(key=lambda p:p['date'],reverse=True)
files=[p for p in ROOT.rglob('*.html') if not any(x.startswith('.') or x=='_chatgpt' for x in p.relative_to(ROOT).parts)]
hashes={}
for path in files:
 s=B(path.read_text(),'html.parser');article=s.select_one('article.static-article')
 if article:hashes[str(path.relative_to(ROOT))]=hashlib.sha256(str(article).encode()).hexdigest()
 nav=s.select_one('[data-ux="Nav"] > ul')
 if nav and not nav.select_one('.static-more'):
  links=nav.select(':scope > li > a')
  secondary=[a for a in links if a.get_text(strip=True) in ['Our Gardens','Calendar','Blog','About','Contact']]
  li=s.new_tag('li',attrs={'class':'nav-item static-more'})
  details=s.new_tag('details',attrs={'class':'more-disclosure'});summary=s.new_tag('summary');summary.string='More';details.append(summary)
  menu=s.new_tag('div',attrs={'class':'more-links'})
  for a in secondary:
   link=s.new_tag('a',href=a['href']);link.string=a.get_text(strip=True)
   if a.get('data-ux')=='NavLinkActive':link['aria-current']='page'
   menu.append(link);a.parent.decompose()
  details.append(menu);li.append(details);nav.append(li)
 drawer=s.select_one('[data-ux="NavigationDrawer"]')
 if drawer:
  drawer['aria-label']='Site navigation'
  for e in drawer.select('[role="menu"],[role="menuitem"]'):del e['role']
  close=drawer.select_one('[data-ux="CloseIcon"]')
  if close:close['aria-label']='Close navigation'
 for a in s.select('[data-ux="Nav"] a,[data-ux="NavigationDrawer"] a'):a.attrs.pop('aria-haspopup',None)
 for region in s.select('.widget-rss'):
  for old in region.select('.static-posts,.blog-listing'):old.decompose()
  full=path==ROOT/'blog/index.html';listing=s.new_tag('div',attrs={'class':'blog-listing'})
  if full:
   filters=s.new_tag('nav',attrs={'class':'blog-filters','aria-label':'Article categories','hidden':''})
   for category in ['All',*sorted({c for p in posts for c in p['categories']})]:
    button=s.new_tag('button',type='button',attrs={'data-blog-category':category,'aria-pressed':'true' if category=='All' else 'false'});button.string=category;filters.append(button)
   listing.append(filters)
  grid=s.new_tag('div',attrs={'class':'blog-cards'})
  for p in posts if full else posts[:3]:
   href=os.path.relpath(ROOT/'blog/f'/p['slug'],path.parent)+'/'
   card=s.new_tag('article',attrs={'class':'blog-card','data-categories':json.dumps(p['categories'])})
   if p['image']:
    link=s.new_tag('a',href=href,attrs={'aria-label':p['title'],'tabindex':'-1'});img=s.new_tag('img',src=os.path.relpath(p['image'],path.parent),alt='',loading='lazy',attrs={'class':'blog-thumbnail'});link.append(img);card.append(link)
   meta=s.new_tag('p',attrs={'class':'blog-meta'});date=s.new_tag('time',datetime=p['date']);date.string=p['date'];meta.append(date)
   if p['categories']:meta.append(' · '+', '.join(p['categories']))
   card.append(meta);heading=s.new_tag('h3');link=s.new_tag('a',href=href);link.string=p['title'];heading.append(link);card.append(heading)
   excerpt=s.new_tag('p');excerpt.string=p['excerpt'];card.append(excerpt)
   link=s.new_tag('a',href=href,attrs={'class':'continue-reading','aria-label':'Continue reading: '+p['title']});link.string='Continue Reading';card.append(link);grid.append(card)
  listing.append(grid)
  if not full:
   p=s.new_tag('p');a=s.new_tag('a',href=os.path.relpath(ROOT/'blog',path.parent)+'/');a.string='View all articles';p.append(a);listing.append(p)
  (region.select_one('section') or region).append(listing)
 # Stale noindex-page/social metadata inherited from About is misleading.
 if s.select_one('meta[name="robots"][content="noindex"]'):
  for e in s.select('meta[property^="og:"],meta[name^="twitter:"],meta[name="description"]'):e.decompose()
 if path==ROOT/'404.html':
  for e in s.select('link[rel="canonical"]'):e.decompose()
 if article:assert hashlib.sha256(str(article).encode()).hexdigest()==hashes[str(path.relative_to(ROOT))]
 path.write_text(str(s))
(ROOT/'_chatgpt/work/phase1-article-hashes.json').write_text(json.dumps(hashes,indent=2))
print('Updated listings and headers; preserved',len(hashes),'article bodies.')
