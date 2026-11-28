# ANES Time Series Cumulative Data File, 1948-2016 release, as packaged in the R package anesr (data/timeseries_cum.rda)

External reference, no bytes stored. Publisher: American National Election Studies (University of Michigan and Stanford University); R packaging by James Martherus. Authoritative source: https://electionstudies.org/data-center/anes-time-series-cumulative-data-file/ (free registration). Byte source: `data/timeseries_cum.rda` of https://github.com/jamesmartherus/anesr at commit `21a6c66b1467c73d994700ae14ba72fb7d9c11cb`.

The file holds 59,944 respondents interviewed in 1948-2016 (the 2016 release; later ANES releases add 2020 and 2024). Variables used by the consumer: `VCF0004` (year), `VCF0604` (trust the government in Washington), `VCF0303` (party identification, three categories), `VCF0106` (race), `VCF0113` (political South), `VCF0704a` (two-party presidential vote) and the weight `VCF0009z`.

Cite: American National Election Studies, ANES Time Series Cumulative Data File (1948-2016).

## Files the consumer verifies

| File | Bytes | SHA-256 | URL |
| --- | ---: | --- | --- |
| `external/timeseries_cum.rda` | 7,823,544 | `12d4ff513714842d473a0337586e26f27453dee2bbf520aadca8b622f9bd6e79` | https://raw.githubusercontent.com/jamesmartherus/anesr/21a6c66b1467c73d994700ae14ba72fb7d9c11cb/data/timeseries_cum.rda |

Consumer: `DiogoRibeiro7/Medium-Blog`, folder `social-contract-break-dates`, contract `data_sources/anes-time-series-cumulative-1948-2016.json`.

## Reuse

ANES distributes the file after a free registration and asks for citation. The copy used here comes from a third-party R package; it was not compared byte for byte with a registered ANES download (see the `resolution` block).
