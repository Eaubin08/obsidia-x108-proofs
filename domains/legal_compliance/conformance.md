# Legal / Compliance Conformance Notes

Status: SCAFFOLD ONLY / DOMAIN PROFILE DOCUMENTED

Runtime conformance: NOT PROVEN
UDIP Legal/Compliance tests implemented in this Domain Pack: NONE
Decision authority: KX108_ONLY
Legal validation authority: HUMAN / EXTERNAL LEGAL REVIEW WHEN REQUIRED

## 1. Universal UDIP constraints

Legal / Compliance MUST:

- preserve unknowns, contradictions, risk flags, evidence references and provenance;
- never create a parallel authority;
- never bypass KX108 for governed admission;
- never bypass Binder for governed execution;
- never turn source provenance into trust;
- never treat replay as execution;
- never leak domain-specific legal semantics into Universal Core.

## 2. Legal / Compliance invariants

```text
READINESS != CERTIFICATION
READINESS != LEGAL COMPLIANCE
LEGAL TEMPLATE != LEGAL ADVICE
DPA TEMPLATE != SIGNED DPA
REGULATORY MAPPING != REGULATOR APPROVAL
COMPLIANCE SIGNAL != LEGAL VERDICT
PROCESSING RISK != PROCESSING AUTHORIZATION
DATA GOVERNANCE ADVISORY != EXECUTION PERMISSION
AUDIT EXPORT TARGET != LEGAL ADMISSIBILITY PROVEN
POLICY != AUTHORITY
DOMAIN != AUTHORITY
KX108_ONLY
```

## 3. Compliance scope / risk

The domain MAY eventually emit:

- processing risk;
- retention risk;
- access risk;
- privacy risk;
- audit-readiness context;
- human-review requirement;
- claim-scope labels;
- evidence references.

It MUST NOT:

- certify RGPD compliance;
- certify ISO compliance;
- authorize personal-data processing;
- turn a risk score into legal permission;
- turn readiness into production approval.

## 4. Data governance advisory

The domain MAY define:

- packet fields;
- review checklists;
- scope labels;
- evidence references;
- proposed retention/minimization constraints.

It MUST NOT:

- write memory;
- write graph state;
- execute tools;
- approve processing;
- bypass KX108;
- act as Binder permission.

## 5. Human / legal review

When a source or policy requires legal/DPO/human review:

```text
KX108 ACT
!=
legal validation complete
```

A governed system action and a legal validation are separate conditions.

The Domain Pack MUST preserve that distinction.

## 6. Regulatory claims

Historical regulatory mapping documents MAY be referenced as design context.

They MUST NOT be restated as established facts without separate evidence.

Forbidden automatic claims include:

- "RGPD compliant";
- "ISO certified";
- "SecNumCloud compliant";
- "AI Act compliant by construction";
- "legal-ready";
- "regulator approved".

## 7. Audit export

A future audit export MAY target:

- manifest;
- policy;
- traces;
- signed tickets;
- replay result;
- violations;
- Merkle/hash material;
- signatures;
- report.

It MUST NOT claim legal admissibility merely because the structure exists.

```text
CRYPTOGRAPHIC VERIFIABILITY
!=
LEGAL ADMISSIBILITY AUTOMATICALLY PROVEN
```

## 8. Candidate future tests

These are requirements only. They are not implemented yet.

- `test_legal_readiness_not_certification`
- `test_legal_template_not_legal_advice`
- `test_legal_dpa_template_not_signed_dpa`
- `test_legal_processing_risk_not_authorization`
- `test_legal_regulatory_mapping_not_regulator_approval`
- `test_legal_audit_export_not_legal_admissibility_claim`
- `test_legal_human_review_gate_preserved`
- `test_legal_data_governance_cannot_write`
- `test_legal_no_kernel_mutation`
- `test_legal_kx108_only`

## 9. Promotion condition

Legal / Compliance remains `SCAFFOLD_ONLY` until at minimum:

1. object model is audited;
2. DomainSignal mapping exists;
3. claim-scope survives canonicalisation;
4. human/legal review requirements are explicit;
5. meaningful non-overclaim tests pass;
6. KX108 boundary is exercised;
7. Binder remains separate from legal validation;
8. audit export claims are evidence-bounded;
9. privacy/data-governance rules remain non-sovereign;
10. external legal review exists where a legal status is claimed.

Documentation of compliance architecture is not legal compliance.
