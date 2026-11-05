# Original baseline audit and repair

Inspected README, verification notes and both actual modules at full commit
`7eedad4fe46033fb1951b9cb6d9bf8d1c96f63dc`.
The baseline is preserved byte-for-byte in `legacy/`; original documentation copies
are named `ORIGINAL_*`. Existing authorship and history are retained. No upstream push.

| Original behavior / finding | Current repair / evidence |
| --- | --- |
| PDFs parsed into unlocated plain text; filename metadata constructed then not passed to Chroma | Page/section-preserving parser and metadata-bearing chunks; tests verify text-PDF page 1, filenames, source URLs and dates |
| Shared persistent Chroma directory allows stale/co-mingled indexes | Session-owned in-memory document sets and indexes; separate-client isolation tested |
| API key stored in process environment and provider SDK global state | No credentials required or handled in the shipped app; local models only |
| Temporary PDFs can be left after failed processing | Parse in-memory bytes; uploads are closed even on failures; no uploaded files persisted |
| Experimental Gemini generation ID and old embedding default | Archived unchanged. Local semantic baseline proxy and optional pretrained local generation actually executed |
| Old retriever API and `vectorstore.persist()` rely on unpinned LangChain/Chroma behavior | Minimal local retrieval abstraction with pinned tested dependencies and exact environment lock; no LangChain/Chroma integration claim |
| No ground truth or measured complete run | Frozen pilot, raw results and browser document-to-export record supplied; external provider remains untested |
| Prompt-only grounding instruction | Explicitly state limitations; default UI shows source excerpts rather than generated factual claims |

The original embedding ID is listed as shut down on January 14, 2026 in Google's
[official deprecation page](https://aistudio.google.com/docs/deprecations), checked 2026-11-04.
The exact archived experimental generation ID was not verified with the provider.
Public documentation is an availability check, not a successful API-call test.
No live cloud provider call was made; no suitable credential was available in the checked
environment-variable names, and no private key was requested. No paid fallback or account
activation was attempted. Local model inference is a separate, recorded path.

The preserved Streamlit workflow still launches `rag_streamlit.py`, now with local parsing,
comparison, retrieval and export. Full evidence edits, criterion ratings and decision briefs
live in the main dashboard. The old archive is historical evidence, not a supported secure
deployment entry point. Baseline quality cannot be causally compared with the original provider
because the embedding, generation and indexing implementations changed.
