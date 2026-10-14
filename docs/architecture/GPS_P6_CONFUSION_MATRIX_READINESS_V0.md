# GPS P6 — Confusion Matrix Readiness V0

Status: `READINESS_ONLY`

## Scope

P6 evaluates the frozen P4 classifier as a **trajectory-discontinuity classifier**.

It does **not** classify spoofing, hostility, attack cause, or aviation safety.

Canonical claim boundary:

`TRAJECTORY_DISCONTINUITY_CLASSIFIER_ONLY_NO_SPOOFING_OR_CAUSAL_ATTRIBUTION`

## Current evidence

The current FGI case is development/post-hoc evidence, not held-out validation.
The CTTC nominal recording is a real negative control, but does not by itself close a held-out confusion matrix.

Therefore the present state remains:

`BLOCKED_HELDOUT_CORPUS_INCOMPLETE`

Required before a TP/TN/FP/FN matrix may be computed:

- at least one held-out reference-positive trajectory-discontinuity case;
- at least one held-out reference-negative nominal case;
- frozen P4 thresholds;
- truth/reference labels unavailable to the classifier before classification.

`UNKNOWN` classifier outputs are never silently mapped to TP/TN/FP/FN. They are reported separately and reduce coverage.

## Certification boundary

Even after a held-out matrix can be computed, the result remains:

`HELDOUT_MATRIX_COMPUTED_NOT_CERTIFIED`

Certification/causal claims remain blocked by independent physical-source corroboration and controlled intervention.

## Governance

- `decision_authority = KX108_ONLY`
- readonly
- no ACT
- no verdict emission
- no memory write
- no kernel/X108 mutation
