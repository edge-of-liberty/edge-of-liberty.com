# Edge of Liberty migration handoff

## November 4, 2026

The repository root holds the GitHub Pages preview. The session snapshot is in `_chatgpt/outputs/edge-of-liberty.com/`. The adjacent URL inventory records results by source URL. The work directory contains crawl inputs, archive captures, recovery scripts, and local test results. The Python environment can be recreated from requirements.txt.

The capture includes 19 live HTML routes and two archived craft fair articles (September and October 2022), with 478 local assets. All checked local link, image, and script targets resolved. The home page loaded at 390 and 1440 pixels, and the mobile drawer opened.

## Open work

Recover 24 missing articles from the GoDaddy editor or backup. The public blog endpoints returned server errors and the listed store URL returned 404. Verify galleries, calendars, payments, contact delivery, member accounts, and bookings before cutover. Keep DNS and GoDaddy service in place until the replacement is verified. The craft fair site is a separate repository.

## Continuing on another computer

Clone or pull this repository. Serve the root with a local web server to preview it. Update this handoff with each migration milestone. Existing archive files are tracked. To share a new file under the ignored _chatgpt directory, explicitly add it with git add -f. Pages publishes from main at the repository root. The archive is public repository material.

## Editor setup and publication checkpoint

Nancy's existing BCF workspace on the Mac is at `~/createhappinesshouse.com/BCF.code-workspace`. It now lists createhappinesshouse.com, edgeofliberty.us, and edge-of-liberty.com. Use the last folder for this migration. A separate Local Repositories workspace was also created and is unnecessary. To add another clone in BCF, use File → Add Folder to Workspace. On another Mac, place the three clones side by side if using the same workspace definition.

Nancy created the public repository and enabled Pages. At handoff, GitHub main was still at 28d0b37, before the local site capture fecf755. HTTPS and SSH push attempts lacked working authentication. The Pages address responded, but that did not verify deployment of the migration. Next, push local main from an authenticated GitHub Desktop session, then verify the remote commit and test the published preview at https://edge-of-liberty.github.io/edge-of-liberty.com/ before any cutover. No DNS change or cancellation was performed.

## November 6, 2026 — static migration continuation

Nancy approved static implementation and a GitHub Pages preview, without DNS changes or subscription cancellation. Accounts/login/registration/appointment systems are intentionally not recreated. Confirmed public contacts: info@edge-of-liberty.com, tours@edge-of-liberty.com, 219-242-8320. Food-truck links now use her specified https://edgeofliberty.us/book destination.

Command-line SSH authentication works as ncalafati. Nancy explicitly prohibits GitHub Desktop; use command-line Git only. At continuation, local and remote main were 3c024cb, containing the prior static work plus a CNAME added separately. The github.io preview redirects to the custom domain; permission to remove that custom-domain setting for an independent preview was requested and is pending.

Imported all 26 published blog posts from the newly supplied export, recovering all 24 previously missing articles. One draft was excluded. Original full XML remains local/ignored; published-only XML and a mapping for 142 article images are retained under work. Both original archived captures remain untouched.

Static runtime replaces GoDaddy navigation/gallery/FAQ behavior. Both galleries use local originals (67 garden-walk and three farm-stand photos). Calendar uses the original public Google calendar directly. Contact is email/telephone links; no invented form backend. PayPal handoff parameters are retained; no payment submitted. Service URLs retain descriptions and explain the absence of online bookings. Account URLs show notices. Historic standalone pages without recovered content show notices rather than fabricated content.

The full 51-route browser check passed before adding two historical URL aliases; final checks and publication status will be recorded after completion. External link check results remain in work/external-links.json. README now documents local preview, validation, source regeneration limitations, and outstanding content/payment/mailbox review.

Final validation: all 53 routes, local images, CSS/srcset references, mobile width, navigation, galleries, FAQs, contact links, food-truck links, and PayPal handoff fields passed. Recovered article typography/background was visually checked and repaired. No real email or payment was sent.

DNS inspection found the domain already points to GitHub Pages (185.199.108–111.153). This was an external change; do not remove CNAME. The earlier request to remove CNAME was superseded by a request to either publish to the now-live domain or retain a review branch/local preview. Preserve DNS and subscriptions.

## Publication authorization

Nancy confirmed that any changes should go live. Keep CNAME and DNS unchanged. The tested migration is approved for publication to main through command-line Git. Commit 6090caf contains all recovered published articles and passed the 53-route validation.

## November 11, 2026 — blog migration finished

Compared the manually recovered sitemap (including its browser-generated preface) with all 27 export entries and existing article contents. All 26 published posts match the sitemap; the remaining draft has no slug and stays unpublished. Preserved 27 distinct article routes, including the evidenced /f/july-2020-update alias. Rebuilt the existing index, added newer/older/index navigation, and excluded redirect aliases from the canonical sitemap. All 142 blog images are local.

Importer now checks existing text, title, date, links and image order before writing and preserves each existing page shell. Detailed results and source URL mapping are in docs/blog-migration-report.md and docs/blog-url-inventory.json. No missing published posts, unmatched blog URLs, or broken local images. One old garden-section fragment (used in three posts) and four linked non-blog pages without recovered content remain unresolved. Do not invent their content. DNS/design unchanged. Changes are authorized to go live using command-line Git.
