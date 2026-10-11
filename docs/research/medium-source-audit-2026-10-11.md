# Phase 11 Medium source audit

Date: 2026-10-11  
Tracking: #195  
Consumer: `medium-statistical-dynamics`

## Scope

This audit separates four questions that were previously mixed together:

1. can the exact upstream object be identified;
2. can the collection method and sampling frame be reconstructed;
3. does the source expose the fields needed by the consumer;
4. do the exact dataset bytes have sufficiently clear reuse/redistribution rights.

Question 4 is intentionally left for #196. Public visibility, a dataset-card licence,
or an upstream author's statement that data are "for public use" is not treated as
sufficient evidence by itself when the dataset contains third-party article text.

## crawlfeeds/Medium-Articles-Corpus

Authoritative record:

- https://huggingface.co/datasets/crawlfeeds/Medium-Articles-Corpus

Observed source facts:

- Hugging Face labels the dataset `cc-by-sa-3.0`;
- the dataset is tagged as web-scraped;
- the current viewer reports 14,702 rows and about 147 MB of downloaded files;
- the card describes it as a sample/subset of a larger Crawlfeeds Medium corpus;
- fields include article and author identifiers, publication/scrape timestamps,
  comments, claps, tags, full/raw article content and a scrape timestamp;
- the visible date range includes a `1970-01-01` publication-date extreme, so
  timestamp cleaning is required before scientific use.

Audit conclusion:

- source location: established;
- current structure and fields: established;
- collection mode: explicitly web-scraped;
- sampling frame: not fully specified beyond being a sample/subset;
- immutable dataset revision/checksum: not yet pinned in registry metadata;
- rights to redistribute third-party article bodies: unresolved.

The source is useful for engagement and temporal analyses, but full-text mirroring
must not be assumed permissible merely from the dataset-card licence.

## fabiochiu/medium-articles

Authoritative record:

- https://huggingface.co/datasets/fabiochiu/medium-articles

Observed source facts:

- Hugging Face labels the dataset `mit`;
- the dataset viewer exposes the concrete revision
  `979af3bcd84565e3f47b9eca752d8ec112824953`;
- at that revision the repository contains at least
  `medium_articles_no_text.csv`, while the dataset builder also sees files with
  a `text` column;
- the visible schema includes title, article text, URL, authors, timestamp and tags;
- the viewer currently reports a cast failure because files have different columns,
  which is relevant to reproducible loading;
- the source contains third-party Medium article text and URLs.

Audit conclusion:

- immutable source revision: established;
- file-level structure: partially established and currently heterogeneous;
- collection provenance: dataset card/source still needs rights-focused review;
- dataset-card licence: MIT is explicitly declared;
- whether that declaration is sufficient to redistribute copied article text:
  unresolved and delegated to #196.

A metadata-only or no-text representation may have a materially different rights
profile from the full-text files and should be evaluated separately.

## harrisonjansma/Analyzing_Medium

Authoritative repository:

- https://github.com/harrisonjansma/Analyzing_Medium
- audited repository head: `c0cc836bcdfbd3bd1d986bb967978d92ee43dac9`

Observed source facts:

- the README states that the author collected data on about 1.4 million unique
  Medium stories across 95 popular writing subjects;
- the repository contains analysis/cleaning notebooks and points to the published
  dataset on Kaggle;
- the README states the dataset was published for public use by the Medium community;
- the repository itself has no `LICENSE` file;
- the actual 1.4M-row dataset is not stored in the GitHub repository.

Audit conclusion:

- repository identity and research methodology context: established;
- exact Git revision: established;
- dataset hosting route: identified as Kaggle from the author's README;
- exact Kaggle dataset revision/file checksum: not established by this repository;
- repository licence for the dataset: absent;
- sampling is explicitly topic/popularity based, not a probability sample of Medium;
- reuse/redistribution rights for the actual dataset bytes remain unresolved.

## Phase 11 audit outcome

The three records no longer have a generic provenance-discovery blocker.

| Source | Exact source identity | Collection/sampling evidence | Remaining blocker |
| --- | --- | --- | --- |
| crawlfeeds | source established; immutable revision not yet pinned | web-scraped sample/subset; frame incomplete | redistribution rights and immutable version pin |
| fabiochiu | revision `979af3bcd84565e3f47b9eca752d8ec112824953` | file structure established; heterogeneous schemas | rights for third-party text |
| Jansma | Git repo pinned to `c0cc836bcdfbd3bd1d986bb967978d92ee43dac9` | 1.4M stories / 95 popular subjects; Kaggle distribution route | dataset licence and exact Kaggle object identity |

#196 should now focus on source-specific reuse and redistribution rights rather than
repeating general source discovery.
