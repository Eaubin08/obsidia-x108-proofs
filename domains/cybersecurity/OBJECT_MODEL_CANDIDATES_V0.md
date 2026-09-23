# Cybersecurity Object Model Candidates V0

Status: CANDIDATE_AUDIT_ONLY
Domain: cybersecurity
Object map impact: NONE
Runtime impact: NONE
Authority impact: NONE

## 1. Purpose

This document audits candidate Cybersecurity objects without promoting them into `object_map.yaml`.

The controlling rule is:

```text
security concept
!=
Cybersecurity-owned domain object
```

The source corpus contains real security architecture, sandbox policy, incident-response structure, evidence boundaries and network audits.

Many of those elements are transversal Obsidia controls rather than Cybersecurity business objects.

## 2. Classification

### SOURCE_DEFINED

The source explicitly names or structures the candidate.

This does not automatically make it domain-owned.

### DERIVED_CANDIDATE

The candidate is a reasonable abstraction from multiple audited sources, but is not yet canonically defined.

### TRANSVERSE_DO_NOT_MAP

The element is real, but belongs to universal security, governance, proof, sandbox, ticketing or execution-control infrastructure.

### HOLD_UNDERDEFINED

The concept may belong to Cybersecurity, but schema, identity, lifecycle or ownership are not frozen.

### REJECT_NOT_DOMAIN_OBJECT

The item is a score, flag, label, state value, audit category or policy field rather than a stable domain object.

## 3. Audited sources

- `docs/investor/SECURITY_BY_THREAT_OBSOLESCENCE_OBSIDIA_X108.md`
- `periphery/specs/Spec_03__Sandbox_Policy_isolation_et_gouvernance_P21_P30.md`
- `periphery/specs/Spec_18__Incident_Response_Protocol_P150_P154_valider_V4.md`
- `runtime_contracts/boundaries/RSSI_EVIDENCE_ONLY.md`
- `docs/core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.md`
- `planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md`

## 4. Candidate: SecurityEvent

Classification: `DERIVED_CANDIDATE`

Decision: HOLD.

Source basis:

- Sandbox Policy defines `VIOLATION_EVENT`;
- Incident Response defines incident triggers;
- security architecture discusses attacks/nuisances/events.

Why not promoted:

- no stable `SecurityEvent` schema exists;
- no canonical identity/lifecycle exists;
- event ownership may be transversal;
- relation to `DomainSignal` is not frozen.

A future schema would need at least provenance, timestamp, event type, evidence refs and uncertainty, but those fields are not frozen here.

## 5. Candidate: ViolationEvent

Classification: `SOURCE_DEFINED`

Decision: HOLD.

Source:

- Sandbox Policy explicitly states that each violation generates a `VIOLATION_EVENT`.

Why not promoted:

- it is currently defined as part of sandbox/governance infrastructure;
- sandbox is transversal;
- no evidence shows `VIOLATION_EVENT` is Cybersecurity-owned rather than a universal control event.

Therefore:

```text
SOURCE_DEFINED
but
TRANSVERSE_OWNERSHIP_UNRESOLVED
```

## 6. Candidate: Incident

Classification: `SOURCE_DEFINED`

Decision: HOLD.

Incident Response explicitly defines an incident lifecycle:

```text
OPEN
→ CONTAINED
→ ANALYZED
→ RESOLVED
→ ARCHIVED
```

This is the strongest Cybersecurity object candidate currently available.

However promotion is premature because:

- the source is `FORMALISÉ_À_VALIDER`;
- incident fields are not frozen as a canonical UDIP schema;
- identity, causal links and relation to receipts are not specified in object-map form;
- automatic vs human actions still need a contract boundary.

## 7. Incident state values are not objects

The following are lifecycle values:

- `OPEN`
- `CONTAINED`
- `ANALYZED`
- `RESOLVED`
- `ARCHIVED`

Classification:

```text
REJECT_NOT_DOMAIN_OBJECT
```

They may become enum values inside an `Incident` object.

They should not become separate DomainObjectMap entries.

## 8. Candidate: ThreatEvidence

Classification: `DERIVED_CANDIDATE`

Decision: HOLD.

Source basis:

- RSSI evidence boundary;
- security architecture evidence refs;
- threat models;
- audit evidence.

Why not promoted:

The source defines evidence surfaces such as:

- `OS3EvidenceTicket`;
- `BoundaryContract`;
- `ContextPacket`.

Those are transversal proof/governance objects.

A Cybersecurity-specific `ThreatEvidence` object could be useful, but it is not yet source-defined as a distinct canonical object.

## 9. Evidence containers that MUST NOT be mapped as Cybersecurity-owned

### OS3EvidenceTicket

Classification: `TRANSVERSE_DO_NOT_MAP`

Reason: proof/evidence surface used beyond Cybersecurity.

### BoundaryContract

Classification: `TRANSVERSE_DO_NOT_MAP`

Reason: governance boundary contract, not Cybersecurity semantics.

### ContextPacket

Classification: `TRANSVERSE_DO_NOT_MAP`

Reason: context transport surface.

### DecisionTicket / receipt surfaces

Classification: `TRANSVERSE_DO_NOT_MAP`

Reason: authority/proof surfaces remain outside domain ownership.

## 10. Candidate: RiskFinding

Classification: `DERIVED_CANDIDATE`

Decision: HOLD.

Source basis:

- risk assessment;
- risk flags;
- network connector risk;
- threat model findings.

Why not promoted:

No source defines a stable `RiskFinding` object.

Risk may be represented as fields, flags or evidence within another object.

## 11. Threat-model and risk labels are not objects

Examples:

- attack/nuisance labels;
- risk scores;
- connector risk categories;
- network egress categories;
- threat model labels.

Classification:

```text
REJECT_NOT_DOMAIN_OBJECT
```

They are values or evidence metadata.

## 12. Candidate: ContainmentCandidate

Classification: `DERIVED_CANDIDATE`

Decision: HOLD.

Source basis:

- Incident Response state `CONTAINED`;
- isolation boundaries;
- response candidate semantics.

Why not promoted:

No source defines `ContainmentCandidate` as a stable object.

Containment may instead be:

- a proposal;
- an action candidate;
- an incident transition;
- a capability reference.

The object boundary must be resolved before mapping.

## 13. Candidate: SecurityBoundary

Classification: `HOLD_UNDERDEFINED`

Decision: HOLD.

Source basis:

- SandboxPolicy;
- BoundaryContract;
- isolation boundaries;
- network egress boundaries.

Problem:

`SecurityBoundary` is too broad and risks duplicating universal boundary infrastructure.

It must not be promoted unless a clearly Cybersecurity-specific boundary entity is demonstrated.

## 14. SandboxPolicy is not Cybersecurity-owned

Source-defined object:

`SandboxPolicy`

Classification:

```text
TRANSVERSE_DO_NOT_MAP
```

Reason:

Sandbox Policy is a generic execution-control mechanism.

Cybersecurity can inspect or reference it.

Cybersecurity must not claim ownership of the universal sandbox contract.

## 15. Sandbox policy fields are not objects

Examples:

- `no_write`;
- `allowed_tools`;
- `forbidden_tools`;
- `max_cost`;
- `max_duration_sec`;
- `max_calls`;
- `external_network`;
- `trace_level`.

Classification:

```text
REJECT_NOT_DOMAIN_OBJECT
```

They are configuration fields.

## 16. Network egress classifications are not objects

P70 categories such as:

- `NETWORK_EGRESS_NONE`;
- `NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW`;
- `NETWORK_EGRESS_TRADING_REVIEW`;
- `CONNECTOR_ACTIVE_REVIEW`;
- `CONNECTOR_DRY_RUN_SAFE`;

are:

```text
REJECT_NOT_DOMAIN_OBJECT
```

They are audit classifications.

Cybersecurity may consume them as evidence/risk attributes.

## 17. Security by Threat Obsolescence concepts

The architecture note contains concepts such as:

- Reality Authenticity Gate;
- DomainState;
- nuisance registry;
- decision receipt;
- replay.

Classification:

```text
TRANSVERSE_DO_NOT_MAP
```

for Cybersecurity object ownership.

These are cross-domain architecture mechanisms, even if they contribute to security.

## 18. Current candidate verdict

### Ready to map now

```text
NONE
```

### Source-defined but HOLD

- `ViolationEvent`
- `Incident`

### Derived candidates but HOLD

- `SecurityEvent`
- `ThreatEvidence`
- `RiskFinding`
- `ContainmentCandidate`

### Underdefined

- `SecurityBoundary`

### Transverse / do not map

- `SandboxPolicy`
- `OS3EvidenceTicket`
- `BoundaryContract`
- `ContextPacket`
- DecisionTicket / receipt / replay surfaces
- Reality Authenticity Gate
- DomainState
- universal nuisance/admission machinery

### Reject as object

- incident state values;
- risk scores;
- threat labels;
- connector/network audit categories;
- sandbox policy fields;
- gate hints.

## 19. Promotion gate

A Cybersecurity candidate may enter `object_map.yaml` only after:

1. source ownership is clearly Cybersecurity rather than transverse;
2. canonical name is fixed;
3. minimum field schema is explicit;
4. identity and lifecycle are defined where relevant;
5. relation to evidence is explicit;
6. relation to `DomainSignal` is explicit;
7. response/action semantics remain separate;
8. no object embeds authority;
9. incident/containment changes cannot bypass KX108/Binder;
10. tests can verify non-sovereignty.

## 20. Final verdict

The correct Cybersecurity V0 object map remains:

```yaml
status: NOT_YET_DEFINED
objects: []
```

The current source corpus supports a strong security perimeter and several candidates, but not a frozen Cybersecurity DomainObjectMap.
