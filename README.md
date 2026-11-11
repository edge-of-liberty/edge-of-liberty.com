# Edge of Liberty static site

Static replacement for the captured GoDaddy site. GitHub Pages publishes `main` from the repository root. GitHub Pages uses its built-in Jekyll step to copy the static HTML and apply `_config.yml` publication exclusions; no application framework is required. Keep DNS and GoDaddy subscriptions unchanged until Nancy authorizes cutover.

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

`scripts/import_blog.py` uses `_chatgpt/backups/blog-export.xml` when present, otherwise the preserved published-only XML. It inventories `_chatgpt/backups/sitemaps/sitemap.blog.xml` and captured links, verifies existing article text/titles/dates/links/image order before writing, preserves each page’s existing shell, and stops on differing content. It never imports draft posts. The full export is ignored because it contains unpublished content. Published article source and image mappings are preserved separately for reproducibility.

## Remaining review items

- Historic pages `/about-bella-lena`, `/crafters%3A-bella-lena`, `/open-farm-vendors`, and `/2021-pcmga-garden-walk` have no recovered standalone content; their URLs display honest availability notices. `/ols/products` likewise has no captured store content.
- Some vendor sites and the old registration form linked from historical articles are no longer publicly available. Original article text and links are preserved; do not invent replacement destinations.
- Current visitor schedules use the approved 2027 season; historical article dates and historic pricing are preserved.
- Confirm mailbox delivery and perform a user-supervised PayPal checkout check before final cutover. Link checks do not establish email delivery or successful payment.
- The custom-domain configuration and GitHub Pages DNS were added outside this migration session. The github.io URL redirects to the live domain. Preserve CNAME and DNS; publication to main updates the live site. Nancy has authorized changes to go live.

Use command-line Git with the existing SSH authentication. Do not use GitHub Desktop.

## Blog migration audit (November 11, 2026)

All 26 sitemap articles match the 26 published export entries. The 27th export entry is an unpublished draft without a slug. Preserved 27 distinct article paths: 26 canonical `/blog/f/` paths and the historical `/f/july-2020-update` alias. Article navigation includes newer/older posts and the index. All 142 article image assets are local.

Run `.venv-migration/bin/python -B scripts/check_blog.py` for source parity, route coverage, sitemap, navigation, and overwrite protection checks. Run `scripts/blog_inventory.py` to refresh [the detailed report](docs/blog-migration-report.md) and [URL inventory](docs/blog-url-inventory.json). One old garden-section anchor and four unrecovered non-blog destinations remain explicitly documented; no content was invented.

## Phase 1 closeout (local commit only)

Blog listing cards use the published export's thumbnails, dates, categories and excerpts; `scripts/phase1_presentation.py` updates listings and headers without regenerating article bodies. Run it after any future deliberate blog import. Primary navigation has five links plus a native More disclosure. Current visitor schedules are Sundays, May 9–October 31, 2027, 10 am–3 pm; historical article dates and product-vintage labels are unchanged.

The root `.nojekyll` bypass was removed so `_config.yml` can exclude backups, migration scripts/docs and unused GoDaddy bundles from the next Pages build. No contact exports or credentials were found among tracked publication files. Existing public repository history is not erased by these exclusions. No push/deployment was performed for this closeout.

Manual checks: keyboard/touch More menu and mobile drawer; Blog category buttons; Google Calendar on Calendar/Event Details (including actual 2027 events); craft-fair iframe and booking destination; garden YouTube/Flickr/Google Sheet; contact mailbox delivery and PayPal handoff. The external Batshit Crazy Farms storefront still uses GoDaddy storefront URLs—keep its hosting if those purchase links are needed. Confirm domain email is not part of a service being canceled. The informational account/appointment URLs no longer provide those retired services. The known old garden fragment and four unavailable historical page bodies remain documented in the existing blog report.

The single local closeout pass found remote touch icons, three service-page canonicals pointing to Home, and retired appointment anchors. These were corrected with existing local icons, page-specific canonicals and the existing Contact page. No browser, network or deployment tests were performed. The updated publication exclusions take effect only after the next authorized push/build.
