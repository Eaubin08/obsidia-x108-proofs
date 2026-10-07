# GPS LIVE Controlled Receiver Readiness V0

Status: VERIFIED / HARDENED

## Purpose

Continue the post-freeze GPS plan without reopening F12→F25.

The next unresolved physical-world objective is controlled LIVE receiver closure. This step hardens receiver readiness so that configuration cannot be mistaken for physical proof.

## Search-before-build result

Existing reusable pieces:
- `detect_live_passive_receiver()`
- `run_live_passive()`
- `OBSIDIA_GNSS_DEVICE` / `OBSIDIA_SDR_DEVICE`
- Docker / GNSS-SDR discovery
- Physical Reality Gate
- GPS X108 gate
- existing no-hardware artifact and tests

No new receiver stack is introduced.

## Hardened rule

Before this patch, an environment-configured receiver candidate could be labelled:

`REAL_PASSIVE_GNSS`

with:

`eligible_for_physical_claim = true`

before any live capture was observed.

That is too strong.

The corrected rule is:

`configured candidate != observed live capture`

`configured candidate != verified receiver identity`

`configured candidate != sensor attestation`

`configured candidate != REAL_PASSIVE_GNSS`

A configured candidate now remains:

`STRUCTURED_STATE`

and:

`eligible_for_physical_claim = false`

until actual live receiver evidence exists.

## Current readiness states

### No candidate

- status: `NO_HARDWARE_DETECTED`
- proof level: `STRUCTURED_STATE`
- physical claim: false
- live capture observed: false

### Environment-configured candidate

- status: `RECEIVER_CANDIDATE_CONFIGURED_UNVERIFIED`
- proof level: `STRUCTURED_STATE`
- physical claim: false
- live capture observed: false
- receiver identity verified: false
- sensor attestation proven: false

## Next physical closure condition

A future REAL_PASSIVE_GNSS promotion must bind at minimum:
- actual receiver output/capture;
- immutable input hash;
- capture time;
- receiver identity/configuration;
- current observables;
- calibration/configuration evidence where applicable;
- provenance;
- explicit remaining limitations.

Configuration alone never satisfies this.

A second residual boundary is also hardened:

`eligible_for_physical_claim != sensor_attestation_proven`

Recorded-real or live physical-claim eligibility can never synthesize sensor attestation. The GPS domain payload now sets `sensor_attested` / `attestation_ready` only from explicit `sensor_attestation_proven=true`.

## Authority

Unchanged:

- KX108_ONLY
- receiver readiness does not decide
- physical evidence does not authorize ACT
- provenance/configuration does not prove authenticity

## Validation

Targeted tests and repository CI required before this readiness patch is accepted.


## Verification finale P1

- Verified HEAD: `b301a270a4ec4026b8467bca741cc3dc4cd2eff1`
- GitHub Actions run: `37578072151`
- Global result: `12565 passed / 12 failed / 46 skipped / 207 deselected`
- P1-specific failures: `0`
- Eleven failures remain in the historical baseline families.
- The twelfth failure is the already-observed intermittent `TestApprovalConcurrency::test_concurrent_identical_content_idempotent`, outside GPS/P1 scope.

**Verdict:** P1 `VERIFIED`. No unrelated baseline repair is pulled into the GPS branch.
