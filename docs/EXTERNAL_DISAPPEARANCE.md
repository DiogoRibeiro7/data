# External-source disappearance and preservation

External source records describe authoritative upstream sources whose bytes are
normally not mirrored by this registry. An upstream source can move, disappear,
or be withdrawn without invalidating its historical provenance.

The machine-readable policy is
`preservation/external-disappearance-policy-v1.json`.

## Availability states

External metadata may optionally declare an `availability` object with one of
five states:

- `live` — the authoritative source is expected to resolve;
- `transient-outage` — temporary failure; provenance must not be rewritten;
- `moved` — the source has a verified replacement URL;
- `permanently-unavailable` — the source is gone and no replacement is known;
- `legal-withdrawal` — access was withdrawn for legal, licensing, privacy, or provider-policy reasons.

`moved`, `permanently-unavailable`, and `legal-withdrawal` require reviewed
evidence. A moved record also requires `replacement_url`.

## Health-check semantics

Live network observations and committed historical state are deliberately
separate.

- timeouts, DNS failures, HTTP 429, and HTTP 5xx are transient warnings;
- a single HTTP 404/410 on a record with no committed disappearance state is
  actionable drift and requires review;
- a committed `moved` state is reported as moved, and the replacement endpoint
  is checked;
- committed `permanently-unavailable` and `legal-withdrawal` states are
  terminal tombstones, not failing live-source checks.

The health checker never turns one network failure into a terminal historical
claim automatically.

## Tombstones

A tombstoned external record remains historically interpretable. Keep:

- its registry ID and title;
- publisher;
- last-known source URL;
- DOI and pinned source commit when available;
- licence/terms evidence;
- reviewed disappearance evidence;
- the date the state was last reviewed.

Do not delete the record merely because the upstream endpoint vanished.

A tombstone means **historically known but no longer live**. It must never be
presented as a currently available source.

## Preservation boundaries

The registry may preserve metadata and last-known immutable identity evidence.
It must not silently mirror source bytes.

Source bytes may be preserved only when separate committed evidence already
permits redistribution. External-layer status alone never grants permission.

For legal withdrawal, privacy withdrawal, or restricted redistribution, the
registry must not preserve or republish bytes merely to bypass the upstream
withdrawal.

## Moving sources

When an authoritative source moves:

1. preserve the old URL as historical identity;
2. record `availability.state: moved`;
3. add the verified `replacement_url`;
4. attach evidence supporting the move;
5. keep source identity and licensing semantics explicit;
6. update downstream discovery only through a reviewed change.

The old endpoint remains part of provenance history rather than being silently
replaced.

## Relationship to provenance debt

A disappearance may also expose unresolved provenance or licensing questions.
Those remain visible through the provenance-debt model.

Availability state answers **whether the source is live and where it moved**.
Provenance debt answers **whether identity, licensing, or redistribution claims
are sufficiently evidenced**. One does not erase the other.
