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
