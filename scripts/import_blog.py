"""Import published articles from Nancy's local export; never publish drafts."""
from pathlib import Path
from bs4 import BeautifulSoup as B
from xml.etree import ElementTree as ET
from urllib.parse import urlsplit, urljoin, unquote, quote
import csv, os, json, html
ROOT=Path(__file__).resolve().parents[1]
NS={'wp':'http://wordpress.org/export/1.2/','c':'http://purl.org/rss/1.0/modules/content/','e':'http://wordpress.org/export/1.2/excerpt/'}
from blog_inventory import inventory, preflight, report
source=ROOT/'_chatgpt/backups/blog-export.xml'
if not source.exists():source=ROOT/'_chatgpt/work/published-blog.xml'
items=[i for i in ET.parse(source).findall('.//item') if i.findtext('wp:status',namespaces=NS)=='publish' and i.findtext('wp:post_name',namespaces=NS)]
manifest=ROOT/'assets/blog-images/image-manifest.tsv'
if not manifest.exists():manifest=ROOT/'_chatgpt/work/blog-image-manifest.tsv'
images={r['original_url']:r['local_file'] for r in csv.DictReader(manifest.open(),delimiter='\t')}
# Complete preflight before any page writes; reject diverging article content.
preflight(items,images)
_, _, original_urls=inventory()
assert all(r['matched'] for r in original_urls), 'Unmatched original URLs require review'
used={}; posts=[]
template=(ROOT/'blog/f/edge-of-liberty-craft-fair---october-16-2022/index.html').read_text()
for item in items:
 slug=item.findtext('wp:post_name',namespaces=NS);assert '/' not in slug and slug not in ('.','..')
 title=item.findtext('title');date=item.findtext('wp:post_date',namespaces=NS)[:10]
 dest=ROOT/'blog/f'/slug/'index.html';s=B(dest.read_text() if dest.exists() else template,'html.parser')
 article=s.select_one('article');assert article
 if 'background-color:#fff' not in article.parent.get('style',''):
  article.parent['style']=article.parent.get('style','')+';background-color:#fff;'
 article['class']=['static-article']
 body=B(item.findtext('c:encoded',namespaces=NS) or '', 'html.parser')
 for e in body.select('script'):e.decompose()
 for e in body.select('*'):
  for key in list(e.attrs):
   if key.startswith('on'):del e[key]
 for img in body.select('img'):
  url=urljoin('https://edge-of-liberty.com/',img['src'])
  assert url in images,url
  p=ROOT/'assets/blog-images'/images[url];assert p.exists(),p
  used[url]=images[url];img['src']='../../../assets/blog-images/'+images[url]
  img['loading']='lazy';img['alt']=img.get('alt','');img.attrs.pop('srcset',None)
 for a in body.select('a[href]'):
  if a['href'].startswith('#'):continue
  u=urlsplit(urljoin('https://edge-of-liberty.com/',a['href']))
  if u.hostname in ('edge-of-liberty.com','www.edge-of-liberty.com','theedgeofliberty.godaddysites.com'):
   route=unquote(u.path).strip('/')
   if route=='f/july-2020-update':route='blog/f/july-2020-update'
   target=ROOT/route
   if (target/'index.html').exists() or route.startswith('blog/f/'):
    a['href']=os.path.relpath(target,dest.parent)+'/'+('?' + u.query if u.query else '')+('#'+u.fragment if u.fragment else '')
  if a.get('target')=='_blank':a['rel']='noopener noreferrer'
 article.clear()
 h=s.new_tag('h1');h.string=title;article.append(h)
 t=s.new_tag('time',datetime=date);t.string=date;article.append(t)
 for child in list(body.contents):article.append(child.extract())
 s.title.string=title+' | The Edge of Liberty'
 for meta in s.select('meta[name="robots"]'):meta.decompose()
 for meta in s.select('meta[property],meta[name]'):
  key=meta.get('property',meta.get('name'))
  if key in ('og:title','twitter:title'):meta['content']=title
  if key in ('description','og:description','twitter:description'):meta['content']=item.findtext('e:encoded',namespaces=NS) or ''
  if key in ('og:image','twitter:image'):
   first=article.select_one('img');meta['content']='https://edge-of-liberty.com/assets/blog-images/'+Path(first['src']).name if first else ''
  if key=='og:url':meta['content']='https://edge-of-liberty.com/blog/f/'+slug+'/'
 for canonical in s.select('link[rel="canonical"]'):canonical['href']='https://edge-of-liberty.com/blog/f/'+slug+'/'
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(str(s));posts.append({'slug':slug,'title':title,'date':date})
posts.sort(key=lambda x:x['date'],reverse=True)
# Preserve every evidenced /f/ route as a static redirect to its canonical article.
for record in original_urls:
 if not record['path'].startswith('/f/'):continue
 target=ROOT/record['path'].lstrip('/')/'index.html'
 destination=ROOT/'blog/f'/record['slug']
 if target.exists():
  existing=B(target.read_text(),'html.parser')
  refresh=existing.select_one('meta[http-equiv="refresh"]')
  assert refresh and record['slug'] in refresh.get('content',''), 'Unexpected alias content: '+str(target)
 href=os.path.relpath(destination,target.parent)+'/'
 markup='<!doctype html><html lang="en"><head><meta charset="utf-8"><title>'+html.escape(next(p['title'] for p in posts if p['slug']==record['slug']))+'</title><meta http-equiv="refresh" content="0;url='+href+'"><link rel="canonical" href="https://edge-of-liberty.com/blog/f/'+record['slug']+'/"></head><body><p><a href="'+href+'">Continue to the article</a></p></body></html>'
 target.parent.mkdir(parents=True,exist_ok=True);target.write_text(markup)
for n,post in enumerate(posts):
 dest=ROOT/'blog/f'/post['slug']/'index.html';s=B(dest.read_text(),'html.parser')
 article=s.select_one('article')
 for old in article.select('.blog-post-nav'):old.decompose()
 nav=s.new_tag('nav',attrs={'class':'blog-post-nav','aria-label':'Blog articles'})
 links=[]
 if n>0:links.append(('Newer: '+posts[n-1]['title'],'../'+posts[n-1]['slug']+'/'))
 links.append(('All articles','../../'))
 if n+1<len(posts):links.append(('Older: '+posts[n+1]['title'],'../'+posts[n+1]['slug']+'/'))
 for label,href in links:
  paragraph=s.new_tag('p');a=s.new_tag('a',href=href);a.string=label;paragraph.append(a);nav.append(paragraph)
 article.append(nav);dest.write_text(str(s))
for dest in [ROOT/'index.html',ROOT/'blog/index.html',*list((ROOT/'ola').rglob('index.html'))]:
 s=B(dest.read_text(),'html.parser')
 for w in s.select('.widget-rss'):
  for old in w.select('.static-posts'):old.decompose()
  ul=s.new_tag('ul',attrs={'class':'static-posts'})
  for post in (posts if dest==ROOT/'blog/index.html' else posts[:3]):
   li=s.new_tag('li');a=s.new_tag('a',href=os.path.relpath(ROOT/'blog/f'/post['slug'],dest.parent)+'/');a.string=post['title'];li.append(a);ul.append(li)
  if dest!=ROOT/'blog/index.html':
   li=s.new_tag('li');a=s.new_tag('a',href=os.path.relpath(ROOT/'blog',dest.parent)+'/');a.string='All articles';li.append(a);ul.append(li)
  (w.select_one('section') or w).append(ul)
 dest.write_text(str(s))
# Preserve only published source data in the public reproducible archive.
r=ET.Element('rss');ch=ET.SubElement(r,'channel')
for item in items:ch.append(item)
ET.ElementTree(r).write(ROOT/'_chatgpt/work/published-blog.xml',encoding='utf-8',xml_declaration=True)
with (ROOT/'_chatgpt/work/blog-image-manifest.tsv').open('w') as fp:
 writer=csv.writer(fp,delimiter='\t',lineterminator='\n');writer.writerow(['local_file','original_url']);writer.writerows((v,k) for k,v in sorted(used.items()))
(ROOT/'_chatgpt/work/imported-posts.json').write_text(json.dumps(posts,indent=2))
ns='http://www.sitemaps.org/schemas/sitemap/0.9';doc=ET.Element('urlset',xmlns=ns)
for f in sorted(ROOT.rglob('index.html')):
 if any(p.startswith('.') or p=='_chatgpt' for p in f.relative_to(ROOT).parts):continue
 doc_page=B(f.read_text(),'html.parser')
 if doc_page.select_one('meta[name="robots"][content="noindex"],meta[http-equiv="refresh"]'):continue
 route=f.parent.relative_to(ROOT).as_posix();ET.SubElement(ET.SubElement(doc,'url'),'loc').text='https://edge-of-liberty.com/'+('' if route=='.' else quote(route,safe='/')+'/')
ET.ElementTree(doc).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
print('Imported',len(posts),'published articles and',len(used),'local images; drafts excluded.')

report()
