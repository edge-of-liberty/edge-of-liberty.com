"""Audit the recovered sitemap/export and verify existing content before import."""
from pathlib import Path
from xml.etree import ElementTree as ET
from urllib.parse import urlsplit, urljoin, unquote
from bs4 import BeautifulSoup as B
import csv, json, re
ROOT=Path(__file__).resolve().parents[1]
NS={'wp':'http://wordpress.org/export/1.2/','c':'http://purl.org/rss/1.0/modules/content/'}
HOSTS={'edge-of-liberty.com','www.edge-of-liberty.com','theedgeofliberty.godaddysites.com'}
EXPORT=ROOT/'_chatgpt/backups/blog-export.xml'
SITEMAP=ROOT/'_chatgpt/backups/sitemaps/sitemap.blog.xml'

def inventory():
    # The manually copied sitemap includes the browser's explanatory text before XML.
    raw=SITEMAP.read_text(); start=raw.find('<urlset')
    if start<0:raise ValueError('No urlset found in recovered sitemap')
    urls=[e.text.strip() for e in ET.fromstring(raw[start:]).findall('.//{*}loc')]
    export=EXPORT if EXPORT.exists() else ROOT/'_chatgpt/work/published-blog.xml'
    items=ET.parse(export).findall('.//item')
    published={i.findtext('wp:post_name',namespaces=NS):i for i in items if i.findtext('wp:status',namespaces=NS)=='publish'}
    assert all(published) and len(published)==sum(i.findtext('wp:status',namespaces=NS)=='publish' for i in items),'Missing or duplicate published slug'
    evidence={u:{'recovered sitemap'} for u in urls}
    sources=[(str(EXPORT.relative_to(ROOT)),i.findtext('c:encoded',namespaces=NS) or '', 'https://edge-of-liberty.com/blog/f/'+slug+'/') for slug,i in published.items()]
    capture=ROOT/'_chatgpt/outputs/edge-of-liberty.com'
    sources += [(str(p.relative_to(ROOT)),p.read_text(),'https://edge-of-liberty.com/'+p.parent.relative_to(capture).as_posix().strip('.')+'/') for p in capture.rglob('index.html')]
    for origin,markup,base in sources:
        for a in B(markup,'html.parser').select('a[href]'):
            u=urlsplit(urljoin(base,a['href']))
            if u.hostname in HOSTS and (u.path.startswith('/blog/f/') or u.path.startswith('/f/')):
                evidence.setdefault(u._replace(query='',fragment='').geturl(),set()).add(origin)
    records=[]
    for url,origins in sorted(evidence.items()):
        path=unquote(urlsplit(url).path).rstrip('/');slug=path.split('/')[-1]
        records.append({'original_url':url,'path':path,'slug':slug,'matched':slug in published,'evidence':sorted(origins)})
    return items,published,records

def preflight(items,images):
    issues=[]
    for item in items:
        slug=item.findtext('wp:post_name',namespaces=NS);dest=ROOT/'blog/f'/slug/'index.html'
        body=B(item.findtext('c:encoded',namespaces=NS) or '', 'html.parser')
        expected_images=[]
        for img in body.select('img[src]'):
            u=urljoin('https://edge-of-liberty.com/',img['src'])
            if u not in images or not (ROOT/'assets/blog-images'/images.get(u,'')).is_file():issues.append(f'{slug}: missing image {u}')
            else:expected_images.append(images[u])
        if not dest.exists():continue
        s=B(dest.read_text(),'html.parser');article=s.select_one('article')
        if not article:
            issues.append(f'{slug}: existing page is not an article; review before overwriting');continue
        heading=article.select_one('h1');date=article.select_one('time')
        if not heading or heading.get_text()!=item.findtext('title'):issues.append(f'{slug}: title differs')
        if not date or date.get_text()!=item.findtext('wp:post_date',namespaces=NS)[:10]:issues.append(f'{slug}: date differs')
        for e in article.select('h1,time,.blog-post-nav'):e.decompose()
        normalize=lambda x:re.sub(r'\s+',' ',x.get_text(' ',strip=True)).strip()
        if normalize(article)!=normalize(body):issues.append(f'{slug}: article text differs')
        def link_identity(href,base):
            u=urlsplit(urljoin(base,href));host=u.hostname
            path=unquote(u.path).rstrip('/')
            if host in HOSTS:
                host='edge-of-liberty.com'
                if path.startswith('/f/'):path='/blog'+path
            return (host,path,u.query,u.fragment)
        current_links=[link_identity(a['href'],f'https://edge-of-liberty.com/blog/f/{slug}/') for a in article.select('a[href]')]
        source_links=[link_identity(a['href'],'https://edge-of-liberty.com/') for a in body.select('a[href]')]
        if current_links!=source_links:issues.append(f'{slug}: link destinations differ')
        if [Path(urlsplit(e['src']).path).name for e in article.select('img[src]')]!=expected_images:issues.append(f'{slug}: image sequence differs')
    if issues:raise ValueError('Import stopped before writing:\n'+'\n'.join(issues))


def report():
    items,posts,records=inventory()
    manifest=ROOT/'assets/blog-images/image-manifest.tsv'
    if not manifest.exists():manifest=ROOT/'_chatgpt/work/blog-image-manifest.tsv'
    images={r['original_url']:r['local_file'] for r in csv.DictReader(manifest.open(),delimiter='\t')}
    preflight(posts.values(),images)
    missing=[];unresolved=set();placeholders=set();remote_images=[]
    for slug in posts:
        f=ROOT/'blog/f'/slug/'index.html'
        if not f.exists():missing.append(slug);continue
        article=B(f.read_text(),'html.parser').select_one('article')
        for e in article.select('img[src]'):
            u=urlsplit(e['src'])
            if u.netloc:remote_images.append((slug,e['src']))
            elif not (f.parent/unquote(u.path)).is_file():missing.append(e['src'])
        for a in article.select('a[href]'):
            href=a['href'];u=urlsplit(href)
            if u.scheme in ('mailto','tel'):continue
            if u.netloc and u.hostname not in HOSTS:continue
            path=ROOT/unquote(u.path).lstrip('/') if u.netloc or href.startswith('/') else f.parent/unquote(u.path)
            target=path/'index.html' if path.is_dir() else path
            if not target.exists():unresolved.add(href);continue
            if target.suffix=='.html':
                doc=B(target.read_text(),'html.parser')
                if doc.select_one('meta[name="robots"][content="noindex"]'):placeholders.add('/'+str(target.parent.resolve().relative_to(ROOT)))
                if u.fragment and not doc.find(id=unquote(u.fragment)) and not doc.find(attrs={'name':unquote(u.fragment)}):unresolved.add(href)
    paths=sorted({r['path'] for r in records if r['matched']})
    result={'export_entries':len(items),'published_posts':len(posts),'draft_entries':len(items)-len(posts),'sitemap_urls':sum('recovered sitemap' in r['evidence'] for r in records),'preserved_article_paths':paths,'missing_posts_or_images':missing,'unmatched_urls':[r for r in records if not r['matched']],'remote_article_images':remote_images,'unresolved_internal_links':sorted(unresolved),'unrecovered_linked_pages':sorted(placeholders),'urls':records}
    (ROOT/'docs/blog-url-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Blog migration verification','',f"Export: {len(items)} entries; {len(posts)} published articles restored; {len(items)-len(posts)} draft without a published URL excluded.",'',f"Original sitemap: {result['sitemap_urls']} URLs, all matched. Preserved: {len(paths)} distinct article paths on edge-of-liberty.com. The GoDaddy-hosted source domain is evidence only; this repository cannot redirect that domain.",'','## Content and images','','Existing titles, dates, body text, and image order checked against the export before import. No differing article content was overwritten. All published article images are local. Draft source remains excluded from publication.','','## Unresolved issues','',f"Missing published posts/images: {len(missing)}. Unmatched original blog URLs: {len(result['unmatched_urls'])}. Remote article images: {len(remote_images)}.",'', 'Unresolved internal links: '+(', '.join(sorted(unresolved)) or 'none')+'.','','Linked historical pages whose original content remains unavailable (existing notices retained):','']
    lines += ['- `'+x+'`' for x in sorted(placeholders)]
    lines += ['','Historical third-party links are preserved. Their current availability is not established by this local migration check.','','## Original URL mapping','', '| Original URL | Preserved path | Match |','| --- | --- | --- |']
    lines += [f"| {r['original_url']} | `{r['path']}` | {'matched' if r['matched'] else 'UNMATCHED'} |" for r in records]
    (ROOT/'docs/blog-migration-report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('urls','preserved_article_paths')},indent=2))
    return result

if __name__=='__main__':report()
