# GPS P5 — CAUSAL SUPPORT V0

Status: VERIFIED OBSERVATIONAL SUPPORT / CAUSAL ATTRIBUTION NOT CLOSED  
Decision authority: KX108_ONLY

## Purpose

P5 evaluates how far the currently verified recorded evidence supports causal interpretation without promoting correlation into a spoofing-causality claim.

The P5 evaluator is deterministic, evidence-only, emits no operational verdict, and cannot authorize action.

## Inputs already verified

- P4 classifier decision is ANOMALY.
- The classifier did not consume hostile truth or official onset.
- First anomaly transition: receiver 132 s -> 174 s.
- Official FGI onset used only after the detector decision: 135 s.
- GNSS-SDR observed displacement: 14640.407 m ECEF.
- FGI-GSRx observed displacement: 14639.336 m ECEF.
- Cross-receiver difference: approximately 1.071 m.
- Separate recorded real RF CTTC nominal control: NOMINAL.

## Deterministic assessment

These checks are satisfied:

- truth-free detector decision;
- ANOMALY present;
- official event boundary is straddled by the first anomaly transition;
- two receiver implementations reproduce the same displacement within 0.1% relative error;
- the real CTTC nominal control remains clean;
- both receiver implementations operate on the same recorded FGI RF source.

Therefore the current support level is:

`STRONG_OBSERVATIONAL_SUPPORT_NOT_CAUSAL`

## Why causal attribution remains open

The following are still absent:

- independent physical-source corroboration;
- controlled intervention / HIL-style causal isolation;
- held-out hostile validation.

Therefore P5 explicitly forbids these claims:

- `SPOOFING_CAUSED_THE_OBSERVED_DISPLACEMENT`
- `GENERAL_SPOOFING_DETECTOR_VALIDATED`
- `SPOOFING_RESISTANCE_PROVEN`

## Method change

Held-out MCD/TGD/TGS downloads are no longer on the critical path.

They remain valuable future validation assets, but P5 proceeds with the evidence already acquired. This avoids blocking the project on a multi-gigabyte external file while preserving the causal claim boundary.

## Next useful work

P5 can now focus on the smallest missing causal discriminator rather than more replay plumbing:

1. independent physical-source corroboration contract;
2. controlled intervention/HIL evidence contract;
3. later held-out hostile generalization when convenient.

P4 remains frozen; its thresholds are not modified.
