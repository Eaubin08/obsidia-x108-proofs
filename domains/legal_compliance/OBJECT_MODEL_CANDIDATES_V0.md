# Legal / Compliance Object Model Candidates V0

Status: CANDIDATE_AUDIT_ONLY
Domain: legal_compliance
Object map impact: NONE
Runtime impact: NONE
Authority impact: NONE
Legal status impact: NONE

## 1. Purpose

This document audits Legal / Compliance object candidates without promoting them into `object_map.yaml`.

The governing rule is:

```text
compliance concept
!=
legal object proven
```

and:

```text
readiness artifact
!=
legal status
```

The current corpus contains real scope guards, readiness boundaries, advisory specs and audit-export targets.

It does not contain a validated legal ontology.

## 2. Classification

### SOURCE_DEFINED

The concept is explicitly named or structured in an audited source.

### DERIVED_CANDIDATE

The candidate is a reasonable abstraction from several sources, but not canonically defined.

### TRANSVERSE_DO_NOT_MAP

The element belongs to generic proof, governance, ticketing, audit or authority infrastructure.

### HOLD_UNDERDEFINED

The concept may belong to Legal / Compliance but lacks stable schema, lifecycle or legal validation.

### REJECT_NOT_DOMAIN_OBJECT

The item is a risk label, checklist field, claim status, readiness flag or certification label rather than a stable domain object.

## 3. Audited sources

- `runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md`
- `runtime_contracts/compliance_data_governance_spec/specs/COMPLIANCE_SCOPE_GUARD_SPEC.md`
- `runtime_contracts/compliance_data_governance_spec/specs/DATA_GOVERNANCE_ADVISORY_SPEC.md`
- `periphery/specs/Spec_17__Legal_Grade_Audit_Export_P149.md`
- `periphery/specs/Spec_20__Regulatory_Compliance_Mapping_EU_FR_P156_P160_valider_V4.md`
- `planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md`

## 4. Candidate: ComplianceRequirement

Classification: `DERIVED_CANDIDATE`

Decision: HOLD.

Source basis:

- required proofs;
- data-governance constraints;
- compliance review requirements;
- register/minimisation/retention expectations.

Why not promoted:

No source defines a canonical `ComplianceRequirement` object with stable fields, identity, jurisdiction, applicability and lifecycle.

## 5. Candidate: ProcessingRisk

Classification: `SOURCE_DEFINED`

Decision: HOLD.

The Compliance Scope Guard explicitly permits marking:

- processing risk;
- retention risk;
- access risk;
- privacy risk.

However `processing risk` is currently a category/field, not a stable object schema.

It may ultimately belong inside a broader assessment or compliance finding.

## 6. Candidate: RetentionRule

Classification: `DERIVED_CANDIDATE`

Decision: HOLD.

Source basis:

- retention requirements;
- data governance;
- personal-data handling constraints.

No canonical rule schema is defined.

Fields such as jurisdiction, scope, duration, lawful basis, trigger and exception model are not frozen by the source corpus.

## 7. Candidate: AccessRule

Classification: `DERIVED_CANDIDATE`

Decision: HOLD.

Source basis:

- access risk;
- governance constraints;
- memory/write boundaries.

Problem:

Access control is strongly cross-domain.

A Legal / Compliance object should only own the **legal/compliance constraint**, not universal permission infrastructure.

## 8. Candidate: PrivacyRisk

Classification: `SOURCE_DEFINED`

Decision: HOLD.

Like processing/retention/access risk, privacy risk is explicitly allowed by the scope guard.

But it is currently a risk category rather than a canonical object.

## 9. Candidate: ReviewRequirement

Classification: `DERIVED_CANDIDATE`

Decision: HOLD.

Source basis:

- `human-review requirement`;
- `human_gate_required: true`;
- audit/legal review conditions.

This candidate is strong, but no stable schema exists for:

- reviewer role;
- trigger;
- required evidence;
- jurisdiction;
- completion status;
- validity window.

## 10. Candidate: ClaimScope

Classification: `SOURCE_DEFINED`

Decision: HOLD.

The RGPD guard explicitly uses `claim_scope`, including:

```text
CLAIMABLE_SPEC_ONLY
```

Claim-scope is central to this Domain Pack.

However the current corpus does not define a stable object with canonical fields and lifecycle.

It may become one of the strongest future Legal / Compliance objects after schema freeze.

## 11. Candidate: LegalEvidenceRef

Classification: `DERIVED_CANDIDATE`

Decision: HOLD.

Sources use:

- evidence refs;
- OS3EvidenceTicket;
- audit logs;
- signed tickets;
- reports;
- templates;
- review artifacts.

A Legal-specific evidence reference could be useful, but generic evidence containers already exist.

The domain should reference evidence without cloning universal proof objects.

## 12. Evidence / governance containers that MUST NOT become Legal-owned objects

### OS3EvidenceTicket

Classification: `TRANSVERSE_DO_NOT_MAP`

### BoundaryContract

Classification: `TRANSVERSE_DO_NOT_MAP`

### RuntimeAdmissionContract

Classification: `TRANSVERSE_DO_NOT_MAP`

### ContextPacket

Classification: `TRANSVERSE_DO_NOT_MAP`

### IntentEnvelope

Classification: `TRANSVERSE_DO_NOT_MAP`

### DecisionTicket

Classification: `TRANSVERSE_DO_NOT_MAP`

Reason:

These are universal governance/proof surfaces.

Legal / Compliance may reference or constrain them, but must not claim ownership.

## 13. Candidate: AuditExport

Classification: `SOURCE_DEFINED`

Decision: HOLD.

The Legal-Grade Audit Export source defines a target bundle:

```text
audit_export/
├─ README.txt
├─ manifest.json
├─ policy/
├─ traces/
├─ tickets/
├─ replay/
├─ violations/
├─ hashes/
├─ signatures/
└─ report/
```

This is a real source-defined artifact candidate.

But the spec is `À_FORMALISER_OU_À_PROUVER`.

Therefore:

```text
SOURCE_DEFINED
but
LEGAL_EFFECT_UNPROVEN
```

No claim of legal admissibility follows from object promotion.

## 14. Audit-export internal files are not separate Legal objects by default

Examples:

- manifest;
- policy binary;
- trace bundle;
- signed tickets;
- replay result;
- violations;
- Merkle root;
- signatures;
- PDF report.

Most of these are proof/audit sub-artifacts.

Classification:

```text
TRANSVERSE_DO_NOT_MAP
```

or fields/components of a future `AuditExport`, unless later evidence shows domain ownership.

## 15. Readiness and certification labels are not objects

Examples:

- `GDPR_ready`;
- `GDPR_compliant_legal`;
- `ISO27001_READY`;
- `ISO27001_CERTIFIED`;
- `SecNumCloud_target`;
- `SecNumCloud_certified`;
- `CLAIMABLE_SPEC_ONLY`.

Classification:

```text
REJECT_NOT_DOMAIN_OBJECT
```

They are states/labels/claim bounds.

## 16. Templates are not automatically domain objects

Examples:

- DPA template;
- legal template;
- privacy policy template;
- DPIA template.

Classification:

```text
HOLD_UNDERDEFINED
```

A template may eventually be represented as a governed document object, but:

```text
template
!= validated legal instrument
```

The current corpus does not define a canonical document model.

## 17. Candidate: RegulatoryMapping

Classification: `SOURCE_DEFINED`

Decision: HOLD.

A dedicated Regulatory Compliance Mapping source exists.

But the source is `FORMALISÉ_À_VALIDER` and contains historical assertions that must not become facts.

A future object would need to distinguish:

- regulation reference;
- requirement;
- system control mapping;
- evidence;
- review status;
- jurisdiction;
- validation status;
- claim scope.

None of this is frozen today.

## 18. Candidate: DataGovernanceConstraint

Classification: `DERIVED_CANDIDATE`

Decision: HOLD.

The advisory spec clearly supports future:

- packet fields;
- review checklists;
- scope labels;
- evidence references.

But the domain must not duplicate universal policy or access-control objects.

A candidate should represent compliance constraints, not execution permissions.

## 19. Current candidate verdict

### Ready to map now

```text
NONE
```

### Source-defined but HOLD

- `ProcessingRisk`
- `PrivacyRisk`
- `ClaimScope`
- `AuditExport`
- `RegulatoryMapping`

### Derived candidates but HOLD

- `ComplianceRequirement`
- `RetentionRule`
- `AccessRule`
- `ReviewRequirement`
- `LegalEvidenceRef`
- `DataGovernanceConstraint`

### Underdefined

- legal/DPA/privacy/DPIA document templates as governed objects

### Transverse / do not map

- `OS3EvidenceTicket`
- `BoundaryContract`
- `RuntimeAdmissionContract`
- `ContextPacket`
- `IntentEnvelope`
- `DecisionTicket`
- generic receipts/replay/hash/signature surfaces

### Reject as object

- readiness labels;
- certification labels;
- claim-status values;
- raw risk categories when used only as fields;
- regulator/certification claims.

## 20. Legal claim boundary

Even if a candidate is eventually promoted:

```text
object exists
!=
legal status exists
```

Examples:

```text
AuditExport object
!= legal admissibility

RegulatoryMapping object
!= regulator approval

ClaimScope object
!= legal validation

ReviewRequirement object
!= review completed

DPA document object
!= signed DPA
```

This boundary is mandatory.

## 21. Promotion gate

A Legal / Compliance candidate may enter `object_map.yaml` only after:

1. source ownership is domain-specific;
2. canonical name is stable;
3. field schema is explicit;
4. jurisdiction/scope is represented where relevant;
5. lifecycle/status semantics are explicit;
6. claim-scope is preserved;
7. evidence references are explicit;
8. human/legal review requirements are explicit;
9. no object implies certification or legal advice;
10. no object grants execution permission;
11. relation to `DomainSignal` is explicit;
12. legal review exists if a real legal status is claimed.

## 22. Final verdict

The correct Legal / Compliance V0 object map remains:

```yaml
status: NOT_YET_DEFINED
objects: []
```

The current corpus supports strong compliance/readiness boundaries and several candidate artifacts.

It does not yet support a validated Legal / Compliance ontology.
