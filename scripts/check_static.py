"""Read-only route/asset checks and browser checks against a running preview."""
from pathlib import Path
from urllib.parse import urlsplit, unquote, urljoin
from bs4 import BeautifulSoup as B
import re, sys, json
ROOT=Path(__file__).resolve().parents[1]
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765/edge-of-liberty.com/'
files=sorted(p for p in ROOT.rglob('index.html') if not any(x.startswith('.') or x=='_chatgpt' for x in p.relative_to(ROOT).parts))
errors=[]
for f in files:
 s=B(f.read_text(),'html.parser'); refs=[]
 for e in s.select('[href],[src],[srcset]'):
  refs.extend(e[k] for k in ('href','src') if e.get(k))
  if e.get('srcset'):refs.extend(x.strip().split()[0] for x in e['srcset'].split(','))
 for e in s.select('style'):refs.extend(re.findall(r'url\([\"\']?([^\)\"\']+)',e.text))
 for v in refs:
  u=urlsplit(v)
  if not u.scheme and not u.netloc and not v.startswith('#'):
   dest=ROOT/unquote(u.path.lstrip('/')) if v.startswith('/') else f.parent/unquote(u.path)
   if not dest.exists():errors.append(f'{f.relative_to(ROOT)}: missing {v}')
 for e in s.select('script'):
  if e.get('type')!='application/ld+json' and not e.get('src','').endswith('static-site.js'):errors.append(f'{f}: unexpected runtime script')
 assert not s.select('input[type="password"]'),f
assert not errors,'\n'.join(errors)
print('PASS: local links, CSS images, srcset, and script references on',len(files),'routes',flush=True)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome',headless=True)
 context=browser.new_context(viewport={'width':390,'height':850})
 # Isolate the static site from embeds. External embeds are checked separately.
 context.route('**/*',lambda route:route.continue_() if route.request.url.startswith(base) or route.request.url.startswith('data:') else route.abort())
 page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 for f in files:
  path=f.parent.relative_to(ROOT).as_posix();url=base+('' if path=='.' else path+'/')
  response=page.goto(url,wait_until='load');assert response.status==200,(path,response.status)
  refresh=B(f.read_text(),'html.parser').select_one('meta[http-equiv="refresh"]')
  if refresh:
   page.wait_for_url(urljoin(url,refresh['content'].split('url=',1)[1]),wait_until='load')
  # Force all captured images to load, including gallery slides.
  page.locator('img').evaluate_all('(xs)=>xs.forEach(x=>x.loading="eager")')
  page.wait_for_function('Array.from(document.images).filter(x=>x.src.startsWith(location.origin)).every(x=>x.complete)',timeout=20000)
  bad=page.locator('img').evaluate_all('(xs)=>xs.filter(x=>x.src.startsWith(location.origin)&&!x.naturalWidth).map(x=>x.src)')
  if bad:errors.append((path,bad))
  width=page.evaluate('document.documentElement.scrollWidth')
  if width>392:errors.append((path,'mobile overflow',width))
 print('PASS: all',len(files),'routes return 200, local images load, mobile layout fits' if not errors else errors,flush=True)
 page.goto(base,wait_until='load');page.locator('[data-aid="HAMBURGER_MENU_LINK"]').click()
 assert page.locator('[data-ux="NavigationDrawer"]').get_attribute('aria-hidden')=='false'
 assert page.locator('[data-ux="NavigationDrawer"] a[href]').count()>=10
 page.keyboard.press('Escape');assert page.locator('[data-ux="NavigationDrawer"]').get_attribute('aria-hidden')=='true'
 page.set_viewport_size({'width':1440,'height':1000})
 assert page.locator('[data-ux="NavLink"]').first.is_visible()
 assert page.locator('[data-ux="Nav"] a:visible').count()==5
 page.locator('.more-disclosure summary').click()
 assert page.locator('.more-links a:visible').count()==5
 page.keyboard.press('Escape')
 page.screenshot(path=str(ROOT/'_chatgpt/work/static-home-desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':850});page.screenshot(path=str(ROOT/'_chatgpt/work/static-home-mobile.png'),full_page=True)
 page.goto(base+'our-gardens/',wait_until='load');assert page.locator('.static-slide').count()==67
 page.get_by_role('button',name='Next photo').click();assert page.locator('.gallery-position').inner_text()=='2 / 67'
 page.get_by_role('button',name='Previous photo').click();page.get_by_role('button',name='Previous photo').click();assert page.locator('.gallery-position').inner_text()=='67 / 67'
 page.goto(base+'private-tours/',wait_until='load');button=page.locator('.accordion-question').first
 button.click();assert button.get_attribute('aria-expanded')=='true'
 page.goto(base+'contact/',wait_until='load');assert page.locator('a[href="mailto:info@edge-of-liberty.com"]').count()>=1
 assert page.locator('form').count()==0
 page.screenshot(path=str(ROOT/'_chatgpt/work/static-contact.png'),full_page=True)
 page.goto(base+'pay/',wait_until='load')
 assert page.locator('form').get_attribute('action')=='https://www.paypal.com/cgi-bin/webscr'
 assert page.locator('input[name="business"]').input_value()=='paypal@batshitcrazyfarms.com'
 assert page.locator('input[name="return"]').input_value()==page.url
 page.goto(base+'food-trucks/',wait_until='load');assert page.locator('a[href="https://edgeofliberty.us/book"]').count()==6
 browser.close()
assert not errors,errors
print('PASS: desktop/mobile navigation, gallery wraparound, FAQs, contact, PayPal handoff fields, food-truck links')
