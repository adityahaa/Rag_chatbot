# DecisionLens protocol v1 — frozen before evaluation

Date: 2026-11-04, Asia/Kolkata. This is a local timestamped protocol, not an external preregistration.
Research question: How reliably can retrieval-based systems compare products when evidence is
distributed or incomplete? This pilot tests narrow retrieval and literal attribute recovery,
and a small generative feasibility check. It cannot establish procurement utility or general
semantic answer correctness. No novelty claim. No trained model or paid service.

## Data and split, fixed before any held-out scores

1. AWS Product Comparison: parse the full TSV with `ast.literal_eval` (never eval).
   Group by sorted attribute-name signature after removing `_productN`. Select up to
   20 development and 60 evaluation records by sorted SHA-256 of group signature then
   record hash; one record per signature. All examples sharing a signature stay on
   the same side. No fine-tuning. This is stricter than row randomization but cannot
   rule out unknown real-product overlap because IDs are anonymized per record.
   Human comparison prose is retained in raw data but **never indexed or used as a query**.
   Attribute dictionaries are reference labels for literal recovery only; human prose
   is not accepted as a universally correct preference ranking.
2. RAG-Multi-Corpus pinned commit in source_manifest.json. Use only the downloaded
   Cloudway Markdown subset and its QA rows from `datasets/Dataset categories - queries_01122025.csv`.
   This subset actually describes a fictional airline, despite the README's SaaS description.
   Audit all QA support JSON, named source existence, and normalized support substring presence.
   Unsupported labels are excluded from retrieval evaluation and logged. Treat filename labels
   as document relevance, not span gold or answer correctness. Connect QA rows sharing a support
   filename into groups; deterministic hash split 25% groups dev, remainder eval, capped at
   60 eval queries, preserving query types. Full downloaded document corpus is indexed for both.
   No human answer quality claims; all content is synthetic. Exact/normalized duplicate
   queries and duplicate documents are audited.
3. Controlled synthetic product cases: generate 5 dev and 15 held-out groups with disjoint
   fictional names and seed 31. Four paired evidence conditions per group: full, one missing
   fact, a conflicting value, and no relevant facts. Report separately from AWS and RAG-Multi.
   Known literal labels are programmatically constructed; this primarily tests software
   behavior, not general language understanding. No human annotation is implied.
4. Small dated public SaaS case: source notes only, separately reported; no automatic
   correctness or procurement ranking claims. Accessible official source pages and license
   restrictions determine what can be retained. Missing/access-blocked sources are logged.

## Methods and budgets

All methods use the same pretrained `sentence-transformers/all-MiniLM-L6-v2` local
384-dimensional normalized embeddings, page-preserving 1000-character chunks / 200 overlap
for prose, CPU float32, and k=3. Runtime model revisions and SHA-256 files are saved.
Source-attribute benchmark uses one short snippet per attribute; this is a task adapter,
not the original PDF layout. No similarity score is called a correctness probability.

- **semantic**: dense cosine top-3. Repaired original-style baseline **proxy**, not a
  reproduction of the inaccessible Gemini embeddings/Chroma/generation stack.
- **keyword**: BM25 (k1=1.5,b=0.75), diagnostic baseline.
- **hybrid**: equal-weight reciprocal rank fusion of semantic and BM25 ranks, constant 60.
- **semantic_diverse**: semantic with at most one snippet per product on the first pass,
  then fill unused budget by rank. Factorial diversity ablation.
- **hybrid_diverse**: same diversification on hybrid. Evidence-aware candidate retrieval.
  For product queries, eligible products are the explicitly named targets; non-target
  distractors are not forcibly excluded. For corpus QA, product metadata is organization
  level and diversification falls back to document name.

No extra context budget for diversification. A fixed literal extractor reads `label: value`
records in all product methods. It emits unknown if no value is found and conflict when
different normalized values occur for the same cell; it never resolves conflicts by date.
This separates retrieval effects from a changing generator. Automatic conflict flags can
overstate semantically equivalent values and do not settle scope or date differences.

## Metrics

- Per-case Recall@3 = unique retrieved gold evidence units / available gold units;
  report separately document recall for RAG-Multi and attribute recall for products.
- Complete evidence rate = fraction of answerable cases with all required available units
  in the context. When >3 units are necessary this has a structural ceiling; report that.
- MRR of first gold unit. Missing/no-evidence cases excluded from retrieval denominators.
- Literal attribute exact-match recovery against reference dictionary. Reference absence
  is unknown, never zero. Conflicting cells require the full value set. String matching
  cannot establish natural-language semantic correctness.
- Controlled unknown status accuracy and conflict detection recall; report denominators
  and coverage tradeoffs separately. These are deterministic schema tests, not hallucination rates.
- Index construction time and per-query retrieval latency (warm encoder, includes query
  embedding; sequential CPU). Save raw timings; tiny pilot timing is not a production SLA.

Generative feasibility: first 3 held-out synthetic groups, full + absent conditions,
semantic/hybrid/hybrid_diverse, same `google/flan-t5-small`, greedy, max_new_tokens=96,
input <=512 tokens, identical prompt and truncation policy, no sampling. First product
SSO question; record reference literal, output, input/output token counts, latency and
heuristic exact/unknown match. Candidate sources are not automatic claim citations.
This check is exploratory and underpowered, with no LLM-as-judge and no human raters.

## Analysis and reporting commitments

Save split IDs and hashes and source provenance before final evaluation. Freeze code/settings
hash in run metadata. Keep append-only run folders and per-case failures, null results, and
tracebacks without secrets. No tuning after held-out scores; fixes must be identified as
software repairs and earlier failures retained. Summarize means plus counts. Do not run
significance tests on these nonrandom pilot samples or claim population improvements.
Plots show separate dataset panels; no pooled synthetic/real score. Final paper is a pilot
draft with explicit incomplete sections, not submission-ready evidence.
