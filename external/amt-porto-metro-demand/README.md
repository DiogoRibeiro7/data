# AMT Metro do Porto demand and service statistics

The [AMT Observatory](https://observatorio.amt-autoridade.pt/publicacao/metros-evolucao-da-procura-e-da-oferta)
publishes demand and service indicators for Portuguese metro systems. Its
Metro do Porto views provide annual and monthly `Passageiros` and
`Comboios-Km` by line, and a separate
[`Troços` view](https://observatorio.amt-autoridade.pt/en/publicacao/metro-porto)
of passenger flows over station-to-station sections.

## Recorded research observations

The downstream `porto-metro-demand-analysis` research (GitLab, private)
transcribed the following public displays, mainly on 29–30 October 2026.
Files are **project-local research transcriptions**, not AMT-provided raw CSV
downloads. Their checksums below were verified against the project's exact
commit `b35a2337949b71db0ad4e1ecb995f4091986620e`.

| Local CSV | Scope | Project-local SHA-256 |
| --- | --- | --- |
| `amt_line_b_monthly_2019_2024.csv` | 72 Line B months: passengers and train-km in thousands | `e972556433cee3dfc1fb4f1019618ec9806171f210bf1756c422a9a7777a0715` |
| `amt_porto_annual_lines_2019_2024.csv` | Six lines, six years | `bd12f27888c30b033a3af4a2a01f772bbaa29eee04aebb750d34dfb55179e6a3` |
| `amt_porto_annual_network_2019_2024.csv` | Annual network totals | `1184f92e370567500ab645400827273ce175c8ffeba94a809cb7c0a748af5238` |
| `amt_porto_line_b_coastal_segments_2019_2024.csv` | Ten coastal Line B links, six years | `e60e2966c62c713e4057ddeec18c362eade65a748663d99ba12e26d8ae7b38fe` |
| `amt_porto_d_f_exclusive_sections_2019_2024.csv` | Four D/F links, six years | `9a799611844425fd6d59c43c6e7b1aa19410867675c342f5c0304cbb8bec7165` |
| `amt_porto_a_c_e_exclusive_sections_2019_2024.csv` | Six A/C/E links, six years | `a5a31c860664b6c228b2b2cd658a76bf17afe6adef230af359094e22514819a8` |
| `amt_porto_operator_report_passengers_2022_2024.csv` | Exact annual whole-network passengers from AMT reports | `4405f1b39ac9bd291d462001819127e82ffb46d1e4eab54ed9fcbd4fa147bfc2` |

For the exact annual series, see AMT's statutory operator-performance
reports for [2022](https://www.amt-autoridade.pt/media/5604/2022_relatorio_desempenho_mpsa.pdf),
[2023](https://www.amt-autoridade.pt/media/5613/2023_relatorio_desempenho_mpsa.pdf),
and [2024](https://www.amt-autoridade.pt/media/5618/2024_relatorio_desempenho_mpsa.pdf).
They provide 65,185,811, 79,140,752 and 89,780,447 reported annual
passengers respectively. These round to the AMT dashboard network values.

## Measurement restrictions

- Line-level `Passageiros` is an AMT allocation, not a direct observation of
  boardings at individual stations; the shared-trunk allocation rule is not
  independently established.
- `Troços` flows measure traversals of consecutive-station sections, not
  unique passengers, entries, exits or card validations. A journey can
  traverse several links, so summing link flows double-counts journeys.
- Station-activity intervals calculated from adjacent links are conditional
  *model bounds*, **not observed station demand**.
- Monthly and annual dashboard figures are rounded to the displayed thousand;
  transcription hashes do not turn them into upstream immutable releases.
- The exceptional 2022–2023 redistribution between published line totals
  remains unexplained. Avoid causal or operator-error claims.

## Rights and registry decision

The named AMT dashboards and reports are publicly available. An explicit
dataset-specific reuse licence for mirroring these transcribed tables was not
identified in the examined source pages on 30 October 2026. Portuguese public
sector information rules are not being used as a substitute for a confirmed
licence covering these particular extracted tables.

**External reference only; redistribution unresolved.** No transcribed AMT
values or PDF files are copied here. Canonical promotion requires an
authoritative rights decision and exact reproducible snapshot contract.
