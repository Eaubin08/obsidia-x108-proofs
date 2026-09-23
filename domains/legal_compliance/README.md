# Legal / Compliance

> Domain Pack pour compliance advisory, data governance, claim-scope, privacy readiness, regulatory mapping et audit juridique vérifiable.
>
> **UDIP status : `NEW_DOMAIN_SCAFFOLD`**  
> **Source type : `repo_reference`**  
> **Implementation state : `SCAFFOLD_ONLY`**  
> **Authority : `KX108_ONLY`**

## 1. Vision

Legal / Compliance ne doit jamais devenir un moteur qui “décide ce qui est légal”.

Le corpus existant définit plutôt une couche de **contraintes, readiness, revue, preuves et limites de claims** :

```text
law / policy / compliance source
→ scope / obligation / risk extraction
→ claim-scope boundary
→ human/legal review requirement
→ LegalCompliance DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ human/legal gate si requis
→ receipt / audit export
```

Le domaine peut contextualiser, signaler, structurer et exiger une revue.

Il ne peut ni certifier, ni rendre un avis juridique autonome, ni autoriser un traitement de données personnelles.

## 2. Statut réel

Le pack reste :

- `status: NEW_DOMAIN_SCAFFOLD` ;
- `source_type: repo_reference` ;
- `implementation_state: SCAFFOLD_ONLY`.

Cette synchronisation reconnaît un corpus repository audité.

Elle ne signifie pas :

- conformité RGPD démontrée ;
- certification ISO ;
- SecNumCloud obtenu ;
- avis juridique validé ;
- DPO review effectuée ;
- runtime Legal/Compliance actif ;
- object map implémenté ;
- export juridique opposable prouvé.

`object_map.yaml` reste volontairement vide.

## 3. Source A — RGPD Compliance Scope Guard

Source :

- [RGPD_COMPLIANCE_SCOPE_GUARD](../../runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md)

Statut source :

```text
CONTRACT_SKELETON_ONLY
COPIED_READONLY
runtime branché = NON
```

Le contrat verrouille notamment :

```text
GDPR_ready != GDPR_compliant_legal
ISO27001_READY != ISO27001_CERTIFIED
SecNumCloud_target != SecNumCloud_certified
DPA_template != DPA_signed
legal_template != validated_legal_advice
```

Il prévoit aussi :

- registre de traitement ;
- minimisation ;
- rétention ;
- human gate ;
- compliance review ;
- claim-scope.

Cette source fournit une base majeure au Domain Pack, mais ne doit jamais être présentée comme conformité juridique effective.

## 4. Source B — Compliance Scope Guard

Source :

- [COMPLIANCE_SCOPE_GUARD_SPEC](../../runtime_contracts/compliance_data_governance_spec/specs/COMPLIANCE_SCOPE_GUARD_SPEC.md)

Statut :

```text
Authority: KX108_ONLY
Runtime active: false
```

La spec peut marquer :

- processing risk ;
- retention risk ;
- access risk ;
- privacy risk ;
- audit-readiness context ;
- human-review requirement.

Elle ne peut pas certifier :

- conformité RGPD ;
- conformité légale ;
- conformité ISO ;
- security posture ;
- autorisation de traitement personnel.

Cette distinction devient un invariant du Domain Pack.

## 5. Source C — Data Governance Advisory

Source :

- [DATA_GOVERNANCE_ADVISORY_SPEC](../../runtime_contracts/compliance_data_governance_spec/specs/DATA_GOVERNANCE_ADVISORY_SPEC.md)

Statut :

```text
advisory-only
Runtime active: false
```

Elle peut définir :

- futurs champs de packets ;
- checklists ;
- scope labels ;
- evidence refs.

Elle ne peut pas :

- approuver un traitement ;
- écrire en mémoire ;
- écrire dans le graphe ;
- exécuter un outil ;
- contourner X108.

Donc :

```text
DATA GOVERNANCE ADVISORY != PROCESSING AUTHORIZATION
```

## 6. Source D — Legal-Grade Audit Export

Source :

- [Legal-Grade Audit Export](../../periphery/specs/Spec_17__Legal_Grade_Audit_Export_P149.md)

Statut :

```text
À_FORMALISER_OU_À_PROUVER
```

La spec décrit une cible d'export vérifiable par un tiers :

- manifest ;
- policy ;
- traces ;
- signed tickets ;
- replay ;
- violations ;
- Merkle root ;
- signatures ;
- report PDF.

Elle contient des formulations historiques fortes sur la “valeur légale”.

Le Domain Pack doit les traiter comme **objectif de conception à démontrer**, pas comme propriété juridique acquise.

```text
AUDIT EXPORT TARGET != LEGAL ADMISSIBILITY PROVEN
```

## 7. Source E — Regulatory Compliance Mapping EU/FR

Source :

- [Regulatory Compliance Mapping EU/FR](../../periphery/specs/Spec_20__Regulatory_Compliance_Mapping_EU_FR_P156_P160_valider_V4.md)

Statut :

```text
FORMALISÉ_À_VALIDER
```

La source contient des affirmations historiques ambitieuses telles que :

- “conforme par construction” ;
- positionnement au-dessus d'exigences high-risk ;
- catégorie juridique défendable.

Ces affirmations **ne sont pas promues en faits UDIP**.

Le Domain Pack les classe comme :

```text
HISTORICAL_REGULATORY_POSITIONING_TO_VALIDATE
```

Toute revendication publique doit être soutenue séparément par revue juridique et preuves applicables.

## 8. Périmètre V0

Le Domain Pack reconnaît maintenant les extensions documentaires suivantes :

### Scope / Readiness

- `compliance_scope`
- `privacy_readiness`
- `claim_scope`

### Data Governance

- `data_governance_advisory`
- `processing_risk`
- `retention_access_privacy_risk`

### Review / Regulation

- `human_legal_review_gate`
- `regulatory_mapping`

### Audit

- `legal_audit_export`

Ces extensions décrivent le périmètre de conception.

Elles ne valent ni conformité, ni certification, ni autorisation de traitement.

## 9. Claim-scope

Le Domain Pack doit distinguer :

```text
readiness
!= compliance

compliance preparation
!= legal validation

template
!= legal advice

target
!= certification

audit export
!= legal admissibility proven

regulatory mapping
!= regulator approval
```

Le claim-scope est donc une fonction centrale du domaine.

## 10. Personal data boundary

Pour les données personnelles, le corpus existant exige une prudence renforcée.

Les sources décrivent notamment :

- registre de traitement ;
- minimisation ;
- rétention ;
- revue humaine/légale ;
- preuve documentaire ;
- claim-scope limité.

Le Domain Pack ne doit jamais convertir cette préparation en autorisation automatique.

```text
PERSONAL DATA CONTEXT != PROCESSING PERMISSION
```

## 11. Human / legal review

Le corpus impose explicitement une revue humaine dans certains cas.

Cette revue doit rester distincte de KX108 :

```text
KX108 authority
!=
human legal validation
```

KX108 peut gouverner l'admission d'une action dans l'architecture.

Il ne remplace pas un avocat, un DPO, un organisme certificateur ou une autorité réglementaire.

## 12. Point de branchement cible

```text
law / regulation / policy / compliance source
→ scope extraction
→ processing / retention / access / privacy risk
→ claim-scope
→ human/legal review requirement
→ LegalCompliance DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ human/legal gate si requis
→ Binder si conséquence exécutable
→ Receipt / Audit Export
```

## 13. Non-souveraineté

Invariants Legal / Compliance :

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

## 14. Source model

Le pack utilise `source_type: repo_reference`.

### REPO_CONTRACT_SOURCE

- `runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md`

### REPO_SPEC_SOURCE

- `runtime_contracts/compliance_data_governance_spec/specs/COMPLIANCE_SCOPE_GUARD_SPEC.md`
- `runtime_contracts/compliance_data_governance_spec/specs/DATA_GOVERNANCE_ADVISORY_SPEC.md`

### REPO_SPEC_SOURCE

- `periphery/specs/Spec_17__Legal_Grade_Audit_Export_P149.md`

### REPO_SPEC_SOURCE

- `periphery/specs/Spec_20__Regulatory_Compliance_Mapping_EU_FR_P156_P160_valider_V4.md`

### REPO_AUDIT_SOURCE

- `planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md`

### Maturité des sources

La nature et la maturité sont séparées selon [SOURCE_TAXONOMY_V0](../../udip/SOURCE_TAXONOMY_V0.md).

Exemples :

- RGPD guard → `REPO_CONTRACT_SOURCE` + `CONTRACT_SKELETON_ONLY` ;
- Compliance/Data Governance specs → `REPO_SPEC_SOURCE` + `RUNTIME_INACTIVE` ;
- Legal-Grade Audit Export → `REPO_SPEC_SOURCE` + `TO_FORMALIZE_OR_PROVE` ;
- Regulatory Mapping → `REPO_SPEC_SOURCE` + `TO_VALIDATE`.

## 15. Conformance

Le profil Legal / Compliance impose désormais :

```text
READINESS != CERTIFICATION
LEGAL TEMPLATE != LEGAL ADVICE
COMPLIANCE SIGNAL != LEGAL VERDICT
PROCESSING RISK != PROCESSING AUTHORIZATION
REGULATORY MAPPING != REGULATOR APPROVAL
KX108_ONLY
```

Les tests correspondants restent à créer.

Voir [conformance.md](conformance.md).

## 16. Manques

Le pack reste incomplet sur :

- object map ;
- taxonomie canonique Legal / Compliance ;
- DomainSignal domaine ;
- parser / source adapters réglementaires ;
- claim-scope runtime ;
- human/legal review integration ;
- audit export prouvé ;
- tests de non-overclaim ;
- tests de non-souveraineté ;
- preuve de conformité réelle ;
- validation juridique externe.

## 17. Object-model candidate audit

L'audit READ_ONLY des objets candidats est maintenant documenté dans [OBJECT_MODEL_CANDIDATES_V0.md](OBJECT_MODEL_CANDIDATES_V0.md).

Verdict :

```text
objets prêts à promouvoir = 0
```

Les candidats les plus structurés sont `ClaimScope`, `AuditExport`, `RegulatoryMapping`, `ProcessingRisk` et `PrivacyRisk`, mais aucun ne possède encore un schéma canonique suffisamment figé.

Le `object_map.yaml` reste volontairement vide.