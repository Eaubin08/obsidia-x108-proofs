# GPS Reality Authenticity Gate - Activation Note

## Core Priority

The activation of the Reality Authenticity Gate for the GPS / defense /
aviation domain is the first technical priority before any real execution path.
Its role is to protect X-108 from false reality inputs such as spoofed
coordinates, replayed telemetry, unauthenticated sensors or incoherent physical
signals.

The purpose is not to let an AI repair the world by probabilistic intuition. The
purpose is to prevent a non-canonical signal from ever becoming executable.

## Physical Truth Chain

The GPS domain must close a physical truth chain before telemetry can be
submitted to the X-108 kernel.

### 1. Oracle Freshness

The incoming position signal must be fresh. A packet must prove that it was
produced within the accepted time window and is not an older state injected back
into the system.

Failure mode:

```text
stale telemetry / replay window
-> REPLAY_ATTACK
-> HOLD fail-closed
```

### 2. Sensor Attestation

The GNSS, IMU or radio/radar source must be attested. If the source identity is
missing, falsified or outside the accepted Causal Identity Context, the signal is
not canonized.

Failure mode:

```text
attestation_ready=false
-> CIC_ATTESTATION_FAILURE
-> HOLD fail-closed
```

### 3. Multi-Source Coherence

The system must compare GNSS position, inertial drift and radio/radar confidence
to verify that independent sources tell the same spatial story.

Failure mode:

```text
GPS drift + IMU/radio contradiction
-> MULTI_SOURCE_CONTRADICTION
-> HOLD fail-closed
```

## Runtime Bridge

The connector `connectors/aviation_robo.py` is now wired with a local P3-05 path
through:

```text
domains/gps/gps_x108_gate.py
```

The gate is the mandatory domain bridge for GPS telemetry before kernel
submission. It follows the `DOMAIN_BRIDGE_ONLY` contract:

- it observes;
- it normalizes;
- it translates;
- it does not decide;
- it does not authorize execution;
- it fails closed with `HOLD` when authenticity is not proven.

## Current Real Implementation

The current implementation builds a `GpsDefenseAviationState` containing:

- flight id;
- flow type;
- nuisance labels;
- authenticity checks;
- risk, confidence and audit scores;
- fail-closed state;
- domain state hash.

The nuisance registry classifies GPS-specific threats such as:

- `GPS_SPOOFING`;
- `MULTI_SOURCE_CONTRADICTION`;
- `REPLAY_ATTACK`;
- `CIC_ATTESTATION_FAILURE`;
- `PATH_FIDELITY_BREACH`.

## Operational Meaning

If telemetry is divergent, stale or not attested, the Reality Authenticity Gate
returns an admissible `HOLD` state before the input can become action. This
prevents probabilistic intelligence from overriding physical uncertainty.

In short:

```text
No fresh signal
or no attested sensor
or no multi-source coherence
-> no executable reality
```

## Boundary

This note documents the P3 domain activation path. Production deployment still
requires the sealed kernel path, production signed receipts, formal proof
closure, sensor attestation infrastructure and domain safety review.
