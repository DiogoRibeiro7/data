# Medium source feasibility: initial audit

Date: 2026-10-07  
Consumer: [medium-statistical-dynamics](https://gitlab.com/DiogoRibeiro7/medium-statistical-dynamics)  
Status: **candidate sources; no canonical datasets approved**

## Scope and decision rule

This is a *source-discovery audit*, not an assertion that public dataset visibility authorizes redistribution. Only promote data under `datasets/` when provenance, source licensing, collection terms, exact source identity, checksum and reusability have been verified. Until then keep upstream bytes outside the registry and record an external reference if it meets the registry schema.

## Candidate A: historical Medium article study

- Repository: https://github.com/harrisonjansma/Analyzing_Medium
- Publisher: Harrison Jansma (community researcher).
- Author reports **1.4 million unique stories** from **95 popular writing subjects**; data published on Kaggle (follow original repository links to identify exact dataset and revision).
- Repository contains exploratory and cleaning notebooks.
- **Unverified**: actual accessible dataset file, data dictionary, complete timestamp range, selection/inclusion mechanism, license applicable to data, terms of original collection and redistributability.
- **Bias concern:** popular-subject sampling cannot be treated as a random sample of all Medium articles.
- Initial relevance: H1, H2, H5 conditional on verified clap, author and date columns.

## Candidate B: crawlfeeds Medium Articles Corpus

- Dataset card: https://huggingface.co/datasets/crawlfeeds/Medium-Articles-Corpus
- Dataset card reports **14,702 rows**, a CSV of approximately **147 MB** and an asserted **CC BY-SA 3.0** license.
- Viewer describes article/author identifiers, publication and scrape timestamps, clap and comments counts, tags, reading time and article text.
- Published-at field includes a **1970-01-01** extreme, warranting timestamp validity screening.
- Source explicitly characterizes the material as scraped. The displayed dataset license **does not, by itself, establish the provider's right to license all article text or collection permission**.
- **Unverified**: original rights for article bodies, sampling frame, coverage bias, identity stability, duplication, version-pinned checksum and permission for redistribution.
- Initial relevance: H1, H2, H5 if provenance/usage questions can be resolved. Avoid importing full article text where it is not required.

## Candidate C: Fabio Chiu Medium articles corpus

- Candidate link from the initial research plan: https://huggingface.co/datasets/fabiochiu/medium-articles
- Related 190k article dataset referenced at https://www.kaggle.com/datasets/fabiochiusano/medium-articles (cross-check dataset identity; do not assume the links are equivalent).
- **Unverified**: Hugging Face dataset availability, license, column schema, timestamp span, sampling and the exact relation to the Kaggle dataset.
- Initial relevance: article/text/topic analysis and potentially H5, pending inspection; do not assume it has engagement outcomes.

## Decision matrix

| Source | Candidate H1 | Candidate H2 | Candidate H5 | Redistribution |
| --- | --- | --- | --- | --- |
| Jansma | Conditional | Conditional | Conditional | Unresolved |
| crawlfeeds | Field advertised | Field advertised | Field advertised | Unresolved despite dataset-card license |
| Fabio Chiu | Unknown | Unknown | Conditional | Unresolved |

**None of these collections is established as a probability sample of the Medium platform.** Initial inference must be explicitly conditional on each dataset's selection process.

## Next verification tasks

1. Confirm exact immutable snapshot/version and list real columns from each source without committing source bytes.
2. Check source-specific legal terms, provenance and permission; retain written evidence.
3. Quantify duplicates, missing IDs, null dates, impossible timestamps, topical coverage, article-age confounding and measurement definitions.
4. Determine whether reproducibility can use metadata-only licensed extracts or an upstream download with explicit use restrictions.
5. Register validated *external* source metadata according to `external/*/metadata.yaml` schema and regenerate catalogs. Do **not** promote any canonical dataset or add consumer contracts until checks pass.

## Notes on statistical validity

Claps are not unique readers or reads; one article can receive multiple claps from an individual. Dataset scrape timestamp is not necessarily clap observation time. Author inequality based on topic-selected articles may underestimate or overestimate the platform-wide concentration of attention.

Links checked for initial discovery: https://github.com/harrisonjansma/Analyzing_Medium ; https://huggingface.co/datasets/crawlfeeds/Medium-Articles-Corpus ; https://huggingface.co/datasets/crawlfeeds/Medium-Articles-Corpus/tree/main ; https://www.kaggle.com/datasets/fabiochiusano/medium-articles .
