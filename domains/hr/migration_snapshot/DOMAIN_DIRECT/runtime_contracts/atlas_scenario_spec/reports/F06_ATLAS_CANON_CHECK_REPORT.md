# F06_ATLAS_CANON_CHECK_REPORT

Status: F06_ATLAS_CANON_CHECK_READY

## Why this check exists

The first F06 terminal run produced F06 files but failed during manifest generation because the manifest pipeline used $.FullName instead of $_.FullName.

The first run reported:
- Atlas rows: 1738
- Atlas zips found: 11
- Atlas zip internal files: 18215

The high zip count likely came from duplicated copies across source locations.

## Repair performed

- Required F06 files checked.
- F06 READY report checked.
- F06 SCOPE_OK checked.
- Atlas XLSX matrix rebuilt.
- Atlas zip inventory rebuilt with SHA256 deduplication.
- SHA256 manifest created.
- No runtime created.
- No .py created.
- No packages created.

## Counts

F78C total rows: 2739
Atlas rows canon: 1738

Atlas zip candidates found: 12
Atlas unique zips by SHA256: 7
Atlas unique zip internal files: 11263

F06 files: 9
F06 manifest rows: 9

.py under runtime_contracts: 0
packages exists: False

## Canon note

Atlas matrix and deduped zip inventory rebuilt.

## Claim-scope

F06 remains:
- SPEC_ONLY
- DOCS_ONLY
- ATLAS_READONLY_ADVISORY_ONLY
- no runtime
- no scenario execution
- no real-world claim
- no memory write
- no graph write
- no X108 bypass

## Verdict

F06_ATLAS_CANON_CHECK_READY