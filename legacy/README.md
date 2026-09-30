# Legacy data quarantine

This directory contains historical data that cannot yet be promoted to the canonical registry or replaced safely by an authoritative external source.

After the 2026-10-01 resolution audit, five packages remain:

- `country-age-sex-2019`
- `italy-covid19`
- `portugal-covid19`
- `portugal-population-2018`
- `portugal-sico-mortality`

Each remaining package has a concrete documented blocker. Legacy quarantine is not a staging area for new data.

Resolved packages were either removed as obsolete project inputs or replaced with external source records where provenance and reproducibility were sufficient.

See:

- [current inventory](INVENTORY.md)
- [legacy resolution audit](../docs/migrations/LEGACY_RESOLUTION.md)
