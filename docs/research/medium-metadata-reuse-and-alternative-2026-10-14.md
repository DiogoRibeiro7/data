# Medium metadata research-use review and licensed alternative

Review date: 2026-10-14. Consumer: `medium-statistical-dynamics`.

## Decision

The user clarified that no independent authorization for Crawlfeeds' original
collection or redistribution has been established, and explicitly approved a
clearly labelled non-Medium engagement study if Medium could not be cleared.
No authorization statement is inferred from the earlier informal confirmation.
Crawlfeeds acquisition remains blocked under this task's evidence requirement.
UCI Online News Popularity is selected for a separate Mashable share-count study.

## What metadata-only changes, and what it does not

Article identifiers, dates and counts avoid copying expressive article bodies.
That reduces the content at issue but does not establish lawful collection,
database extraction rights, contractual permission, or the treatment of author
identifiers. Downloading the full Crawlfeeds CSV and discarding its body columns
would still acquire the bodies. A separately supplied metadata-only file would
require its own evidence and licence scope.

[Crawlfeeds' terms](https://crawlfeeds.com/terms) permit attributed aggregate
analysis and restrict dataset redistribution. They also state that copyright
ownership may not have been checked and claim robots.txt compliance. This is
provider-side permission evidence; robots compliance is not proof of Medium's
consent or rights in third-party text. The CC BY-SA dataset-card label does not
resolve those missing facts.

[Medium's terms](https://help.medium.com/hc/en-us/articles/213481318-Medium-Terms-of-Service)
retain authors' rights and require users to have the necessary rights for copied
content. The explicit automated-access and copying restrictions are in the
**Prohibitions on Use of the Services** section of the
[Medium Rules](https://policy.medium.com/medium-rules-30e5502c4eb4), rather than
the terms paragraph cited in the earlier review. These rules cover data as well
as content. Their existence does not by itself decide every downstream research
use, and this review does not assert that all metadata research is unlawful.

## Possible research exceptions: not assumed applicable

[EU Directive 2019/790, Articles 3 and 4](https://eur-lex.europa.eu/eli/dir/2019/790/oj/eng)
provides distinct text/data-mining routes: qualifying research bodies with lawful
access, and a broader route subject to appropriate rights reservations. A
noncommercial purpose alone is not proof that either route's conditions are met.
[Portugal's implementation](https://diariodarepublica.pt/dr/detalhe/decreto-lei/47-2023-214524782)
also addresses these conditions. Institutional eligibility, applicable law,
lawful access and relevant reservations have not been established for this
project and corpus. No exception is used as an automatic authorization here.

## Alternatives assessed

| Source or route | Reuse evidence and fit | Decision |
| --- | --- | --- |
| Crawlfeeds corpus | Body-containing CSV; metadata fields fit H1/H2; provider terms do not resolve collection/underlying rights | Remains blocked |
| Fabio Chiu no-text variant | Existing review distinguishes this from full text; separate licence scope and collection evidence remain unestablished; engagement field not confirmed | Not acquired |
| Jansma historical Medium data | Author describes public availability and topic-selected collection; exact Kaggle object licence not verified in this review | Not acquired |
| Author-contributed Medium exports | Potential consented route, with exact field/rights review and a defined participating-author sample | No exports supplied; possible future Medium study |
| UCI Online News Popularity | Dataset-specific CC BY 4.0 at authoritative repository; statistics rather than article bodies; shares available, authors absent | Selected for the user-approved alternative |

The selected source is recorded in
[its external record](../../external/uci-online-news-popularity/README.md).
UCI's explicit statistical scope and attribution licence provide a clearer
basis for local analysis than the unresolved body-containing Medium corpus.
No linked article pages are collected. This review does not expand that licence
to content outside the deposited statistical dataset.

## Scientific consequences

The alternative population is the observed Mashable sample; the outcome is
shares, not claps. H1-style concentration and existing discrete count baselines
can be evaluated. H2 and author-cluster intervals are unavailable because author
IDs were not collected. Any article bootstrap intervals must state their IID
assumption and inability to correct dependence or selection. Publication-date
coverage stays descriptive; no complete discovery frame is documented.
