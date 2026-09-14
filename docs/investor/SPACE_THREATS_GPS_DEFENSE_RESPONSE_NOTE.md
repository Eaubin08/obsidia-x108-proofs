# Obsidia X-108 - GPS / Defense Response to Space Threats

## Purpose

This note translates current public space-threat themes - GNSS jamming,
spoofing, laser dazzling, satellite proximity risks and debris escalation - into
the Obsidia X-108 GPS / aviation / defense security model.

The central idea is simple:

```text
Obsidia does not trust the GPS signal.
Obsidia qualifies the signal through provenance, physics and multi-source proof
before any physical action can be authorized.
```

## 1. Spoofing Is Neutralized by Reality Authenticity

GPS spoofing tries to make a false position appear true. In Obsidia, GPS is not
treated as truth. It is only a candidate observation.

Before a coordinate can reach the X-108 decision boundary, it must pass the
Reality Authenticity and Provenance Gate:

- freshness: the signal must be current, not an old state replayed into the system;
- sensor identity: the GNSS, IMU or radio/radar source must be attested;
- anti-replay: stale telemetry cannot authorize a new trajectory;
- causal coherence: the signal must fit the wider physical context.

If the signal cannot prove its legitimacy, it is not canonized into an executable
state. The gate returns `HOLD` fail-closed before the connector or AI can turn it
into action.

## 2. Jamming Is Treated as Multi-Source Contradiction

Jamming makes a system partially blind. Obsidia does not answer blindness with
guessing. It compares independent sources:

- GNSS position;
- inertial drift from IMU;
- radio or radar confidence;
- velocity and g-load plausibility;
- route fidelity against the authorized path.

If GPS appears stable while inertial or radar evidence disagrees, the GPS signal
is classified as a contradiction, not as a truth to be repaired by an LLM.

The current P3 GPS gate expresses this as domain nuisances such as:

- `GPS_SPOOFING`;
- `MULTI_SOURCE_CONTRADICTION`;
- `JAMMING_DETECTED`;
- `PATH_FIDELITY_BREACH`.

## 3. The Deterministic Lock Is Fail-Closed

In aviation and defense, ambiguity cannot default to action. Obsidia applies the
priority:

```text
BLOCK > HOLD > ALLOW
```

If a signal is too noisy, stale, unauthenticated or physically inconsistent, the
system does not ask a probabilistic model to improvise. It suspends admission.

This is the role of the GPS P3-05 bridge:

```text
connectors/aviation_robo.py
-> domains/gps/gps_x108_gate.py
-> GpsDefenseAviationState
-> X-108 IR
-> kernel authority
```

The bridge follows `DOMAIN_BRIDGE_ONLY`: it observes and translates, but does
not decide.

## 4. Space-Threat Scenarios for the Cockpit

The MVP cockpit can show four defensive scenarios inspired by public
counter-space threat patterns:

### GNSS Jam

```text
signal_noise_ratio drops
brownout_score rises
radio / radar confidence degrades
-> HOLD
```

### Laser Dazzle

```text
optical confirmation unavailable
sensor confidence drops
attribution uncertain
-> HOLD
```

### Close Approach

```text
unknown orbital object approaches asset
proximity risk rises
intent attribution incomplete
-> HOLD or BLOCK
```

### Debris Cascade Risk

```text
proposed response = kinetic interception
debris cascade risk high
-> BLOCK
```

The point is not to build or describe a weapon. The point is to show that
Obsidia prevents uncertain spatial reality from becoming irreversible action.

## 5. Formal Proof Direction

For production, the GPS / aviation / defense vertical should eventually close
formal proof around:

- trajectory state validity;
- path fidelity;
- fail-closed priority;
- signed decision receipts;
- no direct connector authority.

The planned Lean 4 proof direction is:

- L-02: trajectory state validity;
- L-06: path fidelity.

Until those are formally closed and verified, they should be presented as the
proof roadmap, not as completed certification.

## 6. Positioning Against Probabilistic World Models

Many AI approaches try to learn physical reality from data and inference.
Obsidia takes a different route:

```text
Structure before inference.
Physical state before narration.
Kernel authority before action.
```

The AI can propose a maneuver or explain a situation, but it cannot authorize
the action. The action must pass through the deterministic state boundary.

## 7. One-Line Message

Obsidia does not believe the GPS signal. It forces the signal to prove itself
through freshness, attestation, multi-source coherence and physical plausibility
before any real-world action can proceed.

## Boundary

This note is for investor, industrial and hackathon positioning. It is not a
claim of certified avionics readiness, live defense deployment, or completed
formal proof closure.
