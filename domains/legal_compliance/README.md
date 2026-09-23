# Legal / Compliance

> Domain Pack futur pour compliance, data governance, claim-scope et audit réglementaire.
>
> **UDIP status : `NEW_DOMAIN_SCAFFOLD`**  
> **Implementation state : `SCAFFOLD_ONLY`**  
> **Authority : `KX108_ONLY`**

## 1. Vision

Le dossier UDIP est encore vide, mais le dépôt possède déjà un corpus compliance substantiel.

Le point central n'est pas “Obsidia décide ce qui est légal”.

La doctrine existante est au contraire :

```text
readiness
≠ conformité finale

template
≠ avis juridique

scope guard
≠ certification

compliance context
≠ autorité
```

Le Domain Pack Legal / Compliance devrait donc structurer les contraintes, preuves, obligations de revue et limites de claims sans produire lui-même un verdict juridique souverain.

## 2. Corpus réel

Sources principales :

- [RGPD Compliance Scope Guard](../../runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md)
- [Compliance Scope Guard Spec](../../runtime_contracts/compliance_data_governance_spec/specs/COMPLIANCE_SCOPE_GUARD_SPEC.md)
- [Data Governance Advisory Spec](../../runtime_contracts/compliance_data_governance_spec/specs/DATA_GOVERNANCE_ADVISORY_SPEC.md)
- [Legal-Grade Audit Export](../../periphery/specs/Spec_17__Legal_Grade_Audit_Export_P149.md)
- [Regulatory Compliance Mapping EU/FR](../../periphery/specs/Spec_20__Regulatory_Compliance_Mapping_EU_FR_P156_P160_valider_V4.md)

## 3. Scope guard

Le `COMPLIANCE_SCOPE_GUARD_SPEC` autorise à signaler :

- processing risk ;
- retention risk ;
- access risk ;
- privacy risk ;
- audit-readiness context ;
- human-review requirement.

Il interdit de certifier automatiquement :

- conformité RGPD ;
- conformité légale ;
- conformité ISO ;
- posture sécurité ;
- autorisation de traitement de données personnelles.

C'est une base forte pour le Domain Pack.

## 4. Data governance

La spec Data Governance est explicitement `advisory-only`.

Elle peut définir :

- futurs champs de packets ;
- checklists ;
- labels de scope ;
- evidence refs.

Elle ne peut pas :

- approuver un traitement ;
- écrire en mémoire ;
- écrire dans le graphe ;
- exécuter un outil ;
- contourner X108.

## 5. RGPD / ISO readiness

Le boundary RGPD existant fait plusieurs distinctions essentielles :

```text
GDPR_ready != GDPR_compliant_legal
ISO27001_READY != ISO27001_CERTIFIED
DPA_template != DPA_signed
legal_template != validated_legal_advice
```

Il prévoit aussi :

- registre de traitement ;
- minimisation ;
- rétention ;
- human gate ;
- audit légal avant certaines validations.

Ces éléments peuvent devenir de la sémantique du Domain Pack, mais leurs claims doivent rester strictement bornés.

## 6. Legal-grade audit

Une ancienne spec décrit une cible d'export tiers-vérifiable comprenant :

- manifest ;
- policy ;
- traces ;
- signed tickets ;
- replay ;
- violations ;
- Merkle root ;
- signatures ;
- report.

Cette spec est marquée `À_FORMALISER_OU_À_PROUVER`.

Elle doit donc être lue comme **direction de conception**, pas comme fonctionnalité déjà garantie.

## 7. Regulatory mapping

La spec EU/FR est `FORMALISÉ_À_VALIDER`.

Elle contient des formulations ambitieuses historiques.

Le Domain Pack ne doit pas reprendre comme faits les affirmations de conformité “par construction” tant qu'une validation juridique externe n'existe pas.

## 8. Point de branchement cible

```text
law / policy / compliance source
→ scope extraction
→ risk / obligation / review requirement
→ LegalCompliance DomainSignal
→ evidence refs
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ human/legal review gate si requis
→ receipt / audit export
```

## 9. Non-souveraineté

```text
LEGAL TEMPLATE != LEGAL ADVICE
READINESS != CERTIFICATION
COMPLIANCE SIGNAL != LEGAL VERDICT
POLICY != AUTHORITY
DOMAIN != AUTHORITY
KX108_ONLY
```

## 10. État réel du pack

Malgré le corpus transversal :

- `source_type: none` ;
- `extensions: []` ;
- `sources.yaml: NOT_YET_DEFINED` ;
- object map absent ;
- runtime UDIP absent.

La priorité est donc de **raccorder proprement ce corpus existant**, pas d'inventer une nouvelle couche juridique.

## 11. Sources

- [Domain Concept Source Audit](../../planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md)
- [RGPD Compliance Scope Guard](../../runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md)
- [Compliance Scope Guard Spec](../../runtime_contracts/compliance_data_governance_spec/specs/COMPLIANCE_SCOPE_GUARD_SPEC.md)
- [UDIP V0](../../docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md)

## 12. Prochaine étape

Créer une taxonomie minimale :

```text
compliance_requirement
processing_risk
retention_rule
access_rule
review_requirement
claim_scope
legal_evidence_ref
```

sans transformer cette taxonomie en autorité juridique.
