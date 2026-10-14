# GPS P4 — DEVELOPMENT CLOSURE V0

Status: VERIFIED DEVELOPMENT / BLIND VALIDATION PENDING  
Decision authority: KX108_ONLY

## Physical / receiver evidence

FGI-SpoofRepo UT_DFMC real RF source is SHA-256 bound and replayed with corrected real8 GNSS-SDR semantics.

Two receiver implementations independently reproduce the same approximately 14.64 km displaced solution:

- FGI-GSRx historical ECEF delta: approximately 14639.336 m
- GNSS-SDR corrected real8 ECEF delta: approximately 14640.407 m
- like-for-like difference: approximately 1.071 m

## Deterministic temporal classifier

Algorithm: P4_TEMPORAL_DISCONTINUITY_V0

Development calibration:

- receiver window: 0–120 s
- baseline positions: 156
- baseline transitions: 155
- baseline ECEF step maximum: 16.963550135639597 m
- baseline clock residual maximum: 0.5 s
- baseline receiver gap maximum: 1.0 s

Frozen V0 thresholds:

- ECEF step: 169.63550135639596 m
- clock residual: 5.0 s
- receiver gap: 10.0 s

Detection on the inspected FGI recording:

- classification: ANOMALY
- first anomaly: receiver 132 s -> 174 s
- ECEF step: 14639.905457614153 m
- GNSS clock residual: 35269.5 s
- receiver gap: 42.0 s
- simultaneous violations: 3/3
- truth/onset consumed: false
- status: DEVELOPMENT_POST_HOC_NOT_BLIND

## Domain evidence

Generated evidence:

- temporal_integrity_classification: ANOMALY
- temporal_integrity_evidence_hash: eb7b6ad4b128bcc7a4810208478bb28784162d20b1b6955dc7915f32e914c46c
- emits_verdict: false
- decision_authority: KX108_ONLY
- causal/hostile claim: not made

## GPS DomainState replay

Observed:

- gate verdict: HOLD
- gate source: REALITY_AUTHENTICITY_GATE_FAIL_CLOSED
- reason: TEMPORAL_INTEGRITY_ANOMALY
- nuisances: []
- GPS_SPOOFING: absent
- connector_decides: false
- OS3 ticket valid: true
- state: GPS_DEFENSE_AVIATION_UNTRUSTED

This verifies a fail-closed governance path for a detected temporal-integrity anomaly without promoting the anomaly to spoofing attribution.

## Tests

Targeted local closure:

- 5/5 temporal classifier tests passed
- 12/12 classifier + evidence + GPS gate tests passed
- DomainState replay completed with the expected HOLD boundary

Latest PR CI:

- 12582 passed
- 46 skipped
- 207 deselected
- 11 failures

The 11 CI failures are outside the P4 change surface and fall in existing infrastructure / environment families: Brody/Sigma route expectations, missing Lean `lake`, batch execution, branching ledger identity, and CI git author identity.

No P4 test appears in the failure list.

## Closure verdict

P4 development classifier and governance binding: VERIFIED.

Not yet closed:

- blind hostile validation on held-out data
- TP/TN/FP/FN
- causal spoofing attribution
- spoofing resistance
- P2 physical live-passive capture
- P3 independent physical source
- controlled live hostile lab
- aviation certification/validation

Next gate: freeze V0 unchanged and evaluate held-out nominal and hostile data with truth disclosed only after decisions.
