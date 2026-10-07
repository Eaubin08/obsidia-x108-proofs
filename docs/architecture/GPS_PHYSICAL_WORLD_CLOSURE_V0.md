# F21 — GPS Physical-World Closure V0

Status: VERIFIED / NO F21 REGRESSION

## Purpose

Close the recorded-real GPS physical-world path across the new world stack without rewriting the existing GPS domain gate.

F21 reuses:
- F5 `RecordedGpsEvidenceV0`
- F5 MMonde/UDIP bridge
- F20 `CrossModalCoherenceReportV0`
- existing `GpsX108Gate` / Reality Authenticity Gate

## Existing real evidence preserved

The repository already contains:
- recorded real NOAA/NGS RINEX evidence;
- recorded real public GNSS I/Q processed through GNSS-SDR;
- the existing GPS domain reality-authenticity gate;
- X108 HOLD receipts for recorded-real paths;
- explicit receiver/configuration blockers for hostile/live work.

F21 does not duplicate those artifacts.

## Contract

`GpsPhysicalWorldClosureV0` binds:
- recorded evidence id/proof level;
- MMonde world-state ref;
- UDIP domain-state ref;
- optional F20 cross-modal report ref;
- receiver status;
- blockers;
- bounded public claim scope.

## Claim boundary

For `RECORDED_REAL_GNSS` and `RECORDED_REAL_RF`, F21 preserves those exact claim scopes.

It does not upgrade them to:
- LIVE GNSS;
- hostile/live spoofing closure;
- sensor attestation;
- physical authenticity;
- action authority.

The following remain explicit blockers where applicable:
- `LIVE_SENSOR_ATTESTATION_NOT_PROVEN`
- `MULTI_SOURCE_CORROBORATION_NOT_PROVEN`
- `RECEIVER_CONFIGURATION_BLOCKED`
- `GENERATED_MODALITY_NOT_PHYSICAL_TRUTH`
- `PHYSICAL_EVIDENCE_REFS_MISSING`

## Gate bridge

`gps_closure_to_gate_payload_v0()` creates a conservative payload for the existing GPS P3-05 gate.

Critical rule:

`recorded provenance != live sensor attestation`

Therefore recorded evidence always enters with:
- `sensor_attested = False`
- `attestation_ready = False`

unless a future dedicated live-attestation closure is separately proven.

`build_gps_domain_gate_state_v0()` evaluates only the local domain-state gate and performs no HTTP/kernel call.

## Expected behavior

A recorded-real GNSS/RF observation can be real and still correctly produce a GPS domain fail-closed state because:
- real recording does not prove current/live origin;
- GNSS alone does not prove multisource coherence;
- no private sensor attestation is proven.

That is the intended boundary, not a failure.

## Authority

F21 remains:
- readonly;
- advisory only;
- `KX108_ONLY`;
- no decision;
- no ACT;
- no live-claim promotion.

## Next phase

F22 — Real E2E Demonstrations.

No F22 runtime before F21 validation.

## Verification finale

- Code SHA vérifié: `18641e67e2b0c8a48edc7b2c7de7cb504b1cfac2`
- GitHub Actions run: `37569069930`
- Résultat global: `12545 passed / 11 failed / 46 skipped / 207 deselected`
- Failures F21 visibles: `0`
- Les 11 failures restantes correspondent aux familles baseline historiques.

**Verdict:** F21 `VERIFIED`.
