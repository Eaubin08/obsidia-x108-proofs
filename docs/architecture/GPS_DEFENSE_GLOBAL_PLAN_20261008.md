# GPS Defense — Global Plan & Current State

Date: 2026-10-08  
Status: `ACTIVE_PROGRAM / P6_PHYSICAL_DATA_PAUSED_FOR_STORAGE`

## Purpose

This document is the canonical global GPS Defense plan.

It complements:

`docs/architecture/GPS_P6_RESUME_PLAN_20261008.md`

The P6 resume plan explains exactly how to restart the paused held-out validation work.  
This file explains where the entire GPS Defense program stands and what comes next.

---

## 1. Global objective

Build a governed GPS/GNSS integrity demonstrator that can ingest real physical evidence, detect bounded integrity anomalies, propagate them through the Obsidia cognition/governance stack, and preserve strict authority and proof boundaries.

The system must never silently promote:

- anomaly -> spoofing;
- observational support -> causality;
- development evidence -> held-out validation;
- held-out matrix -> certification;
- Brody/context -> decision authority.

Decision authority remains:

`KX108_ONLY`

---

## 2. Current global state

```text
P1 receiver readiness                         VERIFIED
P2 real passive GNSS acquisition              ARMED / PHYSICAL RECEIVER BLOCKED
P3 multi-source physical corroboration        PREPARED / BLOCKED
P4 recorded RF anomaly classifier             CLOSED
P5 observational support                      CLOSED
P4/P5 -> Brody/SENS                           CLOSED
Brody real runtime semantic join              CLOSED
P6 confusion-matrix readiness                 CLOSED
P6 held-out admission contract                CLOSED
P6 corpus acquisition protocol                CLOSED
P6 first held-out pair                        RESERVED
P6 actual held-out RF execution               PAUSED_FOR_LOCAL_DISK_CAPACITY
P6 honest TP/TN/FP/FN matrix                  BLOCKED_ON_HELDOUT_DATA
P7 controlled live hostile validation         PLANNED / NOT_STARTED
Certification / aviation validation           NOT_CLAIMED
```

---

## 3. Evidence already closed

### Real nominal GNSS

Real RINEX NOAA/NGS ingestion is proven.

### Real nominal recorded RF

CTTC recorded RF has been processed and is retained as nominal development/control evidence.

It must not be relabeled as held-out validation.

### Real hostile recorded RF

FGI-SpoofRepo `UTD_L1_E1.dat` has been processed through real GNSS receiver software.

Known source SHA-256:

`e8da962e92cfdbcb677361ce769a54f26dc385417bac9fd618492dcd02fb2d72`

Observed evidence includes:

- receiver/PVT discontinuity;
- approximately 42 s PVT gap;
- approximately 9 h 48 min GNSS-time jump;
- approximately 14.64 km trajectory displacement;
- close cross-receiver agreement between FGI-GSRx and GNSS-SDR.

This supports anomaly/integrity evidence only.

Canonical P4 claim boundary:

`TRAJECTORY_DISCONTINUITY_ONLY_NO_HOSTILE_OR_CAUSAL_ATTRIBUTION`

Canonical P5 support level:

`STRONG_OBSERVATIONAL_SUPPORT_NOT_CAUSAL`

Forbidden causal promotion remains:

`SPOOFING_CAUSED_THE_OBSERVED_DISPLACEMENT`

---

## 4. Governance closure

The GPS evidence path preserves:

- `decision_authority = KX108_ONLY`
- `allowed_to_decide = false` for Brody/periphery;
- `allowed_to_act = false`;
- `emits_act = false`;
- `emits_verdict = false`;
- `memory_write = false`;
- `kernel_mutation = false`;
- `x108_mutation = false`.

P4 anomaly reaches the governed chain as evidence/context and produces fail-closed behavior without granting Brody authority.

The semantic query path for GPS integrity has also been closed into Brody/SENS with:

- GPS integrity semantic routing;
- deterministic semantic focus;
- no unresolved semantic unknowns for the tested readonly explanation request;
- no contradiction;
- normal reasoning readiness;
- KX108 authority preserved.

---

## 5. P1 — Receiver readiness

Status:

`VERIFIED`

Receiver-side readiness and the existing real recorded-RF replay path are proven enough to support the current development evidence.

No reopening is required unless hardware/runtime changes.

---

## 6. P2 — Real passive GNSS

Status:

`ARMED / BLOCKED_RECEIVER_CONFIGURATION`

The software/gates are prepared.

What is still missing is the physical receiver/live capture configuration required to close actual passive live GNSS validation.

This remains a hardware/physical-source blocker, not a software architecture blocker.

---

## 7. P3 — Multi-source corroboration

Status:

`PREPARED / BLOCKED`

P3 requires independent physical corroboration rather than multiple software receivers replaying the same RF source.

Current cross-receiver agreement is useful observational evidence but does not count as an independent physical source.

Primary blocker:

`NO_INDEPENDENT_PHYSICAL_SOURCE_CORROBORATION`

Future acceptable directions include an independent:

- GNSS receiver/source;
- IMU/inertial source;
- radar/other physical navigation source;
- controlled live capture chain.

Do not fake P3 completeness using two decoders of the same RF recording.

---

## 8. P4 — Recorded RF temporal anomaly classification

Status:

`CLOSED`

Frozen classifier:

`P4_TEMPORAL_DISCONTINUITY_V0`

Development classifier thresholds are frozen before held-out validation.

Development output:

`ANOMALY`

P4 remains a trajectory-discontinuity classifier only.

It is not a spoofing classifier.

---

## 9. P5 — Observational support

Status:

`CLOSED`

P5 closes the observational evidence layer while preserving non-causal wording.

Required blockers remain visible:

- `NO_INDEPENDENT_PHYSICAL_SOURCE_CORROBORATION`
- `NO_CONTROLLED_INTERVENTION`
- `NO_HELDOUT_HOSTILE_VALIDATION`

P5 must not be upgraded to a causal claim without new evidence.

---

## 10. Brody/SENS integration

Status:

`CLOSED`

The P4/P5 evidence reaches the real Brody runtime as readonly cognition/context.

Closed elements include:

- semantic router correction;
- GPS integrity compound route;
- deterministic semantic focus;
- readonly explanation path;
- P4/P5 evidence preservation;
- anomaly -> HOLD preservation;
- non-causal boundary preservation;
- KX108-only authority preservation.

A degraded cognitive join may still appear for unrelated missing optional inputs such as memory/NPL/Lyapunov metrics. That must not be confused with failure of the GPS semantic closure.

---

## 11. P6 — Honest confusion-matrix validation

### P6-A readiness contract

Status:

`CLOSED`

The system knows exactly when a confusion matrix may and may not be computed.

### P6-B held-out admission contract

Status:

`CLOSED`

A case can enter held-out evaluation only if:

- P4 thresholds were already frozen;
- the case was not used for tuning/development;
- truth was hidden from the classifier;
- classifier output was sealed before truth unseal;
- RF/output/reference hashes exist;
- provenance exists;
- source is independent from development corpus.

Development sources explicitly forbidden from relabeling:

- `FGI_UT_DFMC_L1E1_DEVELOPMENT`
- `CTTC_REAL_RF_NOMINAL_DEVELOPMENT_CONTROL`

### P6-C acquisition protocol

Status:

`CLOSED`

Opaque classifier-facing preparation is implemented.

Truth-bearing names such as `spoof`, `clear-sky`, `SS-33`, etc. must not enter P4 input paths.

### P6-D first held-out pair

Status:

`RESERVED / NOT_DOWNLOADED / NOT_ADMITTED`

Reserved pair:

Positive:
`TUNI2025_POSITIVE_SS33`

Negative:
`TUNI2025_NEGATIVE_C5`

Approximate raw RF storage:

`~70 GB`

Current blocker:

`PAUSED_FOR_LOCAL_DISK_CAPACITY`

Exact restart instructions live in:

`docs/architecture/GPS_P6_RESUME_PLAN_20261008.md`

### P6-E first matrix

Status:

`BLOCKED`

Current honest state:

```text
heldout_positive_admitted = 0
heldout_negative_admitted = 0
ready_to_compute_matrix = false
```

The first 2-case matrix will prove only end-to-end held-out plumbing.

It will not justify a performance claim.

### P6-F real evaluation corpus

Status:

`FUTURE`

After the first pair works, expand to multiple untouched positives and negatives.

Candidate families:

- additional Tuni2025 scenarios;
- TEXBAT;
- eventually independent locally captured physical scenarios.

Only then begin evaluating meaningful:

- TP;
- TN;
- FP;
- FN;
- coverage;
- recall;
- false-positive rate;
- false-negative rate.

Do not publish rates when sample counts are insufficient.

---

## 12. P7 — Controlled live hostile validation

Status:

`PLANNED / NOT_STARTED`

This is the later physical validation step.

Goal:

Create a controlled intervention where the physical condition is intentionally manipulated under an authorized test setup and where the intervention itself can be compared with the system response.

This is necessary to move beyond observational support toward stronger causal evidence.

It must only be performed in an authorized RF-safe/laboratory setup.

P7 must not begin by weakening the existing P4/P5/P6 boundaries.

---

## 13. Global execution order from today

### Current pause

Do not spend more time on P6 RF execution until storage is available.

### While storage is unavailable

Work may continue on independent GPS Defense tasks that do not contaminate the held-out evaluation, especially:

1. P2 physical receiver/live acquisition preparation;
2. P3 independent-source integration preparation;
3. P7 controlled-intervention test-plan design;
4. documentation/demo/public presentation layers;
5. broader regression and proof packaging.

Do not tune P4 against any reserved P6 held-out scenario.

### When storage becomes available

Resume in this exact order:

1. use `GPS_P6_RESUME_PLAN_20261008.md`;
2. download reserved SS-33 and C-5 RF;
3. verify MD5 and compute SHA-256;
4. create opaque classifier inputs;
5. run frozen P4 blindly;
6. seal outputs;
7. unseal truth;
8. admit cases through P6 contract;
9. compute first matrix;
10. expand held-out corpus;
11. return to independent physical-source corroboration;
12. prepare/execute controlled intervention;
13. reassess claims.

---

## 14. What is actually proven today

Allowed summary:

Obsidia GPS Defense has a real recorded-RF evidence chain, a frozen bounded trajectory-integrity anomaly classifier, a governed P4/P5 -> Brody/SENS path, fail-closed KX108 authority preservation, and a complete held-out validation protocol ready for new independent evaluation data.

Not proven today:

- spoofing resistance;
- spoofing causal attribution;
- production readiness;
- aviation certification;
- validated false-positive/false-negative performance;
- live hostile RF resilience;
- independent physical-source corroboration.

---

## 15. Global milestone sequence

```text
[✓] P1 receiver readiness
[~] P2 passive live GNSS                 hardware/source blocker
[~] P3 independent corroboration         physical-source blocker
[✓] P4 recorded RF anomaly classifier
[✓] P5 observational support
[✓] Brody/SENS semantic closure
[✓] P6 readiness contract
[✓] P6 held-out admission contract
[✓] P6 acquisition protocol
[✓] P6 first pair reservation
[||] P6 RF execution                     paused: local disk capacity
[ ] P6 first honest matrix
[ ] P6 expanded held-out corpus
[ ] P3 independent physical corroboration closure
[ ] P7 controlled live intervention
[ ] final validation/claim reassessment
```

Legend:

- `[✓]` closed;
- `[~]` prepared but externally blocked;
- `[||]` deliberately paused;
- `[ ]` not closed.

---

## 16. Single next decision

Current next decision is not algorithmic.

It is:

`WHEN_STORAGE_IS_AVAILABLE, RESUME_P6_HELDOUT_EXECUTION_FROM_THE_CANONICAL_RESUME_PLAN`

Until then, keep P4 frozen and continue only work that cannot contaminate the reserved held-out evaluation.
