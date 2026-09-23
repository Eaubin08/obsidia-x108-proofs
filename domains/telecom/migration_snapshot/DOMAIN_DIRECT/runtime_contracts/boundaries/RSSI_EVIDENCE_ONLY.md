# RSSI_EVIDENCE_ONLY
# runtime_contracts/boundaries/RSSI_EVIDENCE_ONLY.md
# Plan 3 P1 — Gap reporté depuis P0
# Status: CONTRACT_SKELETON_ONLY
# Source: _source_packs/.../raw/OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip
# Pack status: COPIED_READONLY — 167 fichiers — NON importé dans specs/ — à traiter en F03

---

## 1. Boundary Statement

```
RSSI Security Pack = EVIDENCE / CONTROLS / RISK / THREAT_MODEL / AUDIT_PRESENTATION
∀ contrôle de sécurité c : c ↛ correction automatique
∀ contrôle c : c ↛ BLOCK seul
∀ contrôle c : c ↛ ALLOW seul
∀ threat_model t : t ↛ protection garantie effective
∀ security_case s : s ↛ test exécuté
∀ output RSSI : output ∈ {OS3EvidenceTicket, BoundaryContract, ContextPacket}
RSSI posture ≠ certification réelle
threat_model ≠ protection effective
security_case ≠ test en production
controls_map ≠ couverture garantie
decision_authority = KX108_ONLY
```

---

## 2. Applies To

Pack : `OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip` (167 fichiers, ~2MB)

Contenu du pack (estimé) :
- Security posture présentation (état de la posture de sécurité)
- Controls mapping (cartographie des contrôles)
- Risk assessment (évaluation des risques)
- Threat models (modèles de menace)
- Audit narrative (narration d'audit)
- Security evidence (preuves de sécurité)
- Incident response candidates (candidats de réponse aux incidents)

Contraintes spécifiques :
- "RSSI posture ≠ certification réelle" — claim-scope critique
- Security cases = futurs tests adversariaux, pas des tests exécutés
- Threat model = cartographie des risques, pas une protection effective

---

## 3. Source Status

| Élément | Statut |
|---------|--------|
| Zip dans repo | ✅ `_source_packs/.../raw/` |
| Filelist extraite | ✅ `extracted_file_lists/` |
| Importé dans specs/ | ❌ NON — à traiter en F03 |
| Audité session | ✅ backlog audit + PLAN3_P0_INPUT_COVERAGE |
| Boundary dédiée P0 | ❌ NON — couvert par générique NO_ACT_FROM_PERIPHERY |
| Boundary dédiée P1 | ✅ CE FICHIER |
| Runtime branché | ❌ NON |
| Source status global | `COPIED_READONLY` |

---

## 4. Allowed

- Référencer RSSI evidence dans un OS3EvidenceTicket (preuves d'audit, contrôles, risk assessment)
- Créer un BoundaryContract pour les modules de sécurité référençant les contrôles RSSI
- Produire un ContextPacket avec `source_layer="rssi"`, `label="RSSI_EVIDENCE_ONLY_FUTURE"` en advisory
- Référencer le threat model pour enrichir les reason_codes d'un DecisionTicket X-108
- Permettre l'import futur du pack en `specs/rssi_security/` après audit F03

---

## 5. Forbidden

```
❌ "RSSI pack sécurise automatiquement"
❌ "tous les contrôles sont certifiés"
❌ "threat model = protection effective"
❌ "security cases = tests exécutés en production"
❌ "RSSI peut bypass X108"
❌ Les contrôles RSSI produisent BLOCK directement
❌ Les contrôles RSSI produisent ALLOW directement
❌ Clamer compliance sans audit humain validé
❌ Présenter threat model sans sa date de version
❌ Importer le pack sans audit claim-scope F03
```

---

## 6. Failure Mode

| Situation | Comportement |
|-----------|-------------|
| Contrôle RSSI émet BLOCK direct | Reject → fail_closed — X108 décide |
| `threat_model = protection effective` claim | `overauthority_flag` |
| `security_case = test exécuté` claim | `false_claim_flag` |
| Label `RSSI_EVIDENCE_ONLY_FUTURE` manquant | `label_missing_flag` |
| OS3EvidenceTicket RSSI sans `verification_status` | `unverified_evidence_flag` |

---

## 7. Required Contract Fields

- `source_layer: "rssi"` dans ContextPacket si source = RSSI
- `label: "RSSI_EVIDENCE_ONLY_FUTURE"` obligatoire
- Référence RSSI dans OS3EvidenceTicket : `evidence_type: "AUDIT_LOG"` ou `"HASH_CHAIN"`
- `verification_status` obligatoire sur toute preuve RSSI référencée

---

## 8. Required Future Tests (F03 / P2 après import)

- `test_rssi_no_auto_remediation`
- `test_rssi_threat_model_advisory_only`
- `test_rssi_evidence_in_os3ticket`
- `test_rssi_no_block_without_x108`
- `test_rssi_claim_scope_not_certified`

---

## 9. Proof Expectation

- Aucune preuve Lean pour RSSI actuellement
- Python tests après import F03
- Référencement dans OS3EvidenceTicket comme preuve d'audit (non décisionnelle)

---

## 10. Claim-Scope

**Autorisé :**
- "Le pack RSSI Security fournit des éléments de preuve d'audit advisory"
- "Les contrôles RSSI enrichissent le contexte de décision X-108 — jamais la décision"
- "threat_model = cartographie des risques — pas une garantie de protection"
- "security_cases = candidats de tests adversariaux futurs"

**Interdit :**
- ❌ "RSSI pack sécurise automatiquement" — INTERDIT
- ❌ "tous les contrôles sont certifiés" — INTERDIT
- ❌ "threat_model = protection effective" — INTERDIT
- ❌ "RSSI peut bypasser X108" — INTERDIT ABSOLU

---

## 11. Example Violation

```python
# VIOLATION
if rssi_controls.coverage > 0.95:
    return "ALLOW"  # ← RSSI ne peut pas émettre ALLOW
```

---

## 12. Correct Handling

```python
# CORRECT
rssi_evidence = OS3EvidenceTicket(
    evidence_type="AUDIT_LOG",
    source="rssi_security_pack_v1",
    hash=sha256(rssi_controls_report),
    verification_status="UNVERIFIED",  # honest — pas encore validé par audit humain
    claim_scope="CLAIMABLE_SPEC_ONLY"
)
# → attaché au DecisionTicket comme preuve advisory — X108 décide
```

---

## 13. Future Runtime Admission Conditions (F03)

Avant de passer RSSI en `CONTRACT_READY` :
1. Import du pack en `specs/rssi_security/` (F03)
2. Audit claim-scope des security cases et threat models
3. Mapping des contrôles vers OS3EvidenceTicket fields
4. Tests : `test_rssi_no_auto_remediation`
5. Gate humaine : audit humain RSSI requis avant toute preuve `VERIFIED`

---

## 14. Relation To X-108

```
RSSI evidence → OS3EvidenceTicket → linked_decision_ticket → X108 context
RSSI controls → BoundaryContract (reference) → module rights documentation
RSSI threat model → ContextPacket (advisory) → X108 decision context
```

X-108 reste seul décideur. RSSI fournit des preuves documentaires — jamais des verdicts.
