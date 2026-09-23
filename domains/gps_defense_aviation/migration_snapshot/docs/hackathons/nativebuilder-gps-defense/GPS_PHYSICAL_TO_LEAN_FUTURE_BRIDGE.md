# GPS Physical To Lean Future Bridge

Status: FUTURE_BRIDGE_NOTE_ONLY
Lean: NOT_MODIFIED

## Purpose

This note identifies future objects that must be connected to L-02 and L-06 after the Physical Signal Periphery produces real, hashed observation envelopes.

## Future L-02 Objects

- `PhysicalObservationEnvelopeHash`
- `ObservableSetHash`
- `GpsDomainStateHash`
- `TrajectoryStateFromObservation`
- `FreshnessAndMonotonicTime`
- `ReplayExclusion`
- `TrustedSourceBoundary`

## Future L-06 Objects

- `PathFidelityEvidenceHash`
- `AuthorizedRouteHash`
- `DriftBound`
- `SourceCoherence`
- `PhysicalEnvelope`
- `ReplayConsistency`
- `P4_20EvidenceToPathFidelity`

## Required Link

```text
physical_observation_hash
-> observables_hash
-> domain_state_hash
-> P4-20 evidence_hash
-> P3-05 receipt
-> X-108 decision
```

This lot does not prove those relations in Lean. It prepares the runtime and audit vocabulary needed for a later protected proof plan.

