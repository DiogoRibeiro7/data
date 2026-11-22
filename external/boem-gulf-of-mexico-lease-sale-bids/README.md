# BOEM Gulf lease sale bids

The Bureau of Ocean Energy Management publishes, for each Gulf of America (formerly Gulf of Mexico) oil and gas lease sale, a fixed-format ASCII bid archive with its record layout, a sale statistics sheet and a bid recap. Material produced by federal agencies is generally in the public domain ([BOEM copyright notice](https://www.boem.gov/copyright)).

## Consumer contract

`Medium-Blog/auction-entry-boem` downloads and checks against `metadata.yaml`:

- for sales 231, 233, 235, 238, 241, 246, 247 and 248 (August 2013 to March 2016): `data.zip`, the statistics sheet (a PDF, saved as `stats.html` for historical reasons) where BOEM publishes one, and the final bid recap where BOEM publishes one;
- for sales 249 (August 2017) to BBG3 (August 2026): the parsed bid table `case-study/data/bids.csv` of the game- and auction-theory series at [GitLab commit d03cdf8](https://gitlab.com/DiogoRibeiro7/game-auction-theory-ds/-/tree/d03cdf890ee1b2ab40919317d63875c872ee0add/case-study), which is built from BOEM's files and checked there against BOEM's published totals.

## Why the bytes are not mirrored

BOEM is the authoritative byte source; the URLs are BOEM's final file locations, and the checksums pin the files used.
