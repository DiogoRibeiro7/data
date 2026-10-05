# Legacy data quarantine

This directory contains historical data that cannot yet be promoted to the canonical registry or replaced safely by an authoritative external source.

After the 2026-10-03 re-audit, two packages remain:

- `country-age-sex-2019`
- `portugal-covid19`

Each remaining package has a concrete documented blocker. Legacy quarantine is not a staging area for new data.

Resolved packages were either removed as obsolete project inputs or replaced with external source records when the upstream source could be identified. External records may still carry unresolved snapshot or redistribution status, which is documented explicitly.

See:

- [current inventory](INVENTORY.md)
- [legacy resolution audit](../docs/migrations/LEGACY_RESOLUTION.md)
- [phase-four legacy re-audit](../docs/migrations/LEGACY_REAUDIT_2026-10-03.md)


## Structured unresolved evidence

Remaining quarantine packages may use the optional metadata `resolution`
block to distinguish actionable research from terminal quarantine decisions.

See [provenance and licensing resolution evidence](../docs/PROVENANCE_RESOLUTION.md).
