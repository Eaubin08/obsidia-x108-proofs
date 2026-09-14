# Obsidia X-108 - Security by Threat Obsolescence

## Purpose

This note frames Obsidia X-108 as an industrial governance architecture where
critical threats become structurally obsolete instead of merely detected or
filtered after the fact.

The core claim is not that every external attack disappears. The claim is that a
non-canonical input cannot acquire execution authority inside X-108. The burden
of proof is inverted: an input must prove freshness, provenance, identity,
coherence and domain legitimacy before it can be translated into a kernel-facing
state.

## Strategic Thesis

Classic cybersecurity reacts to suspicious patterns. An attacker changes a
signature, an IP, a prompt, a payload shape or a timing pattern, and the defense
must adapt.

Obsidia changes the battlefield. It does not try to guess whether an input is
malicious. It asks whether the input can be canonized into a stable domain state
and submitted to the deterministic authority boundary.

If it cannot, the input does not become action.

```text
Raw input
-> Reality Authenticity Gate
-> DomainState
-> X-108 admission
-> ALLOW / HOLD / BLOCK
-> Decision Receipt
```

This is security by threat obsolescence: the attacker may still produce noise,
but the noise cannot rewrite the stable structure.

## Paradigm Shift

| Classical AI security | Obsidia X-108 security |
| --- | --- |
| Filters prompts and outputs | Authenticates inputs before authority |
| LLM may interpret and decide | LLM narrates only, never decides |
| Attack detection is reactive | Admission is deterministic and fail-closed |
| Memory can be poisoned | Canonical memory is protected by read/write boundaries |
| API can become an authority shortcut | API remains a routing surface |
| Logs explain after the fact | Receipts bind decision, evidence and replay |

## Sovereignty Invariants

The industrial security story rests on several invariants:

- `KX108_ONLY`: the kernel is the exclusive decision authority.
- `api_allowed_to_decide=False`: APIs and connectors route data, but do not decide.
- `does_not_authorize_action=true`: domain votes or business verdicts do not authorize execution.
- `memory_write=false`: agents cannot poison canonical memory through ordinary interaction.
- `DOMAIN_BRIDGE_ONLY`: domain gates translate and submit; they do not grant action authority.
- `BLOCK > HOLD > ALLOW`: safety vetoes dominate incomplete or permissive states.
- `TEST_PASS != AUTHORIZED`: passing a technical test is not an action authorization.

## Security Mechanism

### 1. Reality Authenticity Gate

Before data reaches a decision boundary, the system checks whether it is anchored
in reality:

- Oracle freshness: stale data and replay windows fail closed.
- Sensor or source attestation: the producer identity must be accepted.
- Multi-source coherence: independent sources must tell the same operational story.
- Physical plausibility: critical-world claims must remain inside a plausible physics envelope.
- Anti-replay: old valid-looking states cannot authorize a new action.

In the GPS / defense / aviation slice, this is now represented in
`domains/gps/gps_x108_gate.py` through `GpsDefenseAviationState` and a
fail-closed admission path.

### 2. DomainState Instead of Text

Critical decisions are not taken over natural language. The input is compiled
into a domain state, then mapped into X-108 IR.

For GPS / defense / aviation, the domain state carries:

- flight identity;
- flow type;
- nuisance labels;
- authenticity verdicts;
- risk, confidence and audit scores;
- fail-closed status;
- domain state hash.

An attacker can manipulate text. They cannot obtain execution authority unless
the domain state satisfies the boundary conditions.

### 3. Nuisance Registry

Threats are expressed as domain nuisances, not as vague security impressions.
For the GPS / aviation vertical, the registry includes:

- `GPS_SPOOFING`;
- `MULTI_SOURCE_CONTRADICTION`;
- `REPLAY_ATTACK`;
- `CIC_ATTESTATION_FAILURE`;
- `PATH_FIDELITY_BREACH`;
- `JAMMING_DETECTED`;
- `COLLISION_RISK`;
- `RESTRICTED_ZONE_APPROACH`.

This makes the attack legible to the kernel-facing layer without allowing the
domain connector to decide.

### 4. Receipts and Replay

Every governed decision should produce a decision receipt. The current P3 GPS
implementation emits a local SHA-256 demo receipt. Production P4 requires the
real signed receipt path.

The receipt binds:

- the gate;
- the contract;
- the decision authority;
- the verdict;
- the source;
- the domain state hash;
- the IR payload;
- any kernel response.

This supports deterministic replay: the system can inspect whether a future
claim is coherent with the state and evidence that existed at decision time.

## Industrial Example: AF994

Scenario: an aviation connector proposes a trajectory continuation for flight
`AF994`.

### Nominal Telemetry

Fresh data, attested sensor identity, coherent GNSS / inertial / radio signals,
and plausible velocity / g-load produce a coherent `GpsDefenseAviationState`.

The gate may submit the IR to X-108. It still does not authorize the action by
itself.

### GPS Spoofing

If GPS drift and source conflict rise, the gate classifies:

```text
GPS_SPOOFING
MULTI_SOURCE_CONTRADICTION
```

The gate returns `HOLD` fail-closed before execution authority can be reached.

### Replay Attack

If telemetry is stale, unauthenticated or replayed, the gate classifies:

```text
REPLAY_ATTACK
CIC_ATTESTATION_FAILURE
PATH_FIDELITY_BREACH
```

The input is not canonized. It becomes operational noise, not an executable
future.

## Why This Makes the Threat Obsolete

The attack does not need to be "understood" by an LLM. It must satisfy the
domain invariants. If it cannot, it cannot become action.

This is the inversion:

```text
Old model:
  system must prove the input is malicious

Obsidia model:
  input must prove it is legitimate
```

The attacker can continue mutating the surface pattern. The stable state remains
protected because the execution path is gated by structure, not by wording.

## Investor Message

The short version:

> The market is building faster AI agents. Obsidia provides the deterministic
> authority layer that decides when those agents are allowed to touch the real
> world.

For critical industries, this is not a chatbot feature. It is the missing
control layer between probabilistic intelligence and irreversible action.

## Claim Boundary

The current repository contains real P3 domain-gate work for GPS / defense /
aviation, including local fail-closed admission and test coverage.

Production-grade industrial claims still require:

- finalized P4 signed decision receipts;
- formal proof closure for trajectory state and path fidelity;
- integration with the sealed kernel runtime;
- verified Merkle / seal / replay pipeline;
- real sensor attestation infrastructure;
- external safety and domain review before any live physical deployment.

Until those are complete, this document is an industrial argumentaire and build
direction, not a certification statement.
