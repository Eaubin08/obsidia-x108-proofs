# GPS / Defense / Aviation Conformance Notes

Status: SCAFFOLD ONLY / DOMAIN PROFILE DOCUMENTED

Runtime conformance: PARTIALLY EVIDENCED, NOT UDIP-PROMOTED
UDIP runtime promotion: NONE
Decision authority: KX108_ONLY

## 1. Source basis

This profile is grounded in:

- `domain_packets/gps_defense_aviation_decisional_form_v0.yaml`
- `domains/gps/gps_x108_gate.py`
- `sigma/domains/gps_defense_aviation_agents.py`
- `tests/integration/test_sigma_bridge_gps.py`
- `tests/test_gps_x108_reality_authenticity_gate.py`
- `tests/test_gps_p3_09_contract_and_receipts.py`

GPS has materially stronger branch-local evidence than the other reference packs.

That does not promote the UDIP Domain Pack out of `SCAFFOLD_ONLY`.

## 2. Bridge authority contract

The real gate declares:

```text
DOMAIN_BRIDGE_ONLY
decision_authority = KX108_ONLY
connector_decides = false
```

The bridge:

- observes;
- normalizes;
- translates;
- evaluates Reality Authenticity;
- may fail closed locally with HOLD;
- never returns autonomous ALLOW.

```text
BRIDGE != AUTHORITY
CONNECTOR != DECIDER
LOCAL FAIL-CLOSED HOLD != POSITIVE AUTHORIZATION
```

## 3. Reality Authenticity boundary

The current gate evaluates:

- freshness;
- sensor attestation;
- anti-replay;
- multisource coherence;
- physical envelope.

It distinguishes:

```text
SourceProvenance
!=
RealityAuthenticity
```

and fails closed before kernel execution when the physical input is not sufficiently canonized.

Current fail-closed reasons include:

- `ORACLE_FRESHNESS_FAILED`;
- `CIC_ATTESTATION_FAILED`;
- `ANTI_REPLAY_FAILED`;
- `MULTI_SOURCE_COHERENCE_FAILED`;
- `PHYSICAL_ENVELOPE_FAILED`.

## 4. Multisource / physical envelope

The current contract requires multiple source families:

- GNSS;
- IMU;
- RADIO_OR_RADAR.

The real implementation also checks:

- source conflict;
- trajectory drift;
- velocity;
- g-load.

These thresholds are implementation/reference evidence.

They must not be universalized into UDIP Core.

## 5. Local HOLD semantics

GPS is explicitly allowed to return local `HOLD` before kernel evaluation when reality authenticity fails.

This is a safety admission result.

It MUST NOT evolve into autonomous positive authority.

```text
REALITY FAILURE
→ HOLD

REALITY PASS
→ eligible for KX108 evaluation
not
→ automatic ALLOW
```

## 6. Receipt / proof boundary

The current GPS gate builds a decision receipt and embeds an OS3 ticket.

Existing tests verify:

- `contract == DOMAIN_BRIDGE_ONLY`;
- `decision_authority == KX108_ONLY`;
- `connector_decides == false`;
- hashes are present;
- Merkle root is present;
- ticket is structurally valid;
- `replay_status == NOT_RUN`.

The current receipt explicitly identifies:

```text
LOCAL_SHA256_DEMO_NOT_PRODUCTION_SIGNING
```

Therefore:

```text
HASHED RECEIPT != PRODUCTION SIGNATURE
OS3 TICKET != REPLAY EXECUTED
REPLAY_STATUS NOT_RUN != REPLAY PROOF
```

## 7. Existing tests on this branch

### Reality Authenticity tests

`tests/test_gps_x108_reality_authenticity_gate.py` substantively verifies:

- coherent nominal state;
- spoofed input fails closed before kernel;
- replay/freshness/attestation failures are classified;
- receipt carries an OS3 ticket;
- replay is not falsely claimed as run;
- kernel payload contains the expected physical-state fields.

### P3-09 contract/receipt tests

`tests/test_gps_p3_09_contract_and_receipts.py` verifies:

- DOMAIN_BRIDGE_ONLY;
- KX108_ONLY;
- connector_decides false;
- fail-closed HOLD;
- receipt type;
- receipt completeness across nominal/spoof/replay scenarios.

### Sigma bridge test

`tests/integration/test_sigma_bridge_gps.py` provides basic bridge reachability evidence.

## 8. Required GPS invariants

```text
DOMAIN != AUTHORITY
SOURCE != TRUST
PROVENANCE != REALITY AUTHENTICITY
REALITY AUTHENTICITY PASS != ALLOW
BRIDGE != DECIDER
CONNECTOR != AUTHORITY
SENSOR ATTESTATION != DECISION
PHYSICAL COHERENCE != EXECUTION PERMISSION
LOCAL HOLD != POSITIVE AUTHORIZATION
RECEIPT != DECISION
HASH != PRODUCTION SIGNATURE
REPLAY STATUS != REPLAY EXECUTION
SIMULATION != REALITY
KX108_ONLY
```

## 9. Remaining conformance gaps

Despite strong local evidence, the UDIP pack still lacks:

- promoted DomainObjectMap;
- explicit UDIP-native object mapping;
- full Binder execution boundary proof;
- production signing;
- replay execution verifier integrated as claimed proof;
- complete physical-source independence model;
- promoted runtime state.

## 10. Candidate future tests

- `test_gps_reality_pass_still_requires_kx108`
- `test_gps_act_requires_binder`
- `test_gps_connector_never_executes_directly`
- `test_gps_receipt_not_decision_authority`
- `test_gps_replay_not_execution`
- `test_gps_production_signature_claim_blocked_without_signature`
- `test_gps_no_kernel_mutation`

## 11. Promotion condition

GPS / Defense / Aviation remains `SCAFFOLD_ONLY` until the existing physical/receipt evidence is connected to the UDIP-native object/domain-signal model and the Binder/execution boundary is proven end-to-end.

Strong legacy/runtime evidence is reference evidence, not automatic UDIP promotion.
