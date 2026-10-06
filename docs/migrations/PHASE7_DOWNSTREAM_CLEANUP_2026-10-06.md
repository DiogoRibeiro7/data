# Phase 7 downstream cleanup audit — 2026-10-06

## Scope

This audit follows the Phase 7 canonical promotions of:

- `ons-gross-median-weekly-pay`;
- `unhcr-refugee-population-2024`.

The goal is to remove redundant downstream copies and stale floating source
paths without deleting intentional synthetic fixtures or project-specific
derived data.

## displacement-risk-lab-dynamodb

### Retained

The committed files under `data/raw/` are deterministic **synthetic fixtures**
used by offline demos, CLI examples, and tests.

They are not copies of canonical UCDP or UNHCR data and remain intentionally
local.

The live UNHCR API helper also remains. It serves current-data workflows and is
not treated as a reproducible historical snapshot. Reproducible UNHCR 2024
workflows use the checksum-pinned canonical registry object instead.

### Removed

`reports/sample_run/raw/` contained regenerated copies of the same synthetic
sample inputs already present under `data/raw/`.

Those duplicate report inputs are removed in:

- `DiogoRibeiro7/displacement-risk-lab-dynamodb#8`.

The directory is now ignored because `offline-sample-run` regenerates it.

## city-wage-cost-global

The maintained standalone project now consumes ONS gross median weekly pay from
an exact registry commit/path/SHA-256 contract.

The separate ONS housing-affordability input remains upstream-managed because it
was not promoted in the first Phase 7 batch.

No duplicate canonical ONS weekly-pay bytes are committed locally.

## ds-projects-portfolio

The portfolio contained a full historical copy of
`projects/city_wage_cost_global/`.

That copy had drifted from the standalone repository and still used a floating
ONS `main` URL for weekly pay.

The portfolio scope contract states that duplicated/historical project trees
should not remain in the active public surface when a focused standalone
repository is authoritative.

The duplicated project tree is therefore removed in:

- `DiogoRibeiro7/ds-projects-portfolio#656` (closes portfolio issue #655).

The root portfolio README already links to
`DiogoRibeiro7/city-wage-cost-global`, which remains the maintained source of
truth.

## Final disposition

| Item | Decision | Rationale |
| --- | --- | --- |
| `displacement-risk-lab-dynamodb/data/raw/*` | retain | deterministic synthetic fixtures |
| `displacement-risk-lab-dynamodb/reports/sample_run/raw/*` | remove | generated duplicates |
| live UNHCR API helper | retain | current-data workflow, distinct from immutable snapshot |
| canonical UNHCR 2024 registry path | retain | reproducible historical contract |
| ONS weekly-pay floating URL in standalone project | removed by Phase 7 migration | replaced by pinned registry contract |
| ONS housing-affordability floating URL | retain | not part of first Phase 7 promotion |
| `ds-projects-portfolio/projects/city_wage_cost_global/` | remove | stale duplicate of maintained standalone repo |

## Acceptance result

- redundant downstream copies identified;
- safe duplicates removed;
- intentionally local fixtures have explicit rationale;
- canonical consumers point to exact registry commit/path/SHA-256 contracts;
- no new canonical consumer is invented for the deleted portfolio mirror.
