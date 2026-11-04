from pathlib import Path
import json,requests
from bs4 import BeautifulSoup
for p,v in json.load(open('work/archives.json')).items():
 if isinstance(v,dict) and v.get('closest'):
  u=v['closest']['url'].replace('http://web','https://web').replace(v['closest']['timestamp']+'/',v['closest']['timestamp']+'id_/')
  try:
   r=requests.get(u,timeout=20);print(p,r.status_code,len(r.content));r.raise_for_status();Path('work/'+p.split('/')[-1]+'.archive').write_bytes(r.content)
  except Exception as e:print(str(e))
