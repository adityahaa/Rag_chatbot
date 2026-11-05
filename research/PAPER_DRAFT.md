# DecisionLens: A Local Evidence Workspace and Pilot Study of Retrieval for Product Comparison

**Working pilot draft — not ready for submission.** Prepared 2026-11-05.
Author names, affiliations, author contributions, venue formatting and independent evaluation
remain for the project owner to confirm. Code, experiment execution, source-note preparation
and this draft were AI-assisted. No independent human ratings were collected.

## Abstract

Product comparisons require evidence to be gathered across sources whose coverage and scope
can differ. We extend an existing PDF retrieval-augmented chatbot into DecisionLens, a local
application that retains source provenance, exposes unknown and conflicting values, supports
user review and explicit priorities, and exports an editable decision brief. A frozen pilot
compares semantic retrieval, BM25, reciprocal-rank-fused hybrid retrieval and two diversity
ablations at a common three-chunk budget. On 60 short real-source product-attribute cases all
methods reach 100% literal recovery, revealing a task ceiling rather than method superiority.
On 31 eligible synthetic enterprise questions, source-document Recall@3 is 28/31 for semantic
retrieval and 30/31 for hybrid retrieval. On controlled fictional cases, naive diversification
reduces mean available-evidence recall from 78.3% to 52.2%; every method misses complete
contradictory evidence in the 15 conflict cases. Eighteen local FLAN-T5-small generations
provide a negative feasibility result: all nine answerable outputs fail literal answer match.
These observations motivate evidence inspection and explicit uncertainty rather than automated
vendor selection. Limited labels, simple task adapters and absence of independent review
preclude broader accuracy or procurement-utility claims.

## 1. Introduction

Engineering managers often compare products using differently dated feature descriptions,
pricing notes and service terms. A fluent summary can obscure unavailable evidence or
differences between plans. DecisionLens investigates the practical question: **How reliably
can RAG systems compare products when relevant evidence is incomplete or distributed across
multiple sources?** This pilot addresses narrow components of that question; it does not
establish end-to-end reliability in real procurement.

The engineering contribution is a traceable local workflow built from Aditya Hambire's
existing RAG Chatbot repository at commit `7eedad4`. The empirical contribution is a
reproducible pilot that includes negative and ceiling results. We claim neither a novel
RAG architecture nor a validated vendor-selection method.

## 2. Related work

Lewis et al. introduced a prominent pretrained retrieval-plus-generation framework [1].
Vedula et al.'s HCPC directly studies explainable, factually consistent product comparisons
and supplies the shopping dataset used here [2]; prior work also examines attribute selection
for shoppers [3]. Our literal recovery adapter is materially simpler than their comparison
generation task and does not reproduce their reported gains.

BEIR motivates lexical baselines and domain-sensitive evaluation [4]. Self-RAG [5] and
Corrective RAG [6] address retrieval and generation control through substantially richer
methods than the simple heuristic evaluated here. Long-context evidence placement can affect
answer quality [7]; source presence is not proof of model use. The CRAG benchmark [8]
evaluates realistic factual QA more broadly than our static pilot. Existing multi-criteria
supplier-selection literature [9] predates this application's transparent additive ratings.
Newer abstention benchmarks were identified in the accompanying literature notes; this
targeted review is not exhaustive. No novelty conclusion follows from it.

## 3. Application design

The original prototype uses PDF text extraction, overlapping character chunks, Google
embeddings, persistent Chroma retrieval and Gemini generation. Audit found discarded source
metadata, shared persistence, process-wide credentials, incomplete temporary-file cleanup
and unverified experimental provider defaults. The preserved original is not represented as
a currently working provider baseline. Google's official deprecation record lists the
original embedding identifier as shut down [10]. No credentialed provider call was made.

The repaired local implementation retains the parse–chunk–retrieve–inspect workflow and a
Streamlit entry point. Its main responsive dashboard adds linked product-intelligence and
vendor-decision views. PDFs are parsed locally with page locations; TXT, Markdown, CSV,
JSON and DOCX retain available sections and filenames. Scans without extractable text and
unsupported formats produce explicit errors. Source links are metadata, never fetched by
the server. Unknown document dates remain unknown.

Candidate extraction reads explicit label/value lines and records literal excerpts.
Different normalized values for a cell are flagged for review; this is textual disagreement,
not semantic contradiction detection. Users may edit and confirm a cell with a review note.
Manual changes remain user assertions alongside the original excerpts.

For a product, the optional score is the weighted mean of user-assigned 0–100 ratings over
reviewed, rated criteria. Unknown and unresolved cells contribute neither a zero nor an
eligible weight. Weighted coverage is shown beside the conditional score. Scores with unequal
coverage need not be comparable, and the application declares no automatic winner. This
utility formulation assumes the chosen criteria and compensatory weights are appropriate;
it does not model hard constraints, uncertainty distributions or actual monetary value.

MiniLM embeddings run locally. The default question workflow returns retrieved evidence;
optional FLAN-T5-small output is explicitly experimental. All inference uses downloaded
model files. No billing account, paid API, cloud upload or training from scratch is required.
Workspaces are isolated in server memory and expire. The implementation is loopback-only;
shared deployment requires further authentication and storage work.

## 4. Data and protocol

The protocol in `PROTOCOL.md` was saved before final evaluation. It was not externally
preregistered. Model revisions, hashes, splits, settings and raw measurements are retained.

**Real-source attributes.** The downloaded AWS TSV contains 14,718 records with multiple
literal schemas. We restrict the task to 6,685 rows with explicit per-product attribute keys.
These yield 384 attribute signatures and 2,496 distinct maps. Hash selection assigns 20
signatures to development and 60 to evaluation, one record per signature. Related signatures
do not cross the split, although real entity overlap cannot be excluded under anonymization.
Original human comparison prose is never indexed or used as a query. Reference dictionaries
support literal recovery, not real procurement ranking. Three neutral synthetic distractors
are added consistently; the evidence remains a real-source attribute task with a controlled adapter.

**Synthetic enterprise corpus.** We pin RAG-Multi-Corpus to commit
`39071af3f4dd25e59f5c59a6f9b6e8e99cd643b3`. The downloaded Cloudway subset contains 37 Markdown
documents and 164 QA rows; the files describe an airline despite a different README domain
label. JSON, filename and normalized support-substring checks admit 46 rows and exclude 118.
Those strict exclusions do not prove semantic annotation error. Connected support-document
groups yield 15 development and 31 evaluation queries over 174 chunks. All selected evaluation
queries have one labelled filename, limiting conclusions about distributed evidence.

**Controlled cases.** Twenty disjoint fictional naming groups use the deterministic seed-31
construction: five development groups and fifteen held-out groups. Four conditions per group
are full support, one missing fact, contradictory values and absent relevant evidence. Repeated
templates and programmatic labels make this a software stress test rather than a broad language
benchmark. Results are reported separately from real-source data.

**Public SaaS case.** Three short AI-assisted factual notes from official GitHub and GitLab
pages illustrate cross-source plan differences. Source links and access dates are retained,
publication dates are unknown, and original pricing pages are not redistributed. This qualitative
case has no independent correctness labels and contributes no benchmark accuracy claim.

## 5. Methods and evaluation

All retrieval methods use k=3. Dense retrieval employs normalized
`sentence-transformers/all-MiniLM-L6-v2` vectors and cosine similarity. BM25 uses k1=1.5 and
b=0.75. Hybrid retrieval uses equal-weight reciprocal rank fusion with constant 60. Diversity
ablations take one snippet per product (per filename for the single-organization enterprise
corpus) on the first pass, then fill by rank. They do not receive extra context budget.
Dense retrieval is an original-style **local baseline proxy**, not the original Gemini stack.

We report macro Recall@3 over available gold units, complete-evidence rate, first-relevant-unit
MRR, and fixed-schema literal cell recovery where labels permit. Enterprise gold units are
filenames, not complete answer spans. Controlled missing and conflict metrics evaluate literal
schema status. No metric here automatically establishes natural-language correctness.
Latency includes warm query embedding, with startup and indexing recorded separately.

The generator check uses the same local FLAN-T5-small model, greedy decoding, 96 output-token
maximum and bounded input for semantic, hybrid and hybrid-diverse contexts. Three held-out
groups and full/absent conditions yield 18 calls. Exact string and a frozen abstention-phrase
check are recorded; no LLM judge or independent human rater is used.

## 6. Results

All 755 retrieval method/case runs completed; no execution failures were recorded.

| Method | Real-source attribute Recall@3 (60) | Synthetic enterprise source recall (31) | Controlled available-evidence recall (45) |
| --- | ---: | ---: | ---: |
| Semantic | 100.0% | 90.3% | 78.3% |
| BM25 | 100.0% | 90.3% | 78.3% |
| Hybrid | 100.0% | 96.8% | 78.3% |
| Semantic + diversity | 100.0% | 96.8% | 52.2% |
| Hybrid + diversity | 100.0% | 96.8% | 52.2% |

The real-source task fits its short evidence records into the budget and does not discriminate
methods. On the selected enterprise subset, hybrid retrieves a labelled source in 30/31 queries,
compared with 28/31 for dense retrieval. This two-query difference is descriptive; we make no
significance or population claim. Diversity alone reaches the same count and combining it
with hybrid produces no further recall gain.

On controlled cases, unfiltered diversity spends a slot on an unrelated vendor, lowering
coverage. Literal cell accuracy across all 60 cases is 87.5% without diversity and 68.75% with it.
Missing-cell status is mechanically correct on all 75 missing cells; this does not measure
generative hallucination. All methods have conflict recall 0/15. Full and conflict conditions
require more than three snippets, giving a structural complete-evidence ceiling; ordinary
retrieval completes 15/45 evidence-bearing cases and diverse retrieval completes none.

All nine answerable generator outputs are citation-like strings rather than the reference
value (0/9 exact match). All nine absent outputs say `unanswerable`. The frozen phrase checker
omits this word and therefore does not recognize those abstentions. We retain that measurement
failure and the raw outputs rather than retrospectively replacing the metric. Human semantic
correctness and independently verified source support remain unmeasured.

Mean warm retrieval is approximately 18–23 ms with MiniLM versus 0.2–1.0 ms for BM25 on the
recorded Windows CPU; encoder startup is about 15.1 seconds. These pilot measurements are not
deployment latency guarantees. Figures and full per-case records are provided in `RESULTS.md`.

## 7. Discussion, limitations and ethics

The evidence does not establish reliable general product comparison. Instead it shows how
an apparently strong aggregate result can coexist with an easy task adapter, limited relevance
labels, harmful retrieval diversification and a weak generator. Explicit evidence review is a
practical application choice under these limits; its benefit to users was not experimentally tested.

The original provider baseline was not reproduced, labels have only mechanical support checks,
the real task lacks realistic distractors, and the synthetic task repeats templates. Strict
eligibility creates selection bias. One gold enterprise filename is not proof of sufficient
answer context. Top-3 retrieval imposes a known ceiling on some conditions. Source citations
are not entailment verification. Source dates may be unavailable, and differing values may
describe different plans rather than true contradictions. Prompt instructions cannot eliminate
hallucinations or document prompt injection.

Only public, permitted or synthetic data were used. AWS attribution and share-alike obligations
are recorded; the enterprise repository's MIT notice is preserved. Private documents, credentials
and raw copyrighted web pages are excluded from the distributable source package. No purchase,
financial saving, human user preference or real vendor suitability was measured. Final decisions
remain with the user.

## 8. Conclusions and work required before submission

DecisionLens supplies a working local evidence workflow and reproducible pilot. The observed
hybrid source-retrieval advantage is narrow; diversification harms the controlled task; and
the small generator fails tested answerable cases. The study does not support claims of novel
comparison methods, broad accuracy or procurement efficiency.

**Incomplete before a defensible submission:** construct harder licensed real multi-source
product cases and blind independent labels; validate extraction and semantic contradiction
handling; compare more capable local generators with consistent budgets; improve abstention
measurement on development data; assess end-to-end source support and user utility; obtain
appropriate reviewer agreement and uncertainty estimates; and freeze a new held-out protocol.
Changes motivated by this final pilot must use a new evaluation set rather than rebranding
these cases as untouched. Confirm authorship and venue requirements with a research supervisor.

## References

1. Lewis et al. (2020). [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401).
2. Vedula et al. (2023). [Generating Explainable Product Comparisons for Online Shopping](https://doi.org/10.1145/3539597.3570489).
3. Vedula et al. (2022). [What Matters for Shoppers](https://www.amazon.science/publications/what-matters-for-shoppers-investigating-key-attributes-for-online-product-comparison).
4. Thakur et al. (2021). [BEIR](https://arxiv.org/abs/2104.08663).
5. Asai et al. (ICLR 2024). [Self-RAG](https://arxiv.org/abs/2310.11511).
6. Yan et al. (2024). [Corrective Retrieval Augmented Generation](https://arxiv.org/abs/2401.15884).
7. Liu et al. (TACL 2024; preprint 2023). [Lost in the Middle](https://arxiv.org/abs/2307.03172).
8. Yang et al. (NeurIPS 2024). [CRAG](https://arxiv.org/abs/2406.04744).
9. Ho, Xu & Dey (2010). [Multi-criteria decision making approaches for supplier evaluation and selection](https://doi.org/10.1016/j.ejor.2009.05.009).
10. Google. [Gemini API deprecations](https://aistudio.google.com/docs/deprecations), accessed 2026-11-04.
