# Verification record — 2026-11-05, Asia/Kolkata

## Actually completed

Python 3.11.9, Windows, CPU runtime. Pinned environment installed and `pip check` passed.
`node --check static/app.js` passed. Tests cover readable and empty PDFs, damaged/unsupported
inputs, JSON/CSV/DOCX, source metadata, unknowns, conflicts, reviewed weighted scoring,
session isolation, source links, CSV formula escaping, duplicate uploads and export edits.
Public SaaS note loading and JSON null-versus-zero behavior are checked. Final result:
**19 passed**, one non-failing upstream AnyIO deprecation warning, in 2.22 seconds.
Streamlit AppTest loaded the original entry filename and its local synthetic demo successfully.

Browser walkthrough used the actual running local server, not a static HTML file or mocked
provider. Steps observed: synthetic demo load; two conflicting price excerpts; manual review
resolution; a user-assigned rating of 75 with 30% weighted coverage and no automatic winner;
hybrid search displaying original passages; upload of a real text-based PDF test fixture;
Beacon SSO excerpt at page 1; an edited decision brief; downloaded CSV and Markdown contents.
Synthetic downloaded files are saved as `browser-walkthrough-*` in this folder.

The public SaaS case also loaded with two scoped product tiers, original URLs, unknown dates,
missing attributes and a flag for complementary limitation notes. A narrow viewport was
requested at 390×844; the browser reported CSS width 488. At that measured width, the page
fit its viewport and the wider comparison table remained horizontally scrollable. Normal
viewport was restored. Screenshots: `dashboard.jpg`, `pdf-evidence.jpg`, `mobile.jpg`.

One browser download-event wait timed out; the supported direct link download method then
retrieved the CSV and edited Markdown successfully. A later native confirmation stalled the
old test tab; a fresh tab in the same browser recovered the local preview. No lost private data
or provider failure was involved. A fresh localhost tab displayed the final build; subsequent
automated clicks still had no effect after the stalled native confirmation. This is an unresolved
in-app-browser control limitation. Use a normal Windows browser at localhost if the preview
does not respond. The earlier input-to-download walkthrough was completed before that stall.
These automation issues are not counted as successful interactions.

Real local models were executed: MiniLM in 755 held-out retrieval runs plus development,
and FLAN-T5-small in 18 held-out generations. A separate actual `/api/ask` request returned
HTTP 200 with three candidate chunks, 317 input tokens, 55 output tokens and an off-topic
generated answer; local generator inference works technically but its answer quality is weak.
Its recorded latency was approximately 7,750 ms (including first model load).

## Deliberately unclaimed

No current Gemini credentialed call, paid API, independent human annotation, external
deployment, OCR, multi-user production hardening, complete semantic extraction or prompt-injection
elimination was tested. Unit/API tests are local software checks, not cloud-provider checks.
Original exact-provider baseline is unverified; see BASELINE_AUDIT.md. Research measures
have their own narrow labels and denominators in `research/RESULTS.md`.
