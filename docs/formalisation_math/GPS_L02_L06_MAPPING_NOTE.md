# GPS L-02 / L-06 Mapping Note

Status: MAPPING_NOTE_NOT_FINAL_PROOF
Scope: GPS / Defense / Aviation V0.1
Date: 2026-08-02

## Claim Boundary

This note maps existing proof surfaces to the requested GPS proof names. It does not modify Lean files and does not claim production proof closure.

## L-02 - Trajectory State

Candidate existing proof surface:

`proofs/lean/Obsidia/GeneratedPeripheral/IST_Indice_Stabilite_Trajectoire.lean`

Observed status:

- The file declares `Status : PROVISIONAL scaffold`.
- It defines `TrajectoryStabilityState`.
- It links `trajectory_state`, `temporal_coherence`, `admissible_trajectory`, `stability_score`, `deviation_bound`, `lyapunov_link`, `risk_threshold`, `proof_trace_ready`, and `kernel_boundary`.
- It states that the stability index is non-sovereign and does not decide action.

Mapping:

L-02 can reuse this as a foundation for "trajectory state admissibility", but it is not yet a final L-02 production theorem.

Missing before final L-02:

- explicit past/current/projected state vector relation
- timestamp monotonicity or freshness invariant
- source provenance invariant
- replay exclusion relation
- runtime binding to `GpsDefenseAviationState.domain_state_hash`

## L-06 - Path Fidelity

Candidate existing proof surface:

`proofs/lean/Obsidia/GeneratedPeripheral/P_DomainKernel_PathFidelity_RequiresCoherence.lean`

Observed status:

- The theorem states that if path fidelity is true, coherence must be true.
- This is useful for the GPS MVP because it blocks any path-fidelity claim that ignores source coherence.

Mapping:

L-06 can reuse this as a core invariant: path fidelity requires coherence. It is a partial theorem surface, not a complete production path-fidelity proof.

Missing before final L-06:

- authorized route hash or route identity
- bounded drift against the authorized path
- GNSS/IMU/radio/radar source agreement
- physical envelope relation
- replay consistency
- connection to P4-20 runtime guard output

## Safe Next Step

Create a non-destructive proof work item:

1. Runtime guard proposal P4-20.
2. Python tests that produce evidence fields matching the theorem vocabulary.
3. Lean proof proposal naming the missing invariants.
4. Only after approval, edit protected Lean files and run the proof verifier.
