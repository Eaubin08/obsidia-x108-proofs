# X‑108 STANDARD — Ex‑Ante Governance Interface (Canon Spec)
Version: 1.0
Date: 2026-03-03
Status: Draft (spec + conformance suite blueprint)

This document defines a **portable, domain-agnostic standard** for **ex‑ante governance of irreversible actions** using a **temporal gate** (HOLD→ACT) with **fail‑closed institutional override**.

It is intended to be implementable in:
- finance (payments, trading, custody),
- robotics (actuation, motion, safety envelopes),
- infrastructure (deploys, rollbacks, privileged operations),
- agent systems (tools, API calls, real‑world side effects).

---

## 0) Glossary
- **Intent**: a proposed action with declared irreversibility and constraints.
- **Gate**: a deterministic rule that can output HOLD/ACT (never BLOCK at kernel).
- **Institutional layer**: a fail‑closed layer that can output BLOCK/HOLD/ACT.
- **τ (tau)**: minimum delay threshold for irreversible intents.
- **elapsed**: observed time since intent creation (or since last stable checkpoint).
- **skew**: clock inconsistency (elapsed < 0 or time regressions).
- **Decision**: OS2 kernel output {HOLD, ACT}.
- **Decision3**: institutional output {BLOCK, HOLD, ACT}.

---

## 1) Normative Model

### 1.1 Decision domains
**Kernel decision**
- `Decision := {HOLD, ACT}`

**Institutional decision**
- `Decision3 := {BLOCK, HOLD, ACT}` with strict priority:
  `BLOCK > HOLD > ACT` (fail‑closed).

### 1.2 Intent type (canonical)
An **Intent** MUST include the following fields.

#### Minimal canonical schema (language-agnostic)
```text
Intent:
  intent_id:        string   (unique identifier)
  created_at:       int64    (monotone timestamp, ms or ns; define unit in profile)
  now:              int64    (observation timestamp in same unit)
  elapsed:          int64    (derived = now - created_at)  [can be supplied if computed externally]
  irr:              bool     (irreversible flag)
  tau:              int64    (>= 0; same unit as elapsed)
  payload_hash:     bytes32  (hash of the action payload, canonical encoding)
  scope:            string   (domain namespace, e.g. "finance.payment" / "robotics.actuation")
  params:           map      (domain parameters; MUST be fully covered by payload_hash)
  coherence:        rational (0..1 or profile-defined)  [optional but recommended]
  policy_version:   string   (spec profile / ruleset identifier)
```

#### Notes
- `elapsed` MAY be computed from `(now - created_at)` or provided directly.
- `payload_hash` MUST be computed from a **canonical serialization** of `scope + params`.
- `tau` MUST be non‑negative in all compliant profiles (degenerate `tau < 0` is non‑standard).

---

## 2) Kernel Gate Semantics (OS2)

### 2.1 Canonical rule
The kernel MUST implement the following deterministic gate:

Let `i` be an Intent.

**Rule K1 — Temporal safety (irreversible)**
- If `i.irr = true` AND `i.elapsed < i.tau` THEN `Decision = HOLD`.

**Rule K2 — Skew safety**
- If `i.irr = true` AND `i.elapsed < 0` AND `i.tau >= 0` THEN `Decision = HOLD`.

**Rule K3 — Outside gate**
- If the gate conditions are not met, kernel MAY decide ACT or HOLD based on domain logic,
  but MUST remain deterministic.

> Canonical minimal kernel (pure gate-only) can be:
> - return `HOLD` when gated,
> - else return `ACT` (or defer to a threshold model).

### 2.2 Kernel MUST NOT BLOCK
**Rule K4 — KernelNeverBlocks**
Kernel output domain is strictly `{HOLD, ACT}`.

---

## 3) Institutional Layer Semantics (Consensus / Fail-Closed)

### 3.1 Lift
A compliant implementation MUST define a lift:
- `liftDecision : Decision -> Decision3`
- `liftDecision(HOLD)=HOLD`
- `liftDecision(ACT)=ACT`
- and **never outputs BLOCK**.

### 3.2 Aggregation
If multiple nodes are used, a compliant implementation MUST define:
- an aggregation function over `Decision3` outputs,
- that is **fail‑closed** (if no qualified agreement → BLOCK).

Example profile (N=4, supermajority 3/4):
- if ≥3 ACT → ACT
- else if ≥3 HOLD → HOLD
- else if ≥3 BLOCK → BLOCK
- else → BLOCK

### 3.3 Institutional BLOCK meaning
- BLOCK means: do not execute, and record refusal/incident.
- BLOCK MUST be attributable to institutional layer policy/consensus, never OS2 kernel.

---

## 4) Audit & Attestation (portable)

### 4.1 Audit record (canonical)
Each evaluation MUST append an audit record with:

```text
AuditRecord:
  intent_id
  payload_hash
  now
  elapsed
  irr
  tau
  kernel_decision        (HOLD|ACT)
  institutional_decision (BLOCK|HOLD|ACT)  [if applicable]
  policy_version
  previous_record_hash   bytes32  (hash-chain)
  record_hash            bytes32
  signature              bytes     (optional profile; recommended)
```

### 4.2 Tamper-evidence
A compliant profile MUST provide at least one:
- hash-chain audit log (record i commits record i-1), and/or
- signature per record, and/or
- Merkle anchoring of transcript root.

---

## 5) Conformance Requirements (MUST / SHOULD)

### 5.1 Determinism (MUST)
For fixed `(state, intent)` the kernel MUST output the same decision.

### 5.2 Monotonicity w.r.t time (MUST for irr=true)
If an intent is irreversible and `elapsed` increases monotonically, then:
- for all `elapsed < tau` → decision MUST be HOLD
- for `elapsed >= tau` → decision MAY be ACT or HOLD, but MUST be deterministic given inputs.

### 5.3 Non-anticipation (MUST)
No ACT before tau for irreversible intents.

### 5.4 Skew robustness (MUST for tau>=0)
If elapsed < 0, decision MUST be HOLD (for irr=true).

### 5.5 Institutional fail-closed (MUST if distributed)
If consensus conditions are not met, output MUST be BLOCK.

---

## 6) Conformance Suite Blueprint (Lean + TLA+ + Tests)

### 6.1 Lean (machine-checked invariants)
Minimum required theorems (names indicative):
- `X108_no_act_before_tau`
- `X108_skew_safe` (assume tau >= 0)
- `X108_after_tau_equals_base` (gate inactive implies base decision)
- `KernelNeverBlocks` (Decision domain restriction)
- `lift_refines` (refinement relation: Decision -> Decision3)
- `aggregate_fail_closed` (if no quorum → BLOCK)
- `distributed_no_act_before_tau` (if ≥ quorum HOLD then global ≠ ACT)

### 6.2 TLA+ (temporal property model)
Minimum required properties:
- Safety:
  - `[] (irr /\ elapsed < tau => decision # "ACT")`
- Distributed safety:
  - `[] (irr /\ elapsed < tau => global # "ACT")`
- Optional liveness (profile-defined):
  - `<> (elapsed >= tau => (global="ACT" \/ global="HOLD"))`

TLC model-checking scope:
- bounded N (small) but parametric spec (N=3f+1).

### 6.3 Executable tests (black-box)
A compliant implementation MUST provide a runnable test suite with:
- deterministic replay tests (same seed → same outputs)
- fuzz tests for boundary conditions:
  - elapsed = -1, 0, tau-1, tau, tau+1
  - tau = 0, 1, large
- clock regression tests:
  - elapsed decreases between calls
- distributed adversarial tests:
  - byzantine node proposes ACT before tau; honest nodes HOLD; global must not ACT
- audit tamper tests:
  - edit a record; verification must fail

---

## 7) Profiles (how to specialize without breaking the standard)
The standard supports profiles:
- unit of time (ms/ns),
- quorum definition (3/4, 2/3, 3f+1),
- cryptographic primitives (SHA‑256, ED25519, etc.),
- domain decision logic outside the gate.

A profile MUST NOT weaken:
- non‑anticipation (no ACT before tau for irr=true),
- skew-safe (for tau>=0),
- fail‑closed institutional layer (if distributed).

---

## 8) Minimal Compliance Checklist (PASS/FAIL)
Implementation is compliant iff all are true:

1. Kernel outputs only HOLD/ACT.
2. For irr=true and elapsed<tau, kernel outputs HOLD.
3. For irr=true and elapsed<0 and tau>=0, kernel outputs HOLD.
4. Lift Decision->Decision3 never yields BLOCK.
5. Distributed layer is fail‑closed when quorum absent.
6. Audit is tamper-evident (hash-chain and/or signatures and/or anchoring).
7. Conformance suite runs and passes (Lean proofs + TLA model + executable tests).

---

## 9) Reference Mapping to Obsidia-lab-trad (informative)
This standard aligns with the current Obsidia structure:
- kernel: Decision {HOLD, ACT}
- institutional: Decision3 {BLOCK, HOLD, ACT} + aggregate4 fail-closed
- Temporal gate: X‑108 (HOLD before tau, skew-safe)
- refinement: lift_refines / x108_is_lift / x108_never_blocks
