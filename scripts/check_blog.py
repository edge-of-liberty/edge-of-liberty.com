"""Verify original-URL coverage, article parity and importer overwrite protection."""
import copy, csv
from pathlib import Path
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup as B
from blog_inventory import ROOT, inventory, preflight
_, posts, records=inventory()
manifest=ROOT/'assets/blog-images/image-manifest.tsv'
if not manifest.exists():manifest=ROOT/'_chatgpt/work/blog-image-manifest.tsv'
images={r['original_url']:r['local_file'] for r in csv.DictReader(manifest.open(),delimiter='\t')}
preflight(posts.values(),images)
assert all(r['matched'] for r in records)
for r in records:
    path=ROOT/r['path'].lstrip('/')/'index.html'
    assert path.is_file(),path
    s=B(path.read_text(),'html.parser')
    if r['path'].startswith('/f/'):
        canonical=s.select_one('link[rel="canonical"]')
        assert canonical and canonical['href'].endswith('/blog/f/'+r['slug']+'/')
        assert s.select_one('meta[http-equiv="refresh"]')
index=B((ROOT/'blog/index.html').read_text(),'html.parser')
assert len(index.select('.blog-card') or index.select('.static-posts li'))==len(posts)
for slug in posts:
    s=B((ROOT/'blog/f'/slug/'index.html').read_text(),'html.parser')
    assert s.select_one('.blog-post-nav a[href="../../"]')
    assert not any('wsimg.com' in str(img) for img in s.select('article img'))
urls=[e.text for e in ET.parse(ROOT/'sitemap.xml').findall('.//{*}loc')]
assert {u.rstrip('/').split('/')[-1] for u in urls if '/blog/f/' in u}==set(posts)
assert not any('/f/' in u and '/blog/f/' not in u for u in urls)
changed=copy.deepcopy(next(iter(posts.values())))
changed.find('title').text='An intentionally mismatching title'
try:preflight([changed],images)
except ValueError:pass
else:raise AssertionError('Importer would overwrite differing content')
print(f'PASS: {len(posts)} articles match source text, titles, dates, links and image order; {len(set(r["path"] for r in records))} original paths exist; navigation, canonical sitemap and overwrite protection verified.')
