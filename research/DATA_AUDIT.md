# Dataset fitness and license audit

Access began 2026-11-04. Machine-readable checks: `data_audit.json`;
file URLs, SHA-256 and pinned revision: `data/source_manifest.json`;
pre-evaluation grouping: `split_manifest.json`.

## AWS Product Comparison

Public unsigned HTTPS download succeeded; no AWS account, payment method or billing used.
[Registry](https://registry.opendata.aws/prod-comp-shopping/) states CC BY-SA 4.0 and identifies
Vedula, Collins, Agichtein and Rokhlenko's WSDM 2023 paper. The downloaded TSV has **14,718**
data records and three columns, while the README describes 14,719 records and two fields.
Actual file bytes and headers govern this study. Python literal parsing found 11,270 dictionaries
and 3,448 tuples. Only **6,685** rows have the explicit `_productN` key schema used here.
The remaining 4,585 dictionaries lack that per-product key pattern; tuples lack named attributes.

The audit JSON calls these adapter rejections “malformed attribute key” or “empty or invalid
attributes”; **this does not establish that the original data is defective**. It means the row
cannot support this pilot's specific mapping without additional assumptions. They were excluded,
not silently reinterpreted. Among eligible rows, 2,496 distinct maps and 384 attribute signatures
were found; 4,189 repeated maps were not treated as independent product sets.
Hash-selected 20 development and 60 evaluation signatures use one record each.

Evaluation records are short, anonymized, single-attribute comparisons. Three neutral synthetic
distractors are added consistently. This adapter produced a trivial retrieval test and cannot
support general real-world performance claims. Original human prose was not indexed or scored
as preference truth. For example, the first row has tied ratings for two products but prose
prefers one of them; numeric ranking alone does not explain that preference.

Raw/derived dataset text is omitted from the source ZIP. Fetch it using the hash-verifying script.
If you distribute dataset-derived text later, preserve attribution and comply with CC BY-SA 4.0;
the license does not turn anonymized shopping data into current SaaS proposals.

## RAG-Multi-Corpus

Pinned commit `39071af3f4dd25e59f5c59a6f9b6e8e99cd643b3` downloaded through public GitHub URLs.
The repository LICENSE is MIT, copyright 2025 UDAY ALLU; README states synthetic research data.
License notice retained in `licenses/RAG-Multi-Corpus-LICENSE.txt`. All content is labelled synthetic.
The used QA CSV actually has **1,252** rows, not the README's 786. Cloudway has 164 query rows and
37 downloaded Markdown documents. Those documents describe a fictional airline, contradicting
the README's Cloud/SaaS domain description. This subset is **not a SaaS benchmark**.

Support JSON was parsed, referenced files matched after outer-whitespace normalization, and
support text checked as a normalized substring after decoding literal Unicode/newline escapes.
**46/164** Cloudway rows pass that strict mechanical check; 118 fail it. These may reflect
paraphrases, source revisions, or annotation errors; no manual repair or semantic invalidity
claim is made. Connected support-document groups yield 15 development and 31 evaluation queries.
There are zero exact duplicate source documents in the downloaded Markdown subset. Full files
are indexed for retrieval; held-out query labels are never used in retrieval or prompts.
All 31 selected evaluation queries happen to have one gold filename, limiting multi-source conclusions.

These are source-document relevance labels, not span-complete or semantic correctness labels.
No independent human ratings were obtained. Raw files are not redistributed in the ZIP.

## Controlled and public-case data

Controlled cases and demo files are generated expressly for this project and clearly fictional.
Their deterministic labels test schema behavior. Repeated templates mean that disjoint vendor
names do not provide strong linguistic independence. Results are separate from the real-source task.
The public SaaS case consists of short AI-assisted paraphrases with original links and access date;
unknown publication dates remain null. No copyrighted page dump is bundled. It is qualitative only.
