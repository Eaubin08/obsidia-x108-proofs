# PLAN3_P1_SPECIFIC_BOUNDARIES_REPORT
# runtime_contracts/reports/PLAN3_P1_SPECIFIC_BOUNDARIES_REPORT.md
# Date: 2026-06-02

---

## 1. Pourquoi ces 4 boundaries étaient nécessaires

Plan 3 P0 Input Coverage Audit (PLAN3_P0_INPUT_COVERAGE_PARTIAL) a identifié que
4 packs copiés en readonly dans `_source_packs/` n'avaient pas de boundary dédiée
dans les 9 boundaries P0. Les boundaries génériques (NO_ACT_FROM_PERIPHERY,
READONLY_CONTEXT_ONLY) les couvraient par défaut, mais sans spécificité suffisante.

**P0 Next Steps** listait explicitement ces 4 boundaries comme P1_REQUIRED :
- `COGNITIVE_REINTEGRATION_ADVISORY_ONLY`
- `ATLAS_READONLY_ADVISORY_ONLY`
- `RSSI_EVIDENCE_ONLY`
- `RGPD_COMPLIANCE_SCOPE_GUARD`

Ces 4 boundaries sont nécessaires car chaque pack a des claim-scope spécifiques
critiques qui ne peuvent pas être couverts par des formulations génériques.

---

## 2. Source — Plan3 P0 documents ayant déclenché cette phase

| Source | Passage clé |
|--------|------------|
| `runtime_contracts/reports/PLAN3_P0_NEXT_STEPS.md` | Section P1_REQUIRED_BOUNDARIES |
| `runtime_contracts/reports/PLAN3_P0_RUNTIME_CONTRACT_SKELETON_REPORT.md` | Section "Gaps reportés en P1" |
| `_source_discovery/PLAN3_P0_INPUT_COVERAGE_AUDIT_V1/PLAN3_P0_INPUT_COVERAGE_REPORT.md` | Tableau des 5 gros packs |
| `_source_packs/.../audits/OBSIDIA_V1_GENERAL_CANON_BACKLOG_AUDIT.md` | Packs 2-5 détaillés |

---

## 3. Les 4 Boundaries créées

### COGNITIVE_REINTEGRATION_ADVISORY_ONLY

| Aspect | Valeur |
|--------|--------|
| Fichier | `runtime_contracts/boundaries/COGNITIVE_REINTEGRATION_ADVISORY_ONLY.md` |
| Source pack | OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip (513 fichiers) |
| Phase XLSX | F07 — après Atlas + memory boundaries |
| Couverture contractuelle | ContextPacket (COGNITIVE_ADVISORY_FUTURE label), PeripheralSignalPacket |
| Source status | COPIED_READONLY |

### ATLAS_READONLY_ADVISORY_ONLY

| Aspect | Valeur |
|--------|--------|
| Fichier | `runtime_contracts/boundaries/ATLAS_READONLY_ADVISORY_ONLY.md` |
| Source pack | OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip (1738 fichiers, 36MB) |
| Phase XLSX | F06 — après Graphiti/Brody readonly |
| Contrainte spécifique | 92 doublons runtime_freeze → ARCHIVE_ONLY avant import |
| Source status | COPIED_READONLY |

### RSSI_EVIDENCE_ONLY

| Aspect | Valeur |
|--------|--------|
| Fichier | `runtime_contracts/boundaries/RSSI_EVIDENCE_ONLY.md` |
| Source pack | OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip (167 fichiers) |
| Phase XLSX | F03 — early OS3 audit/security surface |
| Couverture contractuelle | OS3EvidenceTicket, BoundaryContract |
| Source status | COPIED_READONLY |

### RGPD_COMPLIANCE_SCOPE_GUARD

| Aspect | Valeur |
|--------|--------|
| Fichier | `runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md` |
| Source pack | OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip (280 fichiers, 8 doublons) |
| Phase XLSX | F03/F10 — compliance + OS3 |
| Contrainte spécifique | 8 doublons → résolution avant import |
| Source status | COPIED_READONLY |

---

## 4. Mapping Pack → Boundary → Contrats

| Pack | Boundary P1 | Contrats couverts | Label obligatoire |
|------|------------|------------------|------------------|
| Cognitive Reintegration | COGNITIVE_REINTEGRATION_ADVISORY_ONLY | ContextPacket, PeripheralSignalPacket, RuntimeAdmissionContract | `COGNITIVE_ADVISORY_FUTURE` |
| Branchable Atlas | ATLAS_READONLY_ADVISORY_ONLY | ContextPacket, BoundaryContract | `ATLAS_READONLY_FUTURE` |
| RSSI Security | RSSI_EVIDENCE_ONLY | OS3EvidenceTicket, BoundaryContract, RuntimeAdmissionContract | `RSSI_EVIDENCE_ONLY_FUTURE` |
| RGPD ISO | RGPD_COMPLIANCE_SCOPE_GUARD | OS3EvidenceTicket, BoundaryContract, RuntimeAdmissionContract | `RGPD_SCOPE_GUARD_FUTURE` |

---

## 5. Ce que chaque boundary autorise

| Boundary | Outputs autorisés |
|----------|-----------------|
| COGNITIVE | ContextPacket advisory, PeripheralSignalPacket cognitif, world_action_candidate comme CONTEXTE |
| ATLAS | ContextPacket avec scénarios et cartes, scenario_candidate comme contexte |
| RSSI | OS3EvidenceTicket avec preuves d'audit, ContextPacket advisory |
| RGPD | OS3EvidenceTicket readiness, RuntimeAdmissionContract avec required_proofs RGPD |

---

## 6. Ce que chaque boundary interdit

| Boundary | Claims interdits critiques |
|----------|--------------------------|
| COGNITIVE | "agents décident", "consciousness prouvée", "AutoForge auto-promote", ACT direct |
| ATLAS | "Atlas branché runtime", "agents exécutables", "projets installés", ACT direct |
| RSSI | "sécurise automatiquement", "contrôles certifiés", "threat = protection", bypass X108 |
| RGPD | "conforme RGPD", "certifié ISO", "DPO validé", "SecNumCloud compliant" |

---

## 7. Claim-scope locks — Récapitulatif

```
COGNITIVE : source_status = COPIED_READONLY → claim_scope = CLAIMABLE_SPEC_ONLY
            Jamais : CLAIMABLE_FORMAL avant audit F07 + tests + gate humaine

ATLAS : source_status = COPIED_READONLY → claim_scope = CLAIMABLE_SPEC_ONLY
        Jamais : runtime actif, agents exécutables, open-source installé

RSSI : source_status = COPIED_READONLY → claim_scope = CLAIMABLE_SPEC_ONLY
       Jamais : RSSI posture = certification, threat = protection, auto-remediation

RGPD : source_status = COPIED_READONLY → claim_scope = CLAIMABLE_SPEC_ONLY
       Jamais : conforme RGPD, certifié ISO, legal-ready, SecNumCloud compliant
```

---

## 8. Plan d'usage futur F03/F06/F07/F10

| Phase | Pack | Action post-boundary P1 |
|-------|------|------------------------|
| F03 | RSSI Security | Import specs/rssi_security/ → audit claim-scope → test_rssi_no_auto_remediation |
| F03/F10 | RGPD ISO | Résolution 8 doublons → import specs/rgpd_iso/ → test_rgpd_template_advisory |
| F06 | Branchable Atlas | Résolution 92 doublons runtime_freeze → import partiel specs/atlas/ → test_atlas_no_decision |
| F07 | Cognitive | Exclusion 20 QUARANTINE → import specs/cognitive_reintegration/ → test_cognitive_no_act |

**Condition commune à tous :** `RuntimeAdmissionContract` doit être satisfait avant import.

---

## 9. Total boundaries runtime_contracts/

| Phase | Boundaries | Total cumulé |
|-------|-----------|-------------|
| P0 | 9 boundaries génériques + dédiées | 9 |
| P1 (ce rapport) | +4 boundaries spécifiques | **13** |

Les 13 boundaries couvrent maintenant tous les packs audités et copiés.
