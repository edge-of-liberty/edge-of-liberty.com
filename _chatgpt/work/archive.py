exec(open('work/build.py').read().split('pages={}')[0])
def check(p):
 try:
  j=requests.get('https://archive.org/wayback/available',params={'url':base+p},timeout=16).json();return p,j.get('archived_snapshots')
 except Exception as e:return p,str(e)
Path('work/archives.json').write_text(json.dumps(dict(cf.ThreadPoolExecutor(8).map(check,[p for p in urls if '/f/' in p])),indent=2))
