# Literature and methodology notes

Primary paper abstracts, dataset documentation and official model cards inspected
2026-11-04/05. This is a targeted review, not a systematic or exhaustive literature search.
No first-of-its-kind or state-of-the-art claim is supported.

| Prior work | What it establishes / relation to DecisionLens | Evidence reviewed |
| --- | --- | --- |
| Lewis et al., 2020, *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* | Retrieval plus a pretrained generator predates this project. DecisionLens is an application extension and narrow pilot, not a new RAG architecture. | [Primary paper](https://arxiv.org/abs/2005.11401) |
| Vedula, Collins, Agichtein & Rokhlenko, 2023, *Generating Explainable Product Comparisons for Online Shopping*, WSDM, DOI 10.1145/3539597.3570489 | HCPC already studies explainable, factually consistent product comparisons. Its human comparative-text task is richer than this pilot's literal attribute recovery. We do not reproduce its training or claim its reported performance. | [Author publication](https://www.amazon.science/publications/generating-explainable-product-comparisons-for-online-shopping), [paper](https://assets.amazon.science/5d/03/2f7e2ab8407cb37e679211c2c677/generating-explainable-product-comparisons-for-online-shopping.pdf) |
| Vedula et al., 2022, *What Matters for Shoppers: Investigating Key Attributes for Online Product Comparison*, ECIR | Choosing comparison attributes is an existing research problem. A user-editable shortlist does not establish novelty. | [Author publication](https://www.amazon.science/publications/what-matters-for-shoppers-investigating-key-attributes-for-online-product-comparison) |
| Thakur et al., 2021, *BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models* | Retrieval performance depends on domain; lexical retrieval remains a meaningful comparator. We include BM25 and avoid assuming dense retrieval always wins. | [Primary paper](https://arxiv.org/abs/2104.08663) |
| Asai et al., ICLR 2024, *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection* | Retrieval adaptation and self-critique are established research directions. Our simple diversity heuristic is not Self-RAG and has no trained reflection tokens. | [Primary paper](https://arxiv.org/abs/2310.11511) |
| Liu et al., *Lost in the Middle: How Language Models Use Long Contexts*, TACL 2024 (2023 preprint) | Evidence presence alone does not ensure a model uses it; position and context limits matter. Our generator's short token budget is an important confound. | [Primary paper](https://arxiv.org/abs/2307.03172) |
| Yang et al., NeurIPS 2024, *CRAG: Comprehensive RAG Benchmark* | Realistic RAG evaluation includes diverse questions and changing facts. This small static pilot cannot match that evaluation scope. Do not confuse this benchmark with Corrective RAG. | [Primary proceedings](https://papers.nips.cc/paper_files/paper/2024/hash/1435d2d0fca85a84d83ddcb754f58c29-Abstract-Datasets_and_Benchmarks_Track.html) |
| Yan et al., 2024, *Corrective Retrieval Augmented Generation* | Correcting retrieval failures is established work. DecisionLens' metadata diversification is a much narrower heuristic, not a reproduction. | [Primary paper](https://arxiv.org/abs/2401.15884) |
| Ho, Xu & Dey, 2010, *Multi-criteria decision making approaches for supplier evaluation and selection: A literature review*, EJOR, DOI 10.1016/j.ejor.2009.05.009 | Multi-criterion supplier selection, including weighting methods, is long established. The application's additive user ratings are an interpretable utility aid, not a validated procurement model. | [Publisher abstract](https://doi.org/10.1016/j.ejor.2009.05.009) |
| Allu et al., 2025, RAG-Multi-Corpus repository | Synthetic enterprise-style corpus and QA labels; pinned commit and actual subset audit govern use, not README counts or domain descriptions alone. | [Repository](https://github.com/udayallu/RAG-Multi-Corpus), local MIT license copy |

Newer context located during the review includes [LIT-RAGBench](https://arxiv.org/abs/2603.06198)
and [DeclineCraft](https://arxiv.org/abs/2610.28340), which explicitly include abstention and
evidence-integration issues. Only their abstracts were inspected; no reproduction or exhaustive
comparison is claimed. Their existence further rules out a broad novelty claim about abstention.

## Methodological implications

Keep retrieval labels, literal value labels, generative semantic correctness, source support,
and procurement utility separate. Report source presence as traceability, not correctness.
Use the same model and context budget for retrieval ablations. Label a local baseline proxy
as such when the original provider is inaccessible. Keep all failed and uninformative results.
Deduplicate related examples by available evidence groups, while admitting anonymization limits.
Automatic string checks do not replace an independent human review of actual product comparisons.

The paper draft therefore makes an engineering/pilot claim: it provides a reproducible local
application and reports bounded observations and failure modes. A defensible broader study
would need realistic, licensed, cross-source SaaS evidence, stronger comparison labels,
independent review, more capable local models and a newly frozen evaluation.
