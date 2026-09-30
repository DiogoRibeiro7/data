# Dataset migration policy

Existing repositories contain a mixture of reusable source datasets, local fixtures, synthetic examples, generated outputs, and third-party files. Migration therefore requires classification before copying.

## Classification

Each discovered data file or logical dataset must be classified as one of:

| Classification | Action |
| --- | --- |
| Canonical reusable data | Migrate into this repository |
| Project-local fixture | Keep in the consuming project |
| Synthetic/example data | Keep local unless it has independent teaching/reference value |
| Derived reproducibility snapshot | Migrate only when it has durable cross-project value |
| External source, redistribution unclear | Store retrieval metadata/instructions; do not republish bytes |
| Private/sensitive/restricted | Do not migrate |
| Duplicate/obsolete | Remove only after references are updated and verified |

## Migration sequence

For each source repository:

1. inventory candidate files;
2. identify logical datasets rather than migrating file-by-file;
3. establish provenance and redistribution terms;
4. detect exact and near duplicates;
5. create the canonical dataset package;
6. compute and record SHA-256 checksums;
7. update downstream consumers to use a pinned canonical reference;
8. run the consumer's tests or reproducibility checks;
9. remove redundant copies only after consumers succeed;
10. add a deprecation note when an entire legacy data repository is superseded.

## Consumer references

A consuming project should pin:

- a repository tag, release, or commit;
- the canonical dataset path;
- the expected SHA-256 checksum.

Where downloading is appropriate, use a small deterministic fetch helper rather than checking large shared data into every project.

Projects may retain small local fixtures to keep unit tests fast and independent of network access.

## Historical integrity

Migration should not rewrite historical repositories solely to erase evidence of old data locations.

Prefer ordinary commits and documented deprecation. Preserve enough history to understand where a dataset came from and why it moved.

## Review checklist

Before approving a migration:

- [ ] provenance is known;
- [ ] redistribution is permitted;
- [ ] dataset slug follows repository conventions;
- [ ] metadata is complete;
- [ ] checksums are recorded;
- [ ] duplicates have been investigated;
- [ ] downstream consumers have been identified;
- [ ] private or sensitive content has been excluded;
- [ ] removal from source repositories will not break reproducibility.
