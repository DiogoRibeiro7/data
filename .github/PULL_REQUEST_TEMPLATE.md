## Summary

<!-- Describe the change and why it belongs in this registry. -->

## Change type

- [ ] Canonical dataset addition or update
- [ ] External source record addition or update
- [ ] Legacy resolution or migration
- [ ] Registry tooling / validation
- [ ] Documentation / governance
- [ ] Other

## Data governance checklist

For changes involving data or source metadata:

- [ ] Provenance is documented with an authoritative publisher/source.
- [ ] Snapshot, version, commit, DOI, or retrieval date is recorded where applicable.
- [ ] Licence / terms are documented.
- [ ] Redistribution status is explicit.
- [ ] Repository licensing does not overwrite upstream data terms.
- [ ] No credentials, secrets, private download URLs, or confidential access details are committed.
- [ ] No private, personal, sensitive, regulated, or restricted data is committed without an explicit approved publication basis.

For canonical stored data:

- [ ] Redistribution of the committed bytes is explicitly allowed.
- [ ] Every data file is declared in `metadata.yaml`.
- [ ] SHA-256 checksums are correct.
- [ ] Raw / derived roles match directory placement.
- [ ] Derived artifacts include lineage.
- [ ] Large-file policy has been reviewed where applicable.

## Generated artifacts

- [ ] `datasets/catalog.json` and `datasets/CATALOG.md` were regenerated when canonical metadata changed.
- [ ] `external/catalog.json` and `external/CATALOG.md` were regenerated when external metadata changed.
- [ ] Generated documentation/catalog files were not edited manually.

## Validation

- [ ] `python -m unittest discover -s tests -v`
- [ ] `python scripts/validate_repository.py`
- [ ] `python scripts/generate_external_catalog.py`
- [ ] `mkdocs build --strict` when documentation/navigation changed

## Consumer impact

<!-- Note affected repositories, old copies to remove, migration requirements, or "none". -->

## Additional notes

<!-- Include issue links, citations, or review context. Do not paste dataset contents. -->
