# GPS MULTI-SOURCE CORROBORATION — P3 READINESS V0

Status: PREPARED / BLOCKED UNTIL P2 REAL CAPTURE  
Branch: `feat/gps-multisource-corroboration-p3-readiness-v0`  
Authority: `KX108_ONLY`

## Purpose

Prepare P3 without bypassing P2.

P3 reuses:
- F13 Measurement / Evidence;
- F15 Physical Evidence Plane;
- F20 Cross-Modal Coherence;
- current GPS physical closure.

No new generic sensor-fusion engine is created.

## Critical correction

F15/F20 can treat distinct source refs as compatible with source independence.

For GPS P3 this is **necessary but not sufficient**.

Required rule:

`distinct source_ref != independent physical corroboration`

P3 requires explicit evidence of separate physical chains.

## P3 prerequisite

The primary GNSS observation must already carry:

- `proof_level = REAL_PASSIVE_GNSS`
- `live_capture_observed = true`
- non-generated source

Otherwise:

`P2_REAL_PASSIVE_GNSS_NOT_VERIFIED`

and P3 remains blocked.

## Independent physical source contract

Each source chain binds:

- source ref;
- modality;
- instrument identity;
- physical hardware-chain ref;
- exact configuration ref;
- identity evidence refs;
- immutable source hash refs;
- calibration ref, or an explicit not-applicable justification ref;
- optional explicit time-alignment evidence;
- optional explicit frame-alignment evidence.

Independence requires at minimum:

- different source refs;
- different instrument refs;
- different hardware-chain refs;
- identity evidence on both chains;
- source hashes on both chains.

Two software labels attached to the same physical chain do not count.

## Cross-modal reuse

P3 consumes F20 `CrossModalCoherenceReportV0`.

F20 remains unchanged:
- compatibility only;
- no truth;
- no causality;
- no physical-coherence self-promotion.

P3 adds the domain-specific physical evidence needed to remove only the GPS blocker:

`MULTI_SOURCE_CORROBORATION_NOT_PROVEN`

when the actual evidence warrants it.

## Alignment

Temporal alignment is accepted only with:
- F20 temporal compatibility, or
- explicit time-alignment evidence.

Spatial alignment is accepted only with:
- F20 frame compatibility, or
- explicit frame-transform/alignment evidence.

Different frames or clocks are never silently fused.

## Calibration

Both physical chains must bind:
- a calibration ref, or
- an explicit evidence-backed not-applicable justification.

Missing calibration remains a blocker.

## What P3 can prove

P3 may establish:

`multi_source_corroboration_proven = true`

only when all required gates are satisfied.

It still cannot establish:
- physical truth;
- spoofing causality;
- hostile classification;
- execution authority.

Those remain later gates.

## Negative tests

The P3 readiness suite explicitly covers:

1. complete independent GNSS + IMU chain;
2. distinct source refs on the same hardware chain -> blocked;
3. P2 not REAL_PASSIVE_GNSS -> blocked;
4. missing calibration/justification -> blocked;
5. generated secondary source -> blocked.

## Current state

```text
P1 receiver readiness          VERIFIED
        ↓
P2 real passive GNSS capture  RUNTIME READY / PHYSICAL CAPTURE PENDING
        ↓
P3 multi-source corroboration CONTRACT READY / BLOCKED BY P2
```

No P3 physical-success claim is allowed before a real P2 capture exists and a real independent secondary source is connected.
