# GPS P6 Held-Out Corpus Contract V0

Status: `CONTRACT_READY / NO_NEW_HELDOUT_DATA_YET`

## Goal

Define exactly what may enter the first honest P6 held-out confusion matrix.

This contract validates a **trajectory-discontinuity classifier only**. It does not validate spoofing, hostility, causality, resistance, production use, or aviation safety.

## Admission requirements

A case may be tagged `HELD_OUT` only when all of the following are true:

- P4 thresholds were frozen before the case entered the evaluation flow;
- the case was not used for threshold selection;
- the case was not used during classifier development;
- the reference/truth label was invisible to the classifier;
- classifier output was sealed before reference unseal;
- RF artifact, classifier output, and reference manifest each have SHA-256 provenance;
- provider/dataset/acquisition/license-or-authorization provenance is present;
- the source is independent from the development corpus.

## Explicit anti-recycling rule

The current development evidence may not be relabeled as held-out:

- `FGI_UT_DFMC_L1E1_DEVELOPMENT`
- `CTTC_REAL_RF_NOMINAL_DEVELOPMENT_CONTROL`

They remain useful development evidence, not blind validation.

## Classes needed

P6 requires both:

- `TRAJECTORY_DISCONTINUITY_PRESENT`
- `TRAJECTORY_DISCONTINUITY_ABSENT`

Only after at least one valid held-out case exists in both classes may the matrix code run. More cases are required before any serious performance claim should be considered.

## Governance

- `decision_authority = KX108_ONLY`
- readonly
- no ACT
- no verdict emission
- no memory write
- no kernel/X108 mutation
- `certification_status = NOT_CERTIFIED`
