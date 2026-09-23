# UDIP Source Inventory V0

Status: CURRENT_DOCUMENTATION
Audited baseline: b7393ab0090b4f2a23fe266357c33e13237f8605
Runtime impact: NONE
Authority impact: NONE

This inventory summarizes the current source state of all 16 UDIP Domain Packs.

Canonical source vocabulary: [SOURCE_TAXONOMY_V0](../udip/SOURCE_TAXONOMY_V0.md).

## 1. Trading

- Domain: `trading`
- Status: `EXISTING_REFERENCE`
- Source type: `external_reference`
- Source status: `REFERENCE_ONLY`
- Implementation: `SCAFFOLD_ONLY`

Current sources:

- `external://OBSIDIA_TRADING`
- `domains/trading/`
- `domain_packets/trading_decisional_form_v0.yaml`
- `sigma/domains/trading_agents.py`

Main debt:

- UDIP-native adaptation;
- real object map;
- explicit wrapper around historical execution surfaces;
- domain-specific conformance tests.

## 2. Bank

- Domain: `bank`
- Status: `EXISTING_REFERENCE`
- Source type: `repo_reference`
- Source status: `REFERENCE_ONLY`
- Implementation: `SCAFFOLD_ONLY`

Current sources:

- `domain_packets/bank_decisional_form_v0.yaml`
- `domains/bank/`
- `sigma/domains/bank_agents.py`
- `examples/bank_normal.json`
- `examples/bank_suspicious.json`

Main debt:

- Core-neutral object map;
- native UDIP adaptation;
- domain-specific conformance;
- no runtime migration claimed.

## 3. GPS / Defense / Aviation

- Domain: `gps_defense_aviation`
- Status: `EXISTING_REFERENCE`
- Source type: `repo_reference`
- Source status: `REFERENCE_ONLY`
- Implementation: `SCAFFOLD_ONLY`

Current sources:

- `domain_packets/gps_defense_aviation_decisional_form_v0.yaml`
- `domains/gps/`
- `sigma/domains/gps_defense_aviation_agents.py`

Main debt:

- Core-neutral object map;
- conditional physical-extension mapping;
- domain-specific conformance;
- no runtime migration claimed.

## 4. Ecom

- Domain: `ecom`
- Status: `PARTIAL_REFERENCE`
- Source type: `repo_partial_reference`
- Source status: `REFERENCE_ONLY`
- Implementation: `SCAFFOLD_ONLY`

Exact audited source set:

- `docs/architecture/OBSIDIA_F60_SIGMA_REGISTRY_CANONICAL_DOMAINS.md`
- `examples/ecom_normal.json`
- `sigma/domains/ecom_agents.py`
- `sigma/examples/ecom_normal.json`
- `specs/09_CRITICAL_WORLDS/AGENTIC_COMMERCE_GUARD_LITE_RABATTEMENT_SPEC.md`
- `specs/09_CRITICAL_WORLDS/BANK_TRADING_ECOM_INTENT_ONLY_SPEC.md`
- `tests/integration/test_sigma_bridge_ecom.py`
- `tests/run_combinatorial_ecom_report.json`
- `tests/run_combinatorial_ecom.py`

Known missing domain pieces:

- compensation mechanism;
- customer identity model;
- execution result;
- order lifecycle;
- payment adapter;
- refund mechanism;
- shipment / fulfillment adapter.

## 5. Cybersecurity

- Domain: `cybersecurity`
- Status: `NEW_DOMAIN_SCAFFOLD`
- Source type: `repo_reference`
- Source status: `AUDITED_REFERENCE_SET`
- Implementation: `SCAFFOLD_ONLY`
- Object-model state: `CANDIDATES_HOLD`

Current audited sources:

- `docs/investor/SECURITY_BY_THREAT_OBSOLESCENCE_OBSIDIA_X108.md`
- `periphery/specs/Spec_03__Sandbox_Policy_isolation_et_gouvernance_P21_P30.md`
- `periphery/specs/Spec_18__Incident_Response_Protocol_P150_P154_valider_V4.md`
- `runtime_contracts/boundaries/RSSI_EVIDENCE_ONLY.md`
- `docs/core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.md`
- `planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md`

Object candidates:

- documented in `domains/cybersecurity/OBJECT_MODEL_CANDIDATES_V0.md`;
- ready for promotion: **0**.

## 6. Energy / Critical Infrastructure

- Domain: `energy_critical_infrastructure`
- Status: `NEW_DOMAIN_SCAFFOLD`
- Source type: `mixed_reference`
- Source status: `AUDITED_REFERENCE_SET`
- Implementation: `SCAFFOLD_ONLY`
- Object-model state: `CANDIDATES_HOLD`

Repository sources include:

- `docs/periphery/ENERGY_THERMO_GOVERNOR_V0.md`
- `periphery/energy_thermo.py`
- `periphery/agents/energy_thermo_agent.py`
- `specs/01_X108_AUTHORITY/FAIL_CLOSED_PRIORITY_SPEC.md`
- `tests/non_sovereignty/test_energy_cannot_authorize.py`
- `planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md`

Internal concept sources:

- `internal://THERMO_COMPUTE_LAYER`
- `internal://Energy sandbox/freeze/stress history`

Important limitation:

- `test_energy_cannot_authorize.py` remains `PLACEHOLDER_ONLY`.

Object candidates:

- documented in `domains/energy_critical_infrastructure/OBJECT_MODEL_CANDIDATES_V0.md`;
- ready for promotion: **0**.

## 7. Legal / Compliance

- Domain: `legal_compliance`
- Status: `NEW_DOMAIN_SCAFFOLD`
- Source type: `repo_reference`
- Source status: `AUDITED_REFERENCE_SET`
- Implementation: `SCAFFOLD_ONLY`
- Object-model state: `CANDIDATES_HOLD`

Current audited sources:

- `runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md`
- `runtime_contracts/compliance_data_governance_spec/specs/COMPLIANCE_SCOPE_GUARD_SPEC.md`
- `runtime_contracts/compliance_data_governance_spec/specs/DATA_GOVERNANCE_ADVISORY_SPEC.md`
- `periphery/specs/Spec_17__Legal_Grade_Audit_Export_P149.md`
- `periphery/specs/Spec_20__Regulatory_Compliance_Mapping_EU_FR_P156_P160_valider_V4.md`
- `planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md`

Important source maturities:

- contract skeleton;
- runtime inactive;
- to formalize/prove;
- to validate.

Object candidates:

- documented in `domains/legal_compliance/OBJECT_MODEL_CANDIDATES_V0.md`;
- ready for promotion: **0**.

No legal compliance/certification status is claimed.

## 8. Telecom

- Domain: `telecom`
- Status: `NEW_DOMAIN_SCAFFOLD`
- Source type: `mixed_reference`
- Source status: `AUDITED_REFERENCE_SET`
- Implementation: `SCAFFOLD_ONLY`
- Object-model state: `CANDIDATES_HOLD`

Repository sources:

- `docs/core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.md`
- `specs/external_signals/component_specs/C471_gateway_before_endpoint_prefilter.yaml`
- `planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md`

Internal concept sources:

- `internal://Physical Signal World Model`
- `internal://suite pepite implementé 02.7`
- `internal://OBSIDIA_V5_Texte_Continu_Edition_Livre_2026-08-18`

Object candidates:

- documented in `domains/telecom/OBJECT_MODEL_CANDIDATES_V0.md`;
- ready for promotion: **0**.

## 9. Industry / Maintenance

- Status: `NEW_DOMAIN_SCAFFOLD`
- Source type: `none`
- Implementation: `SCAFFOLD_ONLY`

Declared perimeter:

- machines;
- production;
- maintenance;
- sensors;
- operators.

No audited domain source set.

## 10. BTP / Construction

- Status: `NEW_DOMAIN_SCAFFOLD`
- Source type: `none`
- Implementation: `SCAFFOLD_ONLY`

Declared perimeter:

- terrain;
- plans;
- documents;
- subcontractors;
- planning;
- exceptions.

No audited domain source set.

## 11. Logistics / Supply Chain

- Status: `NEW_DOMAIN_SCAFFOLD`
- Source type: `none`
- Implementation: `SCAFFOLD_ONLY`

Declared perimeter:

- stock;
- warehouse;
- suppliers;
- transport;
- route;
- delivery.

No audited domain source set.

## 12. Insurance

- Status: `NEW_DOMAIN_SCAFFOLD`
- Source type: `none`
- Implementation: `SCAFFOLD_ONLY`

No audited insurance-specific source set.

Generic risk/fraud/evidence mechanisms are not treated as Insurance semantics.

## 13. Facility Management

- Status: `NEW_DOMAIN_SCAFFOLD`
- Source type: `none`
- Implementation: `SCAFFOLD_ONLY`

No audited facility-specific source set.

## 14. Administration

- Status: `NEW_DOMAIN_SCAFFOLD`
- Source type: `none`
- Implementation: `SCAFFOLD_ONLY`

No audited administration-specific source set.

## 15. Health

- Status: `NEW_DOMAIN_SCAFFOLD`
- Source type: `none`
- Implementation: `SCAFFOLD_ONLY`

No audited medical/clinical source set.

Transverse consent, provenance, privacy and human-review mechanisms are not treated as Health semantics.

## 16. HR

- Status: `NEW_DOMAIN_SCAFFOLD`
- Source type: `none`
- Implementation: `SCAFFOLD_ONLY`

No audited HR-specific source set.

Transverse human-context, consent, operator-permission and organization mechanisms are not treated as HR semantics.

## 17. Global source-state summary

```text
EXTERNAL_REFERENCE / REFERENCE_ONLY
  Trading

REPO_REFERENCE / REFERENCE_ONLY
  Bank
  GPS / Defense / Aviation

REPO_PARTIAL_REFERENCE / REFERENCE_ONLY
  Ecom

AUDITED REPO/MIXED REFERENCE SETS
  Cybersecurity
  Energy / Critical Infrastructure
  Legal / Compliance
  Telecom

DECLARED PERIMETER, NO AUDITED SOURCE SET
  Industry / Maintenance
  BTP / Construction
  Logistics / Supply Chain

TRUE EMPTY DOMAIN SCAFFOLDS
  Insurance
  Facility Management
  Administration
  Health
  HR
```

All 16 Domain Packs remain `implementation_state: SCAFFOLD_ONLY`.
