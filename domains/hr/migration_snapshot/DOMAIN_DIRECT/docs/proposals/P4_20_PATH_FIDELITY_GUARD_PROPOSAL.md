# P4-20 Path Fidelity Guard - Proposal

Status: PROPOSED_NOT_IMPLEMENTED
Scope: GPS / Defense / Aviation V0.1
Date: 2026-08-02

## Purpose

P4-20 should be the runtime guard that verifies a physical path stays faithful to the authorized plan before X-108 allows any action. It must not decide by itself. It produces evidence for the P3-05 gate and the sovereign kernel.

## Current Evidence

- `domain_packets/gps_defense_aviation_decisional_form_v0.yaml` references `path_fidelity_guard: "P4-20"`.
- `domains/gps/gps_x108_gate.py` already checks physical envelope and multi-source coherence.
- `proofs/lean/Obsidia/GeneratedPeripheral/P_DomainKernel_PathFidelity_RequiresCoherence.lean` proves that path fidelity requires coherence.
- `docs/audits/OBSIDIA_BRANCHING_MATRIX_DRAFT_V0.csv` lists `obsidia_core/guardians/path_fidelity_guard.py` as missing/classify-review.

## Proposed Runtime Contract

Input:
- authorized route or route hash
- current GNSS position candidate
- IMU/inertial estimate
- radio or radar confirmation
- timestamp/freshness
- permitted drift bounds

Output:
- `path_fidelity_ok: bool`
- `coherence_ok: bool`
- `drift_bound_ok: bool`
- `authorized_route_ok: bool`
- `replay_consistent: bool`
- `reason_codes: list[str]`
- `evidence_refs: list[str]`

Fail-closed rule:
- If any required source is missing, stale, replayed, contradictory, or outside bounds, return non-authorizing evidence and let P3-05 force `HOLD`.

## Proposed First Implementation

Do not edit sealed kernel files. First add a non-kernel runtime module only after approval, for example:

`obsidia_core/guardians/path_fidelity_guard.py`

The module should be pure, deterministic, and side-effect-free. It should not import network clients and should not mutate Merkle/seal/proof files.

## Required Tests

1. Nominal path: coherent GNSS/IMU/radio, within drift bounds.
2. Spoof path: GNSS diverges from IMU/radio.
3. Replay path: old state attempts to validate current route.
4. Physical breach: speed or g-load exceeds envelope.
5. Non-sovereignty: guard never emits `ALLOW`, only evidence.

## Claim Boundary

This proposal does not complete P4-20. It defines the safe implementation path. Production promotion requires tests, proof mapping, and explicit approval before any protected proof/kernel work.
