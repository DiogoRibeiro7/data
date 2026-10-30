# Metro do Porto GTFS — 7 September 2026

The [Porto municipal open-data portal](https://dadosabertos.cm-porto.pt/dataset/horarios-paragens-e-rotas-metro-porto)
publishes historical Metro do Porto timetable archives in the General Transit
Feed Specification (GTFS) format. The publisher is Metro do Porto, S.A.

## Identified snapshot

- Resource: [GTFS Metro do Porto 07-09-2026](https://dadosabertos.cm-porto.pt/dataset/713a680c-9e19-11f1-84ed-6abdb6d5cf34/resource/ed724df6-2dda-467c-a6d5-cb027426d82c/download/horarios_gtfs_mdp_07_09_2026.zip).
- Archive filename: `horarios_gtfs_mdp_07_09_2026.zip`.
- Source snapshot date: 7 September 2026; portal last-update display:
  8 October 2026.
- ZIP SHA-256 recorded in the `porto-metro-demand-analysis` research source
  documentation: `38eef4e6e3b93b36cc92e8ffede8844845dac792721dc7a48d666b89f7b56010`.
- Relevant GTFS tables: `routes.txt`, `trips.txt`, `stops.txt`,
  `stop_times.txt`, `calendar.txt` and `calendar_dates.txt`.
- Coverage: route `B` and express route `Bexp`, alongside other Porto routes.

The hash is a downstream recorded file digest, **not** an immutable upstream
revision identifier. The ZIP is not copied into this registry.

## Interpretation

GTFS describes scheduled service and stops. It contains **no passenger
validations or observed demand**. Counting scheduled trips, stop events or
service dates cannot establish how many people actually travelled.

## Reuse terms

The previous official Porto [open-data catalog](https://opendata.porto.digital/dataset/?_tags_limit=0&license_id=cc-zero&organization=metro-do-porto&res_format=GTFS&res_format=ZIP&sort=views_recent+desc)
listed Metro do Porto GTFS under the CC0 filter. The current migrated
[dataset page](https://dadosabertos.cm-porto.pt/dataset/horarios-paragens-e-rotas-metro-porto)
clearly identifies publisher and ZIP but does not visibly restate the licence
for this exact resource in its accessible page view.

The registry therefore does **not** infer continuing CC0 coverage without a
resource-specific check. Source attribution should read **Metro do Porto,
S.A., via the Município do Porto's Open Data Portal**, with snapshot date.

**External reference only; redistribution unresolved pending a licence check.**
An eventual canonical snapshot would also require a fresh checksum comparison
and a real pinned downstream consumer migration.
