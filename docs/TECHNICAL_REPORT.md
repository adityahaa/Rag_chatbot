# DecisionLens implementation report

The upgraded app separates local parsing, retrieval, literal extraction, user review and
decision calculations. `decisionlens/documents.py` handles byte inputs, limits, provenance and
page-preserving chunks. `retrieval.py` implements cosine MiniLM search, BM25 and RRF hybrid.
`evidence.py` extracts labelled facts and retains disagreement sets. `decisions.py` computes
conditional utility and coverage and generates a source-traceable Markdown brief.
`server.py` exposes a loopback FastAPI service; `static/` is a responsive, dependency-free
browser interface. The original two module names remain usable local entry points, while
unchanged original code is archived in `legacy/`.

Model files are public Apache-2.0 pretrained checkpoints downloaded once with explicit
revisions and SHA-256 verification. Runtime requires local files and never calls a billing
service. In-memory normalized vectors replace shared Chroma persistence. All source links
are validated as HTTP(S) metadata, not fetched. Session workspaces expire after inactivity.
The original API-key global state and temporary-file paths are absent from the supported app.

Extraction is deliberately literal. The UI supports manual assertions with review notes and
keeps original source snippets. A text mismatch is a review flag, not a semantic contradiction
verdict. Candidate answer excerpts can be insufficient or irrelevant. Optional FLAN generation
uses the same local checkpoint evaluated in the pilot and is labelled experimental because
its recorded output quality was inadequate.

User ratings are explicit utility judgments. Only reviewed, rated criteria enter the weighted
mean; coverage exposes missing eligible weight. No hidden unit or currency normalization,
automatic winner, learned confidence or procurement guarantee is implemented. Edited briefs
are saved in memory and exported as Markdown, while comparison CSV is formula-escaped and
evidence JSON includes source records. Changing evidence or priorities regenerates the brief.

Research includes a frozen protocol, conservative schema eligibility, evidence-group splits,
five retrieval comparisons and a local generation feasibility check. The all-document matrix
is not the same as the top-k retrieval experimental extractor. Results and limitations must
be interpreted at their actual unit: attribute snippet, source filename or synthetic cell.

Before shared deployment: add authentication, session/storage authorization, encrypted durable
storage, retention controls, worker isolation, quotas and abuse handling; then test the complete
hosted workflow. Current host/origin restrictions intentionally keep this edition local.
