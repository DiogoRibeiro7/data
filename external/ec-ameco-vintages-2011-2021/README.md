# European Commission AMECO database, archived releases 2011–2021

The [AMECO archive](https://economy-finance.ec.europa.eu/economic-research-and-databases/economic-databases/ameco-database/ameco-archive_en) keeps the database as it was released with each past Commission forecast. Each release carries the Commission's estimates at that date, including the output gap, potential output and the structural balance for every year in the database. Comparing releases shows how those estimates were revised.

## Consumer contract

`Medium-Blog/portugal-realtime-output-gap` downloads seventeen archived releases from the legacy path `https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/<release>.zip`:

- spring and autumn 2011 to 2018;
- autumn 2021.

It checks each file against the SHA-256 in `metadata.yaml`, then extracts these series for the 27 member states:

- the output gap `AVGDGP`;
- real GDP `OVGD` and potential GDP `OVGDP`;
- the structural balance `UBLGAPS`, the cyclically adjusted balance `UBLGAP` and the cyclically adjusted primary balance `UBLGBP`;
- the headline balance `UBLGE`.

The current release is the benchmark. It is registered separately as `ec-ameco-autumn-2026`.

## Coverage

The 2019 and 2020 releases, spring 2021 and the 2022–2025 releases are not available under the legacy path and are not part of this record. The autumn 2021 file nests the chapter files inside `ameco0.zip`; the consumer reads both layouts. The structural balance `UBLGAPS` first appears in the spring 2013 release.

## Reuse and registry decision

Commission data are reusable with acknowledgement under Commission Decision 2011/833/EU, per the Commission's legal notice. Attribution should name the European Commission, AMECO, the release and the access date (22 November 2026).

**Metadata-only external record.** The Commission remains the byte source. Archived releases do not change, so the pins are permanent. No bytes are mirrored here or in Medium-Blog.
