from playwright.sync_api import sync_playwright
from pathlib import Path
import threading,http.server,functools
h=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory='outputs'))
threading.Thread(target=h.serve_forever,daemon=True).start()
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome',headless=True)
 for w in (390,1440):
  page=b.new_page(viewport={'width':w,'height':850})
  page.goto(f'http://127.0.0.1:{h.server_port}/edge-of-liberty.com/',wait_until='domcontentloaded')
  page.wait_for_timeout(1200)
  print(w,page.title(),page.evaluate('document.documentElement.scrollWidth'),page.locator('img').evaluate_all('(a)=>a.filter(x=>!x.naturalWidth).map(x=>x.src)').__str__()[:150],flush=True)
  if w==390:
   page.locator('[data-ux=IconHamburger]').first.click(timeout=4000);page.wait_for_timeout(550);print('drawer',page.locator('[data-ux=NavigationDrawer]').bounding_box())
  page.close()
