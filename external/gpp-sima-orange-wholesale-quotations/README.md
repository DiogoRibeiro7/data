# GPP SIMA orange quotations — Portuguese wholesale markets

Metadata-only reference to market quotations obtained from Portugal's
**Sistema de Informação de Mercados Agrícolas (SIMA)**, operated by the
**Gabinete de Planeamento, Políticas e Administração Geral (GPP)**.

## Official source and extraction

- [GPP SIMA source description](https://www.gpp.pt/index.php/sima/sima-2018)
- [Official wholesale-market consultation](https://regsima.gpp.pt/regsima/consulta/mercados?tm=11)
- [GPP consultation and CSV export guide](https://www.gpp.pt/images/Agricultura/SIMA/SIMA_Manual.pdf)
- [GPP methodology](https://www.gpp.pt/images/Agricultura/Documento_Metodologico.pdf)

The downstream consumer documents this **manually exported** selection:

| Property | Documented value |
| --- | --- |
| Query | Sector `Frutos Frescos`, species `Laranja`, all wholesale markets |
| Requested period | 2025-01-01 through 2026-10-31 inclusive |
| Retrieval date | 2026-11-05 |
| Observed quotation dates | 2025-01-02 through 2026-10-30 |
| Observations | 3,412 quotation rows |
| Markets | MAC (1,620), MAP (1,059), MARL (733) |
| Export format | Latin-1, semicolon-delimited CSV |
| Original CSV size | 461,934 bytes |
| Original CSV SHA-256 | `b039f254b4fb18a41b7997208a43ceae46ee9f48db978934ab9fad6de9e24da0` |

These export properties and the SHA-256 are **reported by the consumer**, not
independently recomputed from the government download. In particular, the
export guide's generic delimiter instruction differs from the delimiter in
the actual archived export. Do not substitute the guide's format for the
observed file layout.

There is no known immutable government URL for this specific filtered export.
The live consultation may yield different observations if used at a later
date. For exact replay, use the downstream project's pinned archive and its
checksum verification rather than treating the live query as a fixed dataset.

## Consumer snapshot

`DiogoRibeiro7/ds-projects-portfolio` uses the source for a separate R-based
orange-storage decision study. The following links pin a public consumer
revision, not an upstream government version:

- [Data source and query documentation](https://github.com/DiogoRibeiro7/ds-projects-portfolio/blob/4eab39afadd0548d4e58b1762994a955c7760d9e/projects/orange_storage_decision/MARKET_PRICES.md)
- [Archived gzip-compressed CSV](https://github.com/DiogoRibeiro7/ds-projects-portfolio/blob/4eab39afadd0548d4e58b1762994a955c7760d9e/projects/orange_storage_decision/data/raw/sima_oranges_wholesale_2025-01-01_2026-10-31.csv.gz)
- [Base-R ingestion and validation](https://github.com/DiogoRibeiro7/ds-projects-portfolio/blob/4eab39afadd0548d4e58b1762994a955c7760d9e/projects/orange_storage_decision/R/sima_market_prices.R)

SIMA reports minimum, maximum and most-frequent **market quotations**, not
necessarily executed transaction prices, retail selling prices, or
lot-specific storage outcomes. Product grades, regions, packaging, origin
and markets vary. Pooling them as if they were one homogeneous national
orange-price series would discard important comparability information.

## Redistribution and preservation decision

The [GPP legal notice](https://www.gpp.pt/index.php/avisos-legais/avisos-legais)
allows **reproduction of part of the information** when the source is
acknowledged, acquisition is lawful and protected data are respected. The
notice does not explicitly grant redistribution of a **complete SIMA CSV
export** in a separate public registry.

Consequently, this record remains **external only**, with
`redistribution: unresolved`. The registry does not copy either the original
CSV or the downstream gzip archive, and it does not declare an open-data
licence for those bytes. The restriction concerns the additional registry
mirror; it does not independently assess the downstream project's
publication arrangement.

The review is **terminal pending new evidence**: only explicit publisher
permission or applicable full-export reuse terms would justify reconsidering
central preservation. Retain GPP attribution and the consumer's exact
selection, retrieval date and checksum when reusing results.
