# Crawlfeeds Medium Articles Corpus

**Status:** external reference; no dataset bytes mirrored.

- Upstream: https://huggingface.co/datasets/crawlfeeds/Medium-Articles-Corpus
- Research consumer: [medium-statistical-dynamics](https://gitlab.com/DiogoRibeiro7/medium-statistical-dynamics)
- Redistribution: **unresolved**; no canonical promotion.
- Detailed preliminary audit: [Medium source feasibility](../../docs/research/medium-source-feasibility.md)

Before use, verify the exact source snapshot, licensing and collection terms, stable identifiers, date ranges and fields. Any conclusions must refer to the observed sample rather than the entire Medium platform unless sampling coverage is defensible.

## Source identity review, 2026-10-14

| Item | Verified upstream metadata |
| --- | --- |
| Full Git revision | `2a06e644bf7cfa468f51bfb5ae3f1680632bc234` |
| CSV path | `medium_articles_corpus.csv` |
| File size | 146,560,143 bytes |
| Git LFS SHA-256 | `5b12d3ec8e841f9f26d954d50838149007c443a8eb2b093519d61e8d72857ee0` |

These values come from the [revision-pinned Hugging Face metadata API](https://huggingface.co/api/datasets/crawlfeeds/Medium-Articles-Corpus/revision/2a06e644bf7cfa468f51bfb5ae3f1680632bc234?blobs=true).
The checksum is an upstream declaration, not a digest computed from a local
download. This review did not acquire the corpus or create a research extract.

The [dataset-info service](https://datasets-server.huggingface.co/info?dataset=crawlfeeds%2FMedium-Articles-Corpus&config=default)
reports 14,702 train rows and 20 fields, including `post_id`, `author_url`,
`published_at`, and `total_claps`. Those four fields match the research extractor.
The info-service response is not revision-pinned, so its row count and schema
are provisional until checked against permitted downloaded bytes. The dataset
card's simplified `date`/`claps` table is not the machine-reported schema.
Visible timestamp examples omit timezone offsets. Do not assume UTC or infer a
full-corpus exclusion rate from a preview. Article age and clap-observation time
remain unverified; a scrape timestamp alone does not establish when claps were
measured. Sampling coverage remains undocumented, so H5 inference is disabled.

The [pinned card](https://huggingface.co/datasets/crawlfeeds/Medium-Articles-Corpus/blob/2a06e644bf7cfa468f51bfb5ae3f1680632bc234/README.md)
declares CC BY-SA 3.0. [Crawlfeeds' terms](https://crawlfeeds.com/terms) permit
attributed aggregate analyses but restrict dataset redistribution and disclaim
copyright checks. This does not establish rights in every embedded article or
permission for the original collection. The registry's existing external-only
decision remains in force. Local research acquisition requires its own documented
permission review; neither this metadata update nor the licence label clears it.
