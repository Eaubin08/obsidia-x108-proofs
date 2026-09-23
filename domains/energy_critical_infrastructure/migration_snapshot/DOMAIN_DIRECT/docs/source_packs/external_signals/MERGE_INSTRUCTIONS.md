# Merge Instructions for RSSI Zip

Apply this patch to the RSSI zip by copying the directories into the RSSI pack root.

## Append files

Append:

- `merge_appendices/06_COMPONENT_INDEX_APPEND.csv` to `06_COMPONENT_INDEX.csv`
- `merge_appendices/07_COMPONENT_SPEC_MATRIX_APPEND.csv` to `07_COMPONENT_SPEC_MATRIX.csv`
- `merge_appendices/08_METRIC_DICTIONARY_APPEND.yaml` into the metric dictionary
- `merge_appendices/09_FORMULA_DICTIONARY_APPEND.md` into the formula dictionary
- `merge_appendices/10_INVARIANTS_APPEND.md` into the invariants file

## Copy files

Copy these directories:

```text
component_specs/
family_specs/
packets/
tests/
proof/
```

## Update expected counts

If RSSI pack currently has N components, after this patch:

```text
N_new = N + 24
```

If current base pack follows the 458-component structure:

```text
458 -> 482 components
513 -> 537 total files if full granular mode
```

## Validation

Required checks:

```text
- all 24 new components have DECISION_AUTHORITY = KX108_ONLY
- all 24 new components have can_emit_ACT = false
- all 24 new components have metrics
- all 24 new components have formulas
- all 24 new components have tests
- all 24 new components have proof artifacts
```
