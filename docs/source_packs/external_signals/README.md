# OBSIDIA RSSI External Signals Patch V1

This patch adds the missing external-category signal layer for the RSSI pack.

It adds two controlled, non-authoritative blocks:

1. `TIMEVERSE_INSPIRED_TEMPORAL_SIDECAR_V1`
2. `OBSIDIA_CONSEQUENCE_BOUNDARY_ENRICHMENT_V1`

These blocks are not copied runtimes and not kernel authorities. They enrich Obsidia/X108 proof, temporal validation, replay, refusal and RSSI audit vocabulary.

## Authority rule

```text
DECISION_AUTHORITY = KX108_ONLY
No external category signal may emit ACT.
No external category signal may override HOLD/BLOCK/ACT.
No external category signal may mutate KX108.
```

## Files to merge into RSSI zip

- `family_specs/46_external_category_signals.spec.yaml`
- `family_specs/47_timeverse_temporal_sidecar.spec.yaml`
- `family_specs/48_consequence_boundary_enrichment.spec.yaml`
- `component_specs/C459_*.yaml` through `C482_*.yaml`
- `packets/51_temporal_context_header.packet.yaml`
- `packets/52_temporal_receipt.packet.yaml`
- `packets/53_consequence_boundary.packet.yaml`
- `tests/52_EXTERNAL_SIGNALS_TEST_MATRIX.md`
- `proof/53_EXTERNAL_SIGNALS_PROOF_ARTIFACTS.md`
- `merge_appendices/*`
