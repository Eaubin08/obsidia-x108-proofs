# GPS P4 — HELD-OUT NOMINAL RF CONTROL V0

Status: VERIFIED NEGATIVE CONTROL  
Decision authority: KX108_ONLY

## Input

Public recorded real RF nominal CTTC corpus already present in the repository:

- run log: `hackathons/nativebuilder-gps-defense/runs/iq_cttc_2013_04_04/gnss_sdr_run_stdout_modern.log`
- RF provenance SHA-256: `6489a6630784478f144f20bf872848410dee3b54a20fd8d1bdd9258afccf2976`
- stdout SHA-256: `3291e8d2cffebeeee0411ab467ca4de85b5cdb9253b64df6f4bad13108710ac2`
- proof level: `RECORDED_REAL_RF`
- nominal control was not used to tune P4 temporal thresholds.

## Frozen classifier

Algorithm: `P4_TEMPORAL_DISCONTINUITY_V0`

Frozen thresholds:

- ECEF step: `169.63550135639596 m`
- clock residual: `5.0 s`
- receiver gap: `10.0 s`

No threshold adjustment was made for CTTC.

## Result

- positions: `150`
- transitions: `149`
- overall classification: `NOMINAL`
- ANOMALY transitions: `0`
- UNKNOWN transitions: `0`
- max ECEF step: `1.620613864679828 m`
- max clock residual: `0.5 s`
- max receiver gap: `1 s`

The frozen classifier therefore does not raise a temporal-integrity anomaly on this recorded real nominal RF control.

## Claim boundary

This is one held-out nominal negative control.

It supports specificity against one real nominal corpus, but it is not yet a complete true-negative rate and does not close TP/TN/FP/FN.

Still required:

- additional nominal controls;
- at least one hostile corpus held outside classifier development;
- truth disclosure only after detector decisions;
- aggregate confusion matrix.
