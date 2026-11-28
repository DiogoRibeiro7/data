# European Commission AMECO database, autumn 2026 release

[AMECO](https://economy-finance.ec.europa.eu/economic-research-and-databases/economic-databases/ameco-database_en) is the annual macro-economic database of the Commission's Directorate-General for Economic and Financial Affairs. It is updated with every full Commission forecast, spring and autumn, and carries the forecast years alongside the outturns.

## Consumer contract

`Medium-Blog/portugal-fiscal-reaction` downloads the bulk file `ameco0.zip` (7,275,181 bytes; 18 semicolon-separated text files) and checks it against the SHA-256 in `metadata.yaml`. It extracts the following series for the 27 member states, 1994–2025:

- gross debt `UDGG`, primary balance `UBLGIE` and interest `UYIGE`, on the excessive deficit procedure basis, in % of GDP;
- the output gap `AVGDGP` and the cyclically adjusted primary balance `UBLGBP`;
- GDP at current and 2020 prices `UVGD` and `OVGD`, the GDP deflator `PVGD`, and the long-term interest rate `ILN`.

The general government series start in 1995. The forecast years 2026–2028 are dropped. For Portugal, the 2025 values match Eurostat's October 2026 EDP notification (see `eurostat-portugal-government-finance`).

## Releases

The download URL always serves the latest release, so the hash pins the autumn 2026 release (zip members dated 16 November 2026, retrieved 22 November 2026). The next spring forecast replaces it. The consumer then prints the new hash and stops unless run with `--accept-revision`. To move the pin, record the new hash here and in the consumer's `data_sources/` contract.

The Commission re-issued the file with members dated 24 November 2026 (7,351,615 bytes, SHA-256 `e1d7611367873bac89d2328bd559bf05c116c40fb233683eca69b88ec1ecd526`, retrieved 28 November 2026). `Medium-Blog/social-contract-break-dates` pins this re-issue (contract `data_sources/ec-ameco-autumn-2026-2026-11-24.json`) and reads the adjusted wage share `ALCD0` and the unemployment rate `ZUTN` for 1960-2025, for the United States, the United Kingdom, West Germany (`D_W`, to 1990), Germany and ten other European countries. The three Portugal consumers keep the 16 November pin.

## Reuse and registry decision

Commission data are reusable with acknowledgement under Commission Decision 2011/833/EU, per the Commission's legal notice. Attribution should name the European Commission, AMECO, the release and the access date.

**Metadata-only external record.** The Commission remains the byte source. No bytes are mirrored here or in Medium-Blog.
