# Edge of Liberty static site

Static replacement for the captured GoDaddy site. GitHub Pages publishes `main` from the repository root. No build is required for hosting. Keep DNS and GoDaddy subscriptions unchanged until Nancy authorizes cutover.

## Current content

- Original captured layout, navigation, content, and local images.
- 26 published blog articles recovered from Nancy's export, at their original `/blog/f/.../` URLs. The unpublished draft is excluded.
- Local galleries: 67 garden-walk photos and three farm-stand photos.
- Direct Google Calendar embed and existing calendar subscription links.
- Contact uses confirmed email/telephone links: info@edge-of-liberty.com, tours@edge-of-liberty.com, 219-242-8320. No form submission backend.
- Food-truck reservation links use Nancy's approved https://edgeofliberty.us/book destination.
- Existing PayPal form remains a direct handoff. No payment was submitted during testing.
- GoDaddy account, registration, and appointment engines are retired. Existing account/service URLs remain as informational pages.

## Local preview and validation

From this checkout:

```sh
python3 -m venv .venv-migration
.venv-migration/bin/pip install -r _chatgpt/requirements.txt
.venv-migration/bin/python -B -m http.server 8766 --bind 127.0.0.1
```

Open http://127.0.0.1:8766/ and run:

```sh
.venv-migration/bin/python -B scripts/check_static.py http://127.0.0.1:8766/
```

Browser validation uses an installed Google Chrome through Playwright. It checks local references (including CSS and responsive images), routes, mobile width, images, desktop/mobile navigation, gallery controls, FAQs, contact links, and PayPal handoff fields. External embeds are checked separately; blocking third-party requests during the route test confirms the static pages do not need GoDaddy runtime services.

## Source and recovery

The original capture is preserved in `_chatgpt/outputs/edge-of-liberty.com/`. Never edit or recrawl it for routine site changes. Current HTML files are the deployed site.

`scripts/static_migration.py` recreates the initial static conversion from the original snapshot, overwriting converted HTML. **It is not a routine build command.** If deliberately regenerating, follow it with `scripts/import_blog.py` to restore all 26 published articles. Review the diff before committing. Gallery configuration and asset mappings are retained in `_chatgpt/work/`.

`scripts/import_blog.py` uses local `blog-export.xml` when present, otherwise the preserved published-only XML. It never imports draft posts. The full export is ignored because it contains unpublished content. Published article source and image mappings are preserved separately for reproducibility.

## Remaining review items

- Historic pages `/about-bella-lena`, `/crafters%3A-bella-lena`, `/open-farm-vendors`, and `/2021-pcmga-garden-walk` have no recovered standalone content; their URLs display honest availability notices. `/ols/products` likewise has no captured store content.
- Some vendor sites and the old registration form linked from historical articles are no longer publicly available. Original article text and links are preserved; do not invent replacement destinations.
- Existing season dates, opening-hour differences, and historic pricing are preserved, not editorially revised.
- Confirm mailbox delivery and perform a user-supervised PayPal checkout check before final cutover. Link checks do not establish email delivery or successful payment.
- The custom-domain configuration and GitHub Pages DNS were added outside this migration session. The github.io URL redirects to the live domain. Preserve CNAME and DNS; publication to main updates the live site. Nancy has authorized changes to go live.

Use command-line Git with the existing SSH authentication. Do not use GitHub Desktop.
