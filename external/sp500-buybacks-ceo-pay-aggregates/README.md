# S&P 500 buybacks, EPI CEO pay ratios and S&P 500 price returns (transcribed)

Three small annual series used to test the timing of buybacks against CEO pay.

## What the source provides

- S&P 500 buybacks per calendar year 2007-2024, USD bn, from S&P Dow Jones Indices press releases (one per year, the latest release for each year).
- Realized and granted CEO-to-worker compensation ratios 1965-2024 and five dollar endpoints, from the Economic Policy Institute CEO pay data page (350 largest US firms by sales; 2024 projected).
- S&P 500 annual price return 2005-2024, from a Wikipedia table.

## Consumer

`medium-blog/stock-buybacks-ceo-wealth` holds the values in `src/series.py` with the URL of each release, and recomputes every result and figure with `run_all.sh`.

## Why the bytes are not mirrored

The values come from press releases and web tables, not files, and reuse terms have not been checked. The record pins the transcription by hash and lists the pages.

## Known data characteristics

- 2011 buybacks: 409.0 in the first release, 405.1 later.
- The EPI 2024 ratio is a projection; pre-1992 values are backcast.
- Buyback totals are gross of share issuance to employees.

## Open items

See the `resolution` block: check reuse terms and replace the transcription by downloadable files if allowed.
