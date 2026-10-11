# Phase 11 Medium canonical-promotion score

Date: 2026-10-11  
Tracking: #197

## Decision rule

Canonical promotion is not a ranking contest. A candidate must pass every
mandatory gate before consumer demand or reuse benefit can matter.

Mandatory gates:

1. stable source identity;
2. explicit redistribution permission for the exact bytes to be stored;
3. reproducible file-level identity/checksums;
4. real maintained downstream demand.

A failure on redistribution is disqualifying under
`docs/DATA_POLICY.md`.

## Scoring model

For reviewability, each candidate is scored on four dimensions:

- source identity: 0–2;
- redistribution clarity: 0–2;
- reproducibility / immutable file identity: 0–2;
- downstream demand / reuse benefit: 0–2.

A candidate is **promotion-eligible only if redistribution clarity = 2** and no
mandatory gate fails.

## Results

| Candidate | Source identity | Redistribution clarity | Reproducibility | Demand / reuse | Total | Promotion decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Crawlfeeds Medium Articles Corpus | 1 | 0 | 1 | 2 | 4 / 8 | Remain external; terminal |
| Fabio Chiu Medium articles | 2 | 0 | 1 | 2 | 5 / 8 | Remain external; terminal |
| Harrison Jansma historical Medium study | 2 | 0 | 1 | 2 | 5 / 8 | Remain external; terminal |

## Candidate rationale

### Crawlfeeds

Strengths:

- known upstream dataset location;
- useful engagement and temporal fields;
- real consumer interest from `medium-statistical-dynamics`.

Blocking failures:

- no pinned immutable dataset revision/file identity;
- the corpus contains scraped third-party article bodies;
- the dataset-card CC BY-SA 3.0 declaration does not establish authority to
  relicense all embedded article text.

Decision: **do not promote**.

### Fabio Chiu

Strengths:

- exact visible Hugging Face revision is known;
- real consumer interest exists;
- no-text and full-text representations could in principle support different
  use cases.

Blocking failures:

- files are heterogeneous;
- no separate, authoritative rights basis was established for the no-text file;
- the full-text files reproduce third-party Medium article bodies and the MIT
  dataset label does not establish authority to relicense that content.

Decision: **do not promote**.

### Harrison Jansma

Strengths:

- Git repository is pinned immutably;
- collection method and sampling context are documented;
- real consumer interest exists.

Blocking failures:

- the actual dataset bytes are hosted separately on Kaggle;
- no exact Kaggle object/version/checksum is pinned;
- no explicit dataset redistribution licence was recovered.

Decision: **do not promote**.

## Final Phase 11 promotion decision

No Medium candidate currently satisfies the canonical dataset contract.

The correct outcome is therefore:

- keep all three as external records;
- preserve their terminal evidence-backed status;
- do not create a canonical dataset merely because a consumer exists;
- reopen only if new authoritative evidence changes the redistribution gate.

This decision means #198 should be closed as **not planned** unless new evidence
arrives before Phase 11 closes.
