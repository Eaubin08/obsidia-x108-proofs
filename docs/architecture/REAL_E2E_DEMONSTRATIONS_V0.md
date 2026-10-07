# F22 — Real E2E Demonstrations V0

Status: IMPLEMENTED / VALIDATION REQUIRED

## Purpose

Demonstrate the canonical first-world stack on **existing recorded-real artifacts** without pretending to rerun a live sensor or acquisition chain.

F22 re-ingests stored real GPS evidence and replays it through:

```text
stored real artifact
→ RecordedGpsEvidenceV0
→ F5 MMonde / UDIP
→ F21 GPS Physical-World Closure
→ existing GPS Reality Authenticity Gate
→ fail-closed domain state
```

No network call, no live receiver, no new X108 decision is performed by F22.

## Real artifacts used

1. NOAA / NGS RINEX recorded-real GNSS:
   - `artifacts/gps_rinex_noaa_ab02_2026_210_real_result.json`
   - proof level: `RECORDED_REAL_GNSS`

2. CTTC public GNSS I/Q processed through GNSS-SDR:
   - `artifacts/gps_iq_cttc_2013_04_04_recorded_real_rf_result.json`
   - proof level: `RECORDED_REAL_RF`

These are existing repository artifacts; F22 does not fabricate or regenerate them.

## Canonical replay correction

The historical artifacts were produced before the F21 boundary was formalized.

Some historical payloads set `attestation_ready=true` from `eligible_for_physical_claim=true`.

F22 deliberately does **not** reuse that historical interpretation.

Canonical replay applies the current rule:

`recorded provenance != live sensor attestation`

Therefore:
- physical claim eligibility of a recorded dataset is preserved;
- live sensor attestation remains unproven;
- multisource corroboration remains unproven when IMU/radar is absent;
- the current GPS domain gate correctly remains fail-closed.

Historical evidence is preserved as history; current canonical semantics are not retroactively weakened to match it.

## Contracts

- `RealE2EDemoResultV0`
- `recorded_evidence_from_real_artifact_v0()`
- `run_recorded_real_e2e_demo_v0()`

## Expected demonstrations

### Demo A — recorded-real RINEX

Expected:
- claim scope = `RECORDED_REAL_GNSS`
- real recorded evidence preserved
- live claim = false
- physical authenticity = false
- domain state = fail-closed
- reasons include missing live attestation and missing multisource coherence

### Demo B — recorded-real RF

Expected:
- claim scope = `RECORDED_REAL_RF`
- real I/Q processing evidence preserved
- live claim = false
- physical authenticity = false
- domain state = fail-closed
- reasons include missing live attestation and missing inertial corroboration

## What F22 proves

F22 proves that real stored evidence can traverse the **current canonical world contracts** without losing provenance or being upgraded into stronger claims.

It demonstrates the architectural distinction:

```text
REAL RECORDED DATA
        ≠
LIVE AUTHENTICATED REALITY
```

and:

```text
real evidence
→ candidate world state
→ domain translation
→ reality-authenticity checks
→ HOLD/fail-closed when proof is insufficient
```

## What F22 does not prove

F22 does not prove:
- live receiver operation;
- hostile live spoofing detection;
- causal spoofing attribution;
- sensor private-key attestation;
- IMU/radar corroboration;
- production execution authority;
- a new live X108 HTTP run.

## Authority

F22 is:
- offline replay;
- readonly;
- `KX108_ONLY`;
- no decision;
- no ACT;
- no claim promotion.

## Next phase

F23 — Monde UI Final.

No F23 implementation before F22 validation.
