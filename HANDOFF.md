# DecisionLens handoff — completed local pilot delivery

Updated 2026-11-05, Asia/Kolkata. Start here when the user says continue.

## Where the work is
- Upgraded repository: this folder, outputs/DecisionLens.
- Original commit: 7eedad4fe46033fb1951b9cb6d9bf8d1c96f63dc.
- Full original Git history remains in .git and history/original-rag-chatbot.bundle.
- Unchanged original code is in legacy/; docs/ORIGINAL_* preserves prior documentation.
- Repository publication authorized 2026-11-05: upload the complete upgrade to adityahaa/Rag_chatbot.
- No live deployment or paper submission is authorized or performed.
- Prepared environment: ../../work/.venv; models are already in models/ (both public checkpoints).
- Start-Here.cmd or Start.ps1 uses this prepared environment; on another computer run Setup.ps1.
- Source deliverable: ../DecisionLens-source.zip; scripts/package_source.py rebuilds it.

## Completed application
Responsive local dashboard, product evidence matrix, page/section provenance, dates/URLs,
missing/differing values, user edits and review notes, priorities and conditional scores with
weighted coverage, edited brief and CSV/JSON/Markdown export. Multiple text PDFs, TXT/MD,
CSV/JSON and DOCX supported with limits and explicit scanned-file errors. Runtime is local,
no key or billing. Original Streamlit entry workflow retained and tested. Public SaaS notes
and explicitly fictional demo are selectable. No automatic vendor winner is declared.

## Verification
19 tests passed (one upstream AnyIO deprecation warning). pip check and JS syntax pass.
Streamlit AppTest passes. Real browser uploaded beacon-synthetic.pdf, inspected SSO at page 1,
reviewed a fictional conflict, rated a criterion with 30% coverage, searched local embeddings,
edited and downloaded Markdown and CSV. Downloads and screenshots are in docs/. Narrow layout
was inspected at actual CSS width 488 and normal viewport restored. Native confirmation and
one download-event watcher had browser automation failures; direct downloads and a fresh tab
recovered the preview display; later automated clicks remained unresponsive after the native
confirmation. Final localhost API demo and served-JS checks passed. Use a normal Windows
browser if the in-app preview is unresponsive. See docs/VERIFICATION.md for exact scope; do not call failed interactions successful.

## Frozen experiments — do not retune or rerun without a reason
Protocol: research/PROTOCOL.md, saved before held-out evaluation (not external preregistration).
Final run: research/runs/20261104T204725_905751Z, local date 2026-11-05.
151 held-out cases x five retrieval methods = 755 completed measurements, zero execution failures.
Development run: 20261104T071859_329995Z, 55 cases x five = 275.
18 real local FLAN-T5-small generations; raw strings, token counts and timings saved.
Source code snapshot in final run predates later application UX/null-handling repairs; retrieval
methods/settings were not tuned after results. Latest-run pointer identifies the held-out run.
Independent validation reconstructs all saved retrieval memberships and mean recall, with zero
split-group overlap. It does not validate semantic labels. No model was trained from scratch.

## Actual findings and limits
- AWS downloaded 14,718 records. Only 6,685 fit explicit per-product schema; other schemas
  are adapter exclusions, not proven dataset errors. Select 20 dev + 60 eval signatures.
  All methods reach 100% on this easy short-record task: no superiority/real-world accuracy claim.
- RAG-Multi-Corpus pinned at 39071af3f4dd25e59f5c59a6f9b6e8e99cd643b3, MIT synthetic.
  Actual QA CSV: 1,252 rows. Cloudway subset: 37 airline docs, 164 questions; 46 pass strict
  normalized support-span checks. Split 15 dev/31 eval. Semantic source hit: 28/31; hybrid 30/31.
  All selected held-out questions have one gold filename. Not a SaaS correctness benchmark.
- Controlled synthetic: 5 dev/15 held-out groups, four evidence conditions each.
  Plain/hybrid recall 78.3% on 45 evidence-bearing cases; diversity 52.2% (negative result).
  Conflict recall 0/15 for every method. k=3 budget cannot contain four/five required facts.
  UI all-document conflict flags are different from this top-k limitation.
- FLAN: all nine answerable outputs are citation-like strings (zero exact matches), nine
  absent outputs say unanswerable. Frozen abstention phrase list omitted that word; report
  this measurement defect, do not silently fix/rebrand metrics. Optional generator stays experimental.
- Dated GitHub/GitLab public case uses short AI-assisted notes, not independently reviewed
  labels. Source publication dates unknown; source links/access date retained. No vendor winner.

## Deliverables
README.md for beginner Windows setup; docs/BASELINE_AUDIT.md and VERIFICATION.md;
research/DATA_AUDIT.md, PROTOCOL.md, LITERATURE.md, RESULTS.md, PAPER_DRAFT.md;
reproducible download/prepare/run/plot/validate scripts, full raw measurement records and
standalone PNG/SVG figures. Package excludes model binaries, environments, raw/derived datasets,
credentials and private uploads; includes the original history bundle and license notices.

## What remains / genuine blockers
No blocker to local use. Original Gemini path is not provider-verified; deprecated embedding
ID is documented. No cloud credential was requested, no paid fallback used. Do not run the
archived insecure provider workflow as a supported app. No key needs to be pasted into chat.
Before a defensible paper: harder licensed real distributed-evidence cases; independent
annotations/semantic review; stronger free local generation and development-only metric repair;
a newly frozen evaluation set; uncertainty and user-utility study; supervisor/author/venue review.
Pilot paper draft is explicitly incomplete for submission. Shared deployment still needs auth,
durable authorized storage and worker/retention controls (docs/DEPLOYMENT.md).

## Resume rules
Reuse saved models, data, results and checks. Do not repeat final experiments just to regenerate
charts or prose. A new method prompted by these results needs new held-out cases. Rebuild the
source ZIP only after changed deliverables. Never claim mock/offline checks as cloud calls or AI
review as independent human assessment. User budget remains zero.
