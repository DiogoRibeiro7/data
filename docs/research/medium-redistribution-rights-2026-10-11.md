# Phase 11 Medium redistribution-rights review

Date: 2026-10-11  
Tracking: #196

## Decision rule

This registry distinguishes a dataset publisher's licence declaration from the
underlying rights in third-party content contained in the dataset.

A permissive or Creative Commons label on a dataset repository is not treated
as sufficient evidence that the dataset publisher owns or received permission
to redistribute every copied Medium article body.

The current Medium terms state that authors retain their rights in submitted
content and grant Medium a licence for use across Medium's services. Medium's
terms also instruct users not to copy, download, or share content unless they
have the right to do so, and prohibit scraping/copying the service without
express written consent.

For this registry, therefore, full-text third-party article corpora remain
external-only unless authoritative evidence establishes the necessary rights
for the exact bytes.

This is a conservative registry eligibility decision, not a general legal
opinion about every possible research use.

## Crawlfeeds Medium Articles Corpus

Source:

- https://huggingface.co/datasets/crawlfeeds/Medium-Articles-Corpus

Evidence:

- Hugging Face declares `cc-by-sa-3.0`;
- the dataset card describes the corpus as scraped from Medium;
- the dataset includes full/raw article bodies belonging to many third-party
  Medium authors;
- no evidence was recovered that Crawlfeeds obtained a licence from those
  authors authorizing republication of all article bodies outside Medium.

Decision:

- registry redistribution: **unresolved / terminal**;
- registry storage: **authoritative-upstream only**;
- canonical promotion: **not permitted under current evidence**;
- reopening condition: authoritative rights evidence covering the exact
  redistributed bytes, plus immutable dataset identity.

The CC BY-SA 3.0 dataset-card label may describe Crawlfeeds' intended licence
for its dataset compilation, but it does not establish that every embedded
third-party article body can be relicensed.

## Fabio Chiu Medium articles

Source:

- https://huggingface.co/datasets/fabiochiu/medium-articles
- reviewed visible revision:
  `979af3bcd84565e3f47b9eca752d8ec112824953`

Evidence:

- Hugging Face declares `mit`;
- files include third-party article text and a separate no-text representation;
- the full-text rows reproduce substantial Medium article bodies;
- no evidence was recovered that the dataset publisher obtained redistribution
  rights from each underlying article author.

Decision:

- full-text redistribution: **unresolved / terminal**;
- registry storage: **authoritative-upstream only**;
- canonical promotion of full-text files: **not permitted under current evidence**;
- the no-text file is not automatically approved either, because its exact
  rights, provenance, and intended licence scope have not been separately
  established;
- reopening condition: authoritative evidence that the relevant exact file(s)
  may be redistributed, assessed separately for full-text and no-text variants.

The MIT label cannot safely be interpreted as transferring rights the dataset
publisher may not own in third-party article bodies.

## Harrison Jansma historical Medium dataset

Source:

- https://github.com/harrisonjansma/Analyzing_Medium
- repository revision:
  `c0cc836bcdfbd3bd1d986bb967978d92ee43dac9`

Evidence:

- the README states that the author collected roughly 1.4 million Medium
  stories from 95 popular subjects;
- it says the dataset was published for public use on Kaggle;
- the repository itself has no `LICENSE` file;
- the actual dataset bytes are distributed outside the Git repository;
- no authoritative dataset-specific licence was recovered for the exact
  Kaggle object.

Decision:

- registry redistribution: **unresolved / terminal**;
- registry storage: **authoritative-upstream only**;
- canonical promotion: **not permitted under current evidence**;
- reopening condition: exact Kaggle object/version plus authoritative
  dataset-specific redistribution terms.

A statement that data were made available for public use is useful provenance
evidence, but it is not equivalent to an explicit redistribution licence.

## Phase 11 outcome

All three Medium sources are now **terminal external-only records under current
evidence**.

This removes the actionable provenance-debt queue without pretending that
ambiguous rights are resolved positively.

Any future reopening requires new authoritative rights evidence for the exact
dataset bytes. Until then, downstream consumers may use the upstream sources
subject to their own legal/ethical review, but this registry will not mirror or
promote the data.


## Promotion follow-up

Canonical-promotion scoring is recorded in
[medium-canonical-promotion-score-2026-10-11.md](medium-canonical-promotion-score-2026-10-11.md).

All three candidates fail the mandatory redistribution gate and therefore remain
external-only under current evidence.
