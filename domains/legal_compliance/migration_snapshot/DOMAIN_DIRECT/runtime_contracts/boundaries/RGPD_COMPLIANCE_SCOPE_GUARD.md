# RGPD_COMPLIANCE_SCOPE_GUARD
# runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md
# Plan 3 P1 — Gap reporté depuis P0
# Status: CONTRACT_SKELETON_ONLY
# Source: _source_packs/.../raw/OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip
# Pack status: COPIED_READONLY — 280 fichiers — 8 doublons — NON importé dans specs/ — à traiter en F03/F10

---

## 1. Boundary Statement

```
RGPD ISO Readiness = READINESS / PRE-AUDIT / COMPLIANCE PREPARATION
RGPD ISO ≠ CONFORMITÉ FINALE
RGPD ISO ≠ CERTIFICATION LÉGALE
∀ template t : t ≠ contrat validé avocat/DPO
ISO27001_READY ≠ ISO27001_CERTIFIED
SecNumCloud_target ≠ SecNumCloud_certified
GDPR_ready ≠ GDPR_compliant_legal
∀ donnée personnelle d : d ↛ traitement sans registre + minimisation + rétention
legal_template ≠ avis juridique validé
DPA_template ≠ DPA signé
data_governance → doit contraindre Graphiti/Brody/NPL/Education plus tard
∀ output RGPD : output ∈ {OS3EvidenceTicket, BoundaryContract, RuntimeAdmissionContract}
decision_authority = KX108_ONLY
```

---

## 2. Applies To

Pack : `OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip` (280 fichiers, ~3MB)

Contenu du pack (estimé) :
- RGPD readiness documentation (registre traitement, minimisation, rétention)
- ISO 27001 readiness checklist
- ISO 27701 privacy framework
- SecNumCloud target documentation
- Data Protection Agreement (DPA) templates
- Legal templates (mentions légales, CGU, politique de confidentialité)
- Data governance frameworks
- DPIA (Data Protection Impact Assessment) templates

Contraintes spécifiques :
- 8 doublons internes → résolution avant import (1 vrai doublon DPA_TEMPLATE.md, reste cross-pack)
- RSSI V1 présent dans ce pack → garder comme LEGACY_SOURCE_ONLY
- Sensibilité légale : templates ≠ avis juridique — claim-scope critique

---

## 3. Source Status

| Élément | Statut |
|---------|--------|
| Zip dans repo | ✅ `_source_packs/.../raw/` |
| Filelist extraite | ✅ `extracted_file_lists/` |
| 8 doublons résolus | ❌ EN ATTENTE — DPA_TEMPLATE.md = RICHER_VERSION_TO_KEEP |
| Importé dans specs/ | ❌ NON — à traiter en F03/F10 |
| Audité session | ✅ backlog audit + PLAN3_P0_INPUT_COVERAGE |
| Boundary dédiée P0 | ❌ NON — couvert par générique NO_ACT_FROM_PERIPHERY |
| Boundary dédiée P1 | ✅ CE FICHIER |
| Runtime branché | ❌ NON |
| Source status global | `COPIED_READONLY` |

---

## 4. Allowed

- Référencer RGPD readiness comme preuve documentaire dans OS3EvidenceTicket
- Créer un BoundaryContract exigeant compliance review avant admission de certains modules
- Créer un RuntimeAdmissionContract avec `required_proofs: ["RGPD_readiness_review"]`
- Produire un ContextPacket avec `source_layer="rgpd"`, `label="RGPD_SCOPE_GUARD_FUTURE"` advisory
- Contraindre les accès mémoire (Graphiti/Brody/Education) avec des règles data governance
- Permettre l'import futur du pack en `specs/rgpd_iso/` après audit F03/F10

---

## 5. Forbidden

```
❌ "conforme RGPD" — readiness ≠ conformité légale finale
❌ "certifié ISO" — readiness ≠ certification
❌ "prêt production" — templates ≠ documents validés
❌ "DPO validé" — DPA_template ≠ DPA signé
❌ "legal-ready" — legal_template ≠ avis juridique
❌ "SecNumCloud compliant" — SecNumCloud_target ≠ certification
❌ Traiter des données personnelles réelles sans registre de traitement
❌ Traiter des données personnelles sans minimisation et rétention définie
❌ Importer le pack sans résolution des 8 doublons
❌ Présenter les templates comme des contrats juridiquement valides
```

---

## 6. Failure Mode

| Situation | Comportement |
|-----------|-------------|
| "conforme RGPD" claim dans un rapport | `compliance_overclaim_flag` |
| Donnée personnelle sans registre de traitement | BLOCK — `RGPD_ART30_REQUIRED` |
| DPA_template utilisé comme contrat réel | `legal_false_claim_flag` |
| ISO27001_READY présenté comme ISO27001_CERTIFIED | `certification_overclaim_flag` |
| Label `RGPD_SCOPE_GUARD_FUTURE` manquant | `label_missing_flag` |

---

## 7. Required Contract Fields

- `source_layer: "rgpd"` dans ContextPacket si source = RGPD
- `label: "RGPD_SCOPE_GUARD_FUTURE"` obligatoire
- Référence RGPD dans RuntimeAdmissionContract : `required_proofs: ["RGPD_readiness_review"]`
- `human_gate_required: true` pour tout module traitant des données personnelles
- `claim_scope: "CLAIMABLE_SPEC_ONLY"` — jamais `CLAIMABLE_FORMAL` sans audit légal

---

## 8. Required Future Tests (F03/F10 / P2 après import)

- `test_rgpd_template_not_presented_as_legal_contract`
- `test_iso_ready_not_iso_certified`
- `test_personal_data_requires_treatment_register`
- `test_dpa_template_advisory_only`
- `test_secnumcloud_target_not_certified`

---

## 9. Proof Expectation

- Aucune preuve Lean pour RGPD actuellement
- Python tests après import F03/F10
- Audit humain légal requis avant toute preuve `VERIFIED` sur compliance

---

## 10. Claim-Scope

**Autorisé :**
- "Le pack RGPD ISO prépare la readiness — pas la conformité légale finale"
- "ISO27001_READY = préparation aux exigences ISO27001 — pas certification"
- "SecNumCloud target = objectif de qualification — pas label actif"
- "Les templates RGPD sont des modèles documentaires — validation légale requise"
- "Data governance framework contraint Graphiti/Brody en données personnelles"

**Interdit :**
- ❌ "conforme RGPD" — INTERDIT
- ❌ "certifié ISO" — INTERDIT
- ❌ "DPO validé" — INTERDIT
- ❌ "legal-ready" — INTERDIT
- ❌ "SecNumCloud compliant" — INTERDIT

---

## 11. Example Violation

```python
# VIOLATION dans un rapport public
report.add("Status: RGPD Compliant")  # ← OVERCLAIM — readiness ≠ conformité
report.add("ISO 27001 Certified")     # ← OVERCLAIM — pas de certification
```

---

## 12. Correct Handling

```python
# CORRECT dans un rapport
report.add("Status: RGPD Readiness V2 — pre-audit documentation. Legal validation required.")
report.add("ISO 27001 Readiness — checklist documentaire. Certification audit pending.")
```

---

## 13. Future Runtime Admission Conditions (F03/F10)

Avant de passer RGPD en `CONTRACT_READY` :
1. Résolution des 8 doublons (DPA_TEMPLATE.md → garder version plus riche)
2. Import du pack en `specs/rgpd_iso/` (F03/F10)
3. Audit claim-scope de chaque template (avocat/DPO review pour production)
4. Mapping data governance → Graphiti/Brody write boundaries
5. Tests : `test_personal_data_requires_treatment_register`
6. Gate humaine + légale avant tout usage en production

---

## 14. Relation To X-108

```
RGPD readiness → RuntimeAdmissionContract (required_proofs) → gate humaine
RGPD compliance review → OS3EvidenceTicket (evidence_type: "AUDIT_LOG") → advisory
data governance → BoundaryContract (can_write_memory = false par défaut) → X108 contrôle
Personal data access → IntentEnvelope (CRITICAL) → X108 gate → DecisionTicket
```

X-108 reste seul décideur. RGPD fournit des contraintes documentaires de readiness —
jamais des certifications ou des verdicts légaux.
