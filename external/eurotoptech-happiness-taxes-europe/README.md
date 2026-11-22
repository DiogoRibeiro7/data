# Euro Top Tech: Happiness and taxes in Europe

[Euro Top Tech](https://www.eurotoptech.com/research/happiness-taxes-europe)
publishes a country table built from self-reported submissions by software
engineers living in Europe: the mean 0-10 rating of happiness, the mean 0-10
rating of satisfaction with what taxes pay for (infrastructure, healthcare,
public services), the number of rated reports, and the average effective tax
rate (1 - net/gross), savings rate and net pay.

## Snapshot used

| Field | Value |
| --- | --- |
| Read on | 22 November 2026 |
| Countries | 29 (at least 5 rated reports each) |
| Reports | 1,673 approved, 782 rated, 744 in the listed countries |
| Transcription | `Medium-Blog/ranking-extremes/snapshot.py` |
| SHA-256 of the canonical text | `7bb9db9c13991e50adeb860a8e2f8403fe0ff85687f1862e582dbcdc64707140` |

The page recomputes from a live database and offers no download, so the table
was transcribed by hand. The digest is taken over `snapshot.canonical_text()`
(one comma-separated line per country with fixed decimals) and is checked by
the consumer's tests.

## Limits

- Respondents are self-selected engineers, not a sample of residents.
- The page reports means only: no standard deviations, distributions or
  intervals. Twelve countries rest on 5 to 9 reports, which the page labels
  "thin sample".
- Numbers change as submissions arrive; a capture from 11 October 2026 in the
  Wayback Machine shows an earlier state.

## Rights

No licence for the published aggregates is stated on the page, and the site's
terms were not reviewed. Redistribution is unresolved; no bytes are mirrored
in this registry. Cite Euro Top Tech, "Happiness and taxes in Europe" (2026).

## Consumers

- `medium-blog/ranking-extremes`: `DiogoRibeiro7/Medium-Blog`, folder
  `ranking-extremes`.
