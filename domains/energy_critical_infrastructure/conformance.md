# Energy / Critical Infrastructure Conformance Notes

Status: SCAFFOLD ONLY / DOMAIN PROFILE DOCUMENTED

Runtime conformance: NOT PROVEN
UDIP Energy tests implemented with meaningful authority assertions: NO
Decision authority: KX108_ONLY

## 1. Universal UDIP constraints

Energy MUST:

- preserve unknowns, contradictions, risk flags, evidence references and provenance;
- never create a parallel authority;
- never bypass KX108 for governed admission;
- never bypass Binder for governed execution;
- never turn source provenance into trust;
- never treat replay as execution;
- never leak Energy-specific semantics into Universal Core.

## 2. Energy-specific invariants

```text
ENERGY METRIC != DECISION
ENERGY EFFICIENCY != AUTHORITY
THERMO DEBT != BLOCK AUTHORITY
SIGMA/TRUTH MISMATCH != FINAL VERDICT
BLOCK_CANDIDATE != BLOCK
PHYSICAL RISK != EXECUTION RIGHT
FAIL_CLOSED POLICY != DOMAIN AUTHORITY
DOMAIN != AUTHORITY
KX108_ONLY
```

## 3. Thermo / Compute family

Thermo/Compute MAY provide:

- energy efficiency;
- thermo debt;
- compute cost;
- attention cost;
- recovery cost;
- useful work;
- Sigma/truth mismatch;
- advisory risk flags;
- contradiction signals;
- recommended HOLD;
- BLOCK candidate.

It MUST NOT:

- emit final ACT/HOLD/BLOCK authority;
- convert `BLOCK_CANDIDATE` into `BLOCK`;
- treat low efficiency as execution prohibition by itself;
- mutate the kernel;
- become an execution adapter.

## 4. Physical Critical Infrastructure family

A future physical-infrastructure path MAY provide:

- physical state observations;
- source provenance;
- authenticity evidence;
- safety constraints;
- physical risk;
- execution constraints;
- evidence refs.

It MUST NOT:

- treat physical risk as execution authority;
- bypass KX108;
- bypass Binder;
- treat a sensor/source as trusted solely because it exists;
- turn fail-closed policy into domain sovereignty.

## 5. Fail-closed relation

The universal fail-closed rule remains owned by the authority boundary.

Energy MAY supply conditions that contribute to a HOLD/BLOCK decision.

Energy MUST NOT own the final priority rule.

```text
Energy signal
→ governance context
→ KX108
→ final authority
```

## 6. Current test limitation

The file:

`tests/non_sovereignty/test_energy_cannot_authorize.py`

currently contains only:

```python
def test_non_sovereign():
    assert True
```

Therefore:

```text
TEST FILE PRESENT != NON-SOVEREIGNTY PROVEN
```

This placeholder MUST NOT be cited as evidence of authority isolation.

## 7. Candidate future tests

These tests are requirements only and are not implemented yet:

- `test_energy_metric_cannot_emit_act`
- `test_energy_metric_cannot_emit_final_block`
- `test_energy_block_candidate_requires_kx108`
- `test_energy_thermo_debt_not_authority`
- `test_energy_sigma_truth_mismatch_advisory_only`
- `test_energy_physical_risk_requires_kx108`
- `test_energy_execution_requires_binder`
- `test_energy_source_provenance_not_trust`
- `test_energy_no_kernel_mutation`
- `test_energy_kx108_only`

## 8. Promotion condition

Energy remains `SCAFFOLD_ONLY` until at minimum:

1. object map is audited;
2. Thermo/Compute and Physical Infrastructure objects are explicitly separated;
3. DomainSignal mappings exist;
4. meaningful non-sovereignty tests pass;
5. KX108 boundary is exercised;
6. Binder is explicit for any physical consequence;
7. receipts/replay are defined where consequence exists;
8. source authenticity is addressed for physical infrastructure;
9. code presence is not confused with UDIP runtime integration.

Documentation and peripheral code alone do not establish Domain Pack conformance.
