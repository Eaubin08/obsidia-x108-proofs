# Telecom Object Model Candidates V0

Status: CANDIDATE_AUDIT_ONLY
Domain: telecom
Object map impact: NONE
Runtime impact: NONE
Authority impact: NONE

## 1. Purpose

This document records candidate Telecom objects without promoting them into `object_map.yaml`.

The audit follows a strict rule:

```text
object mentioned
!=
domain object proven
```

Telecom currently has enough source material to define a perimeter, but not enough to freeze a canonical DomainObjectMap.

## 2. Classification

Each candidate uses one of these labels.

### SOURCE_DEFINED

The name or structure is explicitly present in an audited source.

This does not automatically mean it belongs in the Telecom object map.

### DERIVED_CANDIDATE

The candidate is a reasonable abstraction from multiple sources, but no source defines it as a stable domain object yet.

### TRANSVERSE_DO_NOT_MAP

The object/component is real, but it belongs to a cross-domain or universal mechanism rather than Telecom semantics.

### HOLD_UNDERDEFINED

The candidate may become Telecom-specific, but its fields, lifecycle or boundary are not defined well enough.

### REJECT_NOT_DOMAIN_OBJECT

The item is a metric, score, category, risk flag or implementation detail rather than a domain object.

## 3. Audited sources

Repository sources:

- `docs/core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.md`
- `specs/external_signals/component_specs/C471_gateway_before_endpoint_prefilter.yaml`
- `planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md`

Internal concept sources recorded in `sources.yaml`:

- `internal://Physical Signal World Model`
- `internal://suite pepite implementé 02.7`
- `internal://OBSIDIA_V5_Texte_Continu_Edition_Livre_2026-08-18`

## 4. Network / Connectivity candidates

| Candidate | Classification | Source basis | Decision |
|---|---|---|---|
| `ConnectorIdentity` | DERIVED_CANDIDATE | P70 connector classification + Telecom README | HOLD |
| `NetworkObservation` | DERIVED_CANDIDATE | P70 network surfaces + Telecom perimeter | HOLD |
| `EgressCapability` | DERIVED_CANDIDATE | P70 egress categories | HOLD |
| `GatewayConstraint` | DERIVED_CANDIDATE | C471 gateway prefilter pattern | HOLD |
| `Topology` | HOLD_UNDERDEFINED | README candidate only | HOLD |
| `NetworkSegment` | HOLD_UNDERDEFINED | README candidate only | HOLD |
| `LinkState` | HOLD_UNDERDEFINED | README candidate only | HOLD |
| `ServiceState` | HOLD_UNDERDEFINED | README candidate only | HOLD |
| `AvailabilityState` | HOLD_UNDERDEFINED | inferred from availability/freshness perimeter | HOLD |

None of these are ready for `object_map.yaml`.

Why:

- no stable field schema;
- no lifecycle;
- no canonical identity rule;
- no demonstrated mapping to `DomainSignal`;
- P70 primarily classifies runtime egress risk, not Telecom business objects.

## 5. C471 components that MUST NOT become Telecom objects

C471 explicitly defines:

- `agent_tool_gateway`;
- `api_critical_gateway`;
- `world_action_gateway`;
- `temporal_prefilter`;
- `tool_call_intent`;
- `api_call_intent`;
- `world_action_candidate`;
- `prefiltered_action_candidate`;
- `gateway_rejection_signal`.

Classification:

```text
TRANSVERSE_DO_NOT_MAP
```

Reason:

C471 is an external-signal / temporal-gateway architecture pattern.

It is useful to Telecom, but it is not Telecom semantics.

Promoting these objects into the Telecom object map would incorrectly make a transverse control mechanism look domain-owned.

## 6. P70 classifications that MUST NOT become Telecom objects

Examples:

- `NETWORK_EGRESS_NONE`;
- `NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW`;
- `NETWORK_EGRESS_TRADING_REVIEW`;
- `NETWORK_EGRESS_BLOCKED`;
- `CONNECTOR_ACTIVE_REVIEW`;
- `CONNECTOR_DRY_RUN_SAFE`.

Classification:

```text
REJECT_NOT_DOMAIN_OBJECT
```

Reason:

These are audit categories / verdict labels, not persistent Telecom entities.

They may later become values on a Telecom observation or risk field.

They should not become objects themselves.

## 7. Physical Signal source-defined candidates

The internal Physical Signal sources explicitly name:

- `PhysicalSignalReport`;
- `PhysicalSignalEvent`;
- `WorldStateCandidate`;
- `PhysicalCoherenceScore`;
- `SignalContradictionScore`;
- `ReplayablePhysicalProofCandidate`;
- `PhysicalRiskHint`.

### `PhysicalSignalReport`

Classification: `SOURCE_DEFINED`

Decision: HOLD.

Reason:

The source defines the name and purpose, but no canonical schema is frozen and the concept may belong to a broader Physical Signal periphery shared by Telecom, GPS and other physical domains.

### `PhysicalSignalEvent`

Classification: `SOURCE_DEFINED`

Decision: HOLD.

Reason:

Likely event-level observation, but fields, identity, lifecycle and relationship to `DomainSignal` are not frozen.

### `WorldStateCandidate`

Classification: `SOURCE_DEFINED`

Decision: HOLD.

Reason:

This is explicitly a **candidate**, not a fact.

It also appears broader than Telecom.

Promoting it directly as Telecom-owned would risk absorbing a cross-domain world-model concept.

### `PhysicalCoherenceScore`

Classification: `REJECT_NOT_DOMAIN_OBJECT`

Reason:

It is a score/metric.

It may become a field or evidence feature on another object.

### `SignalContradictionScore`

Classification: `REJECT_NOT_DOMAIN_OBJECT`

Reason:

It is a score/metric, not a standalone business object.

### `ReplayablePhysicalProofCandidate`

Classification: `TRANSVERSE_DO_NOT_MAP`

Reason:

Proof/evidence belongs to the UDIP proof surface and should be referenced rather than owned as Telecom semantics.

### `PhysicalRiskHint`

Classification: `REJECT_NOT_DOMAIN_OBJECT`

Reason:

Risk hint is signal metadata, not a stable domain entity.

## 8. Instruments are not domain objects by default

The source vision names:

- Wi-Fi;
- RF;
- telecom;
- satellite;
- GNSS/GPS;
- radar;
- UWB;
- SDR;
- Bluetooth.

These are currently **source/instrument classes**, not proven Telecom DomainObjectMap entities.

Classification:

```text
HOLD_UNDERDEFINED
```

A future object model may need something like a `SignalSourceRef`, but that name and schema are not source-defined today.

## 9. Shared-source rule

A physical source may be interpreted by several domains.

Example:

```text
same RF observation
├── Telecom interpretation: propagation / connectivity / interference
└── GPS interpretation: navigation integrity / spoofing / positioning
```

Therefore a source object must not silently become a domain object simply because Telecom consumes it.

The future map must preserve:

- source provenance;
- source identity when available;
- timestamp/freshness;
- evidence reference;
- domain interpretation boundary.

## 10. Current candidate verdict

### Ready to map now

```text
NONE
```

### Source-defined but HOLD

- `PhysicalSignalReport`
- `PhysicalSignalEvent`
- `WorldStateCandidate`

### Derived candidates but HOLD

- `ConnectorIdentity`
- `NetworkObservation`
- `EgressCapability`
- `GatewayConstraint`

### Underdefined

- `Topology`
- `NetworkSegment`
- `LinkState`
- `ServiceState`
- `AvailabilityState`

### Transverse / do not map

- C471 gateway/control objects
- `ReplayablePhysicalProofCandidate`

### Reject as object

- egress audit labels
- connector audit labels
- `PhysicalCoherenceScore`
- `SignalContradictionScore`
- `PhysicalRiskHint`

## 11. Promotion gate

A Telecom candidate may enter `object_map.yaml` only after:

1. at least one stable source defines its meaning;
2. minimum fields are explicit;
3. identity/lifecycle are explicit where relevant;
4. domain ownership is demonstrated;
5. cross-domain overlap is documented;
6. relation to `DomainSignal` is explicit;
7. provenance survives canonicalisation;
8. no authority is embedded in the object;
9. no individual-identification semantics are silently introduced.

## 12. Final verdict

The correct V0 object map remains:

```yaml
status: NOT_YET_DEFINED
objects: []
```

This is not missing work hidden by documentation.

It is the correct result of the current evidence.
