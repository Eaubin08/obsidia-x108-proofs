# UDIP Migration Snapshot Compaction V0

Raw snapshot preserved in Git history:

a9ab7e4310098d9758258a7a09bad743c3eda1dd

Canonical main used for duplicate verification:

553df13d7bc8746ba582649d08a07a7f1478d081

Policy:

- exact duplicate migration copies are not retained physically inside Domain Packs;
- their provenance is preserved in MIGRATION_REFERENCE_INDEX_V0.csv;
- every removed copy was revalidated against an identical Git blob in pinned main;
- UDIP-specific migration material is preserved;
- no UDIP-to-main merge is performed by this cleanup;
- KX108 / Binder / runtime authority is not modified.

Exact duplicate migration files removed:

4346

UDIP-specific migration snapshot files preserved:

199
