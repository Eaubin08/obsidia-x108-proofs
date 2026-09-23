# Energy / Critical Infrastructure Object Model Candidates V0

Status: CANDIDATE_AUDIT_ONLY
Domain: energy_critical_infrastructure
Object map impact: NONE
Runtime impact: NONE
Authority impact: NONE

## 1. Purpose

This document records Energy object candidates without promoting them into `object_map.yaml`.

The current Energy source corpus contains real code and metrics, but real code does not automatically imply stable domain objects.

The key distinction is:

```text
metric
!=
domain object
```

and:

```text
transverse packet
!=
Energy-owned object
```

## 2. Classification

Labels:

- `SOURCE_DEFINED`
- `DERIVED_CANDIDATE`
- `TRANSVERSE_DO_NOT_MAP`
- `HOLD_UNDERDEFINED`
- `REJECT_NOT_DOMAIN_OBJECT`

## 3. Audited sources

Repository sources:

- `docs/periphery/ENERGY_THERMO_GOVERNOR_V0.md`
- `periphery/energy_thermo.py`
- `periphery/agents/energy_thermo_agent.py`
- `periphery/common.py`
- `periphery/agent_contracts.py`
- `apps/obsidia_api/brody_thermo_coherence_time_unified.py`
- `specs/01_X108_AUTHORITY/FAIL_CLOSED_PRIORITY_SPEC.md`
- `tests/non_sovereignty/test_energy_cannot_authorize.py`

Internal concept sources:

- `internal://THERMO_COMPUTE_LAYER`
- `internal://Energy sandbox/freeze/stress history`

## 4. Real Energy metrics

The current implementation explicitly computes or carries:

- `pin`;
- `pout`;
- `energy_cost`;
- `compute_cost`;
- `attention_cost`;
- `recovery_cost`;
- `useful_work`;
- `energy_efficiency`;
- `thermo_debt`;
- `truth_score`;
- `sigma_score`;
- `sigma_truth_mismatch`.

Classification:

```text
REJECT_NOT_DOMAIN_OBJECT
```

Reason:

These are fields / metrics.

They may belong inside a future assessment object, but they are not standalone domain entities.

## 5. Real risk and contradiction labels

Current code emits:

- `ENERGY_INEFFICIENT`;
- `SIGMA_TRUTH_MISMATCH`;
- `THERMO_DEBT_HIGH`;
- `COLLAPSE_DISGUISED_HIGH_SIGMA`.

It may recommend:

- `HOLD`;
- `BLOCK_CANDIDATE`.

Classification:

```text
REJECT_NOT_DOMAIN_OBJECT
```

Reason:

These are risk flags, contradiction labels or gate hints.

They belong on a signal/assessment.

They must not become Energy objects.

## 6. Real transverse objects that MUST NOT be mapped as Energy-owned

### `ActionCandidate`

Source: `periphery/common.py`

Classification:

```text
TRANSVERSE_DO_NOT_MAP
```

Reason:

It is a generic periphery action candidate with fields such as domain, actor, intent, action type and payload.

It is not Energy-specific.

### `PeripheralSignalPacket`

Source: `periphery/common.py`

Classification:

```text
TRANSVERSE_DO_NOT_MAP
```

Reason:

It is a generic non-sovereign signal packet used to carry metrics, unknowns, risk flags, contradictions and evidence refs.

### `AgentResult`

Source: `periphery/agent_contracts.py`

Classification:

```text
TRANSVERSE_DO_NOT_MAP
```

Reason:

It is a generic agent wrapper result, not Energy semantics.

### `NonSovereignAgentSpec`

Classification:

```text
TRANSVERSE_DO_NOT_MAP
```

Reason:

It expresses a universal/periphery authority boundary.

## 7. Thermo / Compute candidate objects

### `ThermoAssessment`

Classification: `DERIVED_CANDIDATE`

Decision: HOLD.

Rationale:

The code clearly groups a coherent set of Energy/Thermo metrics and risk flags.

A future object could reasonably bundle:

- efficiency;
- thermo debt;
- mismatch;
- risks;
- contradictions;
- evidence refs.

But no current source defines an object named `ThermoAssessment` or freezes its schema.

Therefore it must not enter `object_map.yaml` yet.

### `EnergyThermoObservation`

Classification: `DERIVED_CANDIDATE`

Decision: HOLD.

Rationale:

This name would reflect the advisory nature better than an authoritative assessment, but it is still invented by the audit rather than source-defined.

### `ThermoCoherenceTimePacket`

The file `brody_thermo_coherence_time_unified.py` defines a unified readonly packet version.

Classification:

```text
TRANSVERSE_DO_NOT_MAP
```

Reason:

It explicitly unifies Thermo, coherence and time across Brody/periphery concerns.

It is not a stable Energy business object.

## 8. Physical Critical Infrastructure candidates

The current manifest defines the family:

- `physical_infrastructure`;
- `fail_closed`;
- `real_world_execution_constraints`.

However, the source corpus does **not** currently define stable objects such as:

- `CriticalInfrastructureAsset`;
- `GridNode`;
- `PowerSource`;
- `EnergyFlow`;
- `PhysicalInfrastructureState`.

Classification for all such names:

```text
HOLD_UNDERDEFINED
```

Reason:

These would be invented domain models.

The current source material does not provide their field schemas, lifecycle or boundaries.

## 9. Fail-closed is not an Energy object

The source `FAIL_CLOSED_PRIORITY_SPEC.md` defines an authority rule:

```text
BLOCK > HOLD > ALLOW
```

Classification:

```text
TRANSVERSE_DO_NOT_MAP
```

Fail-closed is a governance/authority property.

It must not be represented as an Energy-owned object.

## 10. Placeholder test does not define objects

`tests/non_sovereignty/test_energy_cannot_authorize.py` currently contains only `assert True`.

It provides no object semantics.

Classification:

```text
REJECT_NOT_DOMAIN_OBJECT
```

for object-model purposes.

## 11. Current candidate verdict

### Ready to map now

```text
NONE
```

### Derived candidates but HOLD

- `ThermoAssessment`
- `EnergyThermoObservation`

### Transverse / do not map

- `ActionCandidate`
- `PeripheralSignalPacket`
- `AgentResult`
- `NonSovereignAgentSpec`
- unified Thermo/Coherence/Time packet
- fail-closed authority rule

### Reject as object

- all current Energy/Thermo metrics;
- all current Energy risk labels;
- contradictions;
- gate hints;
- placeholder test.

### Underdefined physical-domain candidates

- physical infrastructure asset;
- physical infrastructure state;
- energy flow;
- power/grid object;
- execution-constrained physical target.

These remain unnamed/frozen only as conceptual categories, not canonical objects.

## 12. Promotion gate for Thermo objects

A Thermo candidate may enter `object_map.yaml` only after:

1. a stable source gives it a canonical name;
2. field schema is explicit;
3. metric units/ranges are defined;
4. relation to `PeripheralSignalPacket` is explicit;
5. relation to `DomainSignal` is explicit;
6. no gate hint becomes authority;
7. evidence/provenance rules are defined;
8. replay behavior is documented if claimed.

## 13. Promotion gate for Physical Infrastructure objects

A physical-infrastructure candidate additionally requires:

1. real source type or simulator contract;
2. provenance;
3. authenticity/reality boundary;
4. physical identity/reference model;
5. consequence model;
6. Binder boundary where action exists;
7. ExecutionOutcome semantics;
8. receipt/proof requirements.

## 14. Final verdict

The correct V0 object map remains:

```yaml
status: NOT_YET_DEFINED
objects: []
```

The evidence currently supports Energy metrics, packets and architecture boundaries.

It does not yet support a stable Energy DomainObjectMap.
