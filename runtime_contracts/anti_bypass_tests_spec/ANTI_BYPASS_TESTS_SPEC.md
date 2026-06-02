# ANTI_BYPASS_TESTS_SPEC
# runtime_contracts/anti_bypass_tests_spec/
# Plan 3 P4 — Spec documentaire uniquement — NO TEST EXECUTION
# Date: 2026-06-02
# Status: ANTI_BYPASS_SPEC_ONLY / NO_RUNTIME_EXECUTION / NO_TEST_EXECUTION

---

## 1. Purpose

Ce document spécifie la structure documentaire des futurs tests anti-bypass d'Obsidia X-108.

Un test anti-bypass vérifie qu'aucune source périphérique, aucun pack, aucune couche
NPL/Atlas/Cognitive/RSSI/RGPD, et aucun module de contexte ne peut contourner X-108
pour déclencher une action, émettre un verdict, ou prétendre à une autorité décisionnelle.

Ces tests sont **documentaires uniquement** en P4.
Aucun test n'est exécutable à ce stade.

---

## 2. Status

```
Status:                     ANTI_BYPASS_SPEC_ONLY
Test execution:             NO
Python files:               NO
Runtime execution:          NO
Packages:                   NO
World action:               NO
Pack imports:               NO (F03/F06/F07 requis)
Commit:                     NO
Push:                       NO
runtime_allowed_now:        false — TOUTES les matrices
```

---

## 3. Scope

Les tests anti-bypass couvrent toutes les couches qui pourraient tenter de contourner X-108 :

| Couche | Pack/Source | Boundary associée |
|--------|------------|-------------------|
| External Signals | RSSI_EXTERNAL_SIGNALS_PATCH_V1 | EXTERNAL_SIGNALS_SIGNAL_ONLY |
| NPL | specs/12_NARRATIVE_PROVENANCE_LAYER/ | NPL_ADVISORY_ONLY |
| Audio/Entropy | specs/03_ENTROPY_DISCIPLINE/ | AUDIO_ENTROPY_ADVISORY_ONLY |
| P107/P161 | specs/03_ENTROPY_DISCIPLINE/ | P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY |
| Graphiti | periphery (readonly) | READONLY_CONTEXT_ONLY |
| Brody | periphery (readonly) | READONLY_CONTEXT_ONLY |
| Cognitive | COGNITIVE_REINTEGRATION (COPIED_READONLY) | COGNITIVE_REINTEGRATION_ADVISORY_ONLY |
| Atlas | BRANCHABLE_ATLAS (COPIED_READONLY) | ATLAS_READONLY_ADVISORY_ONLY |
| RSSI | RSSI_SECURITY (COPIED_READONLY) | RSSI_EVIDENCE_ONLY |
| RGPD | RGPD_ISO (COPIED_READONLY) | RGPD_COMPLIANCE_SCOPE_GUARD |
| XLSX backlog | OBSIDIA_IMPLEMENTATION_PLAN | NO_IMPORT_AS_WRITE_AUTHORITY |
| Source .py | Dans les zips F78B | DO_NOT_IMPORT_RUNTIME |

---

## 4. Non-executable status

P4 crée uniquement :
- Fichiers `.md` documentaires
- Zéro fichier `.py`
- Zéro test exécutable
- Zéro runner pytest / unittest
- Zéro fixture runtime

Les futurs tests exécutables seront créés dans `tests/anti_bypass/` uniquement après :
1. F78B SOURCE_PACKS_DEEP_DIFF validé ✅ (fait)
2. F78C XLSX réconcilié ✅ (fait)
3. Plan 3 P4 Anti-bypass Spec validé (ce run)
4. Gate humaine explicite sur les specs P4
5. Chaque pack concerné passé par F03/F06/F07 selon le cas

---

## 5. Threat model

### Sources de bypass identifiées

```
DIRECT (tentative d'action sans X108) :
  T01 — Peripheral emits ACT directly
  T02 — Peripheral emits ALLOW/HOLD/BLOCK directly
  T03 — X108 gateway skipped entirely

CONTEXT AUTHORITY CLAIM (contexte prétend à la décision) :
  T04 — ContextPacket claims final verdict
  T05 — PeripheralSignalPacket claims decision authority
  T06 — External Signals overrides X108 decision

DOMAIN OVERREACH (domaine spécialisé prétend à l'autorité générale) :
  T07 — NPL claims diagnostic/moral/final verdict
  T08 — P107/P161 claims Lean-proven theorem authority
  T09 — Audio/Entropy claims certified physical law
  T10 — Cognitive agent claims autonomous action
  T11 — Atlas scenario triggers runtime action
  T12 — RSSI control attempts automatic block
  T13 — RGPD readiness claims compliance certification

PIPELINE BYPASS (ordre de la chaîne violé) :
  T14 — Tool-call before DecisionTicket
  T15 — Memory write before X108 gate
  T16 — Graphiti/Brody write from readonly layer
  T17 — RuntimeAdmissionContract skipped
  T18 — OS3EvidenceTicket missing for CRITICAL

SOURCE INTEGRITY BYPASS (source non auditée utilisée) :
  T19 — Zip pack imported without F78B audit
  T20 — XLSX target_path treated as write authorization
  T21 — .py from source pack imported into runtime
  T22 — packages/ path recreated
  T23 — .runtime_freezes treated as live state
  T24 — Unknown source status passes admission

TEMPORAL/STATE BYPASS :
  T25 — Stale temporal context accepted as valid
  T26 — Replay attack passes anti-replay horizon
  T27 — fail_open behavior accepted as default
```

---

## 6. Bypass classes

| Class | Code | Description | Criticité |
|-------|------|-------------|-----------|
| DIRECT_ACT | T01-T03 | Action ou décision sans X108 | CRITICAL |
| CONTEXT_AUTHORITY | T04-T06 | Contexte prétend à souveraineté | CRITICAL |
| DOMAIN_OVERREACH | T07-T13 | Domaine spécialisé sort de son scope | HIGH |
| PIPELINE_BYPASS | T14-T18 | Ordre de chaîne violé | HIGH |
| SOURCE_INTEGRITY | T19-T24 | Source non auditée utilisée | HIGH |
| TEMPORAL | T25-T27 | Contexte temporel compromis | MEDIUM |

---

## 7. Required contracts

| Contrat | Rôle dans les tests |
|---------|---------------------|
| IntentEnvelope.contract.md | Vérifier structure avant X108 |
| ContextPacket.contract.md | Vérifier readonly / advisory |
| PeripheralSignalPacket.contract.md | Vérifier non-souveraineté |
| DecisionTicket.contract.md | Vérifier X108 seul producteur |
| OS3EvidenceTicket.contract.md | Vérifier trail de preuve |
| BoundaryContract.contract.md | Vérifier droits modules |
| RuntimeAdmissionContract.contract.md | Vérifier critères admission |

---

## 8. Required boundaries

Toutes les 13 boundaries P0+P1 sont requises pour les tests anti-bypass :

| Boundary | Classe de tests |
|----------|----------------|
| NO_ACT_FROM_PERIPHERY | T01, T10, T11 |
| X108_GATEWAY_REQUIRED | T02, T03, T06 |
| FAIL_CLOSED_PRIORITY | T27 |
| READONLY_CONTEXT_ONLY | T04, T15, T16 |
| EXTERNAL_SIGNALS_SIGNAL_ONLY | T06, T25, T26 |
| NPL_ADVISORY_ONLY | T07 |
| P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY | T08 |
| AUDIO_ENTROPY_ADVISORY_ONLY | T09 |
| COGNITIVE_REINTEGRATION_ADVISORY_ONLY | T10 |
| ATLAS_READONLY_ADVISORY_ONLY | T11 |
| RSSI_EVIDENCE_ONLY | T12 |
| RGPD_COMPLIANCE_SCOPE_GUARD | T13 |
| NO_PACKAGES_RUNTIME_BOUNDARY | T22 |

---

## 9. Test families

| Famille | ID | Tests futurs | Contrat principal |
|---------|----|-------------|-------------------|
| DIRECT_BYPASS | TB-01 à TB-10 | Tenter ACT / décision directe | DecisionTicket |
| CONTEXT_SOVEREIGNTY | TB-11 à TB-20 | ContextPacket / PeripheralSignal prétend à l'autorité | ContextPacket |
| DOMAIN_OVERREACH | TB-21 à TB-35 | NPL/P107/Audio/RSSI/RGPD/Cognitive/Atlas | BoundaryContract |
| PIPELINE_ORDER | TB-36 à TB-45 | Ordre de la chaîne | RuntimeAdmissionContract |
| SOURCE_INTEGRITY | TB-46 à TB-55 | Source non auditée | BoundaryContract |
| TEMPORAL | TB-56 à TB-60 | Contexte temporel | OS3EvidenceTicket |

Total : 60 tests documentaires minimum

---

## 10. Expected future test artifacts

À créer après gate humaine + F03/F06/F07 :

```
tests/anti_bypass/
  test_direct_bypass.py          → TB-01 à TB-10
  test_context_sovereignty.py    → TB-11 à TB-20
  test_domain_overreach.py       → TB-21 à TB-35
  test_pipeline_order.py         → TB-36 à TB-45
  test_source_integrity.py       → TB-46 à TB-55
  test_temporal_bypass.py        → TB-56 à TB-60
  conftest.py                    → fixtures communes
  README.md                      → instructions
```

Ces fichiers ne sont PAS créés en P4.

---

## 11. Forbidden runtime claims

```
❌ "Les tests P4 sont exécutés"
❌ "pytest P4 a passé"
❌ "Les packs sont importés après P4"
❌ "P4 valide le runtime"
❌ "P4 prouve qu'aucun bypass n'existe"
❌ "La spec P4 = une suite de tests validés"
❌ "External Signals autorise X108 car la spec P4 l'inclut"

✅ "P4 = spec documentaire des tests futurs"
✅ "P4 définit les scénarios et critères"
✅ "Les tests seront créés et exécutés après F03/F06/F07 + gate humaine"
✅ "P4 garantit que les critères anti-bypass sont définis avant l'import"
```

---

## 12. Failure handling

```
∀ bypass attempt b : b → fail_closed
∀ bypass attempt b : b → no_act
∀ bypass attempt b : b → requires_x108_review
∀ bypass attempt b : b ↛ allow_by_default
Priorité : BLOCK > HOLD > ALLOW
```

---

## 13. Claim-scope

| Composant | Claim autorisé en P4 |
|-----------|---------------------|
| P4 spec | ANTI_BYPASS_SPEC_ONLY — documentation future |
| Tests futurs | FUTURE_EXECUTABLE — après gate humaine |
| Packs | COPIED_READONLY — selon statut F78B |
| RSSI/RGPD | EVIDENCE_ONLY / COMPLIANCE_SCOPE_GUARD |
| NPL | ADVISORY_ONLY |
| P107/P161 | PYTHON_SPEC_NOT_LEAN_PROVEN |
| X108 | Seul droit de passage — invariant D1 |

---

## 14. Future implementation gates

| Gate | Prérequis | Description |
|------|-----------|-------------|
| Tests P4 exécutables | P4 Spec ✅ + gate humaine + F78B + F78C | Créer tests/anti_bypass/ |
| F07 (Cognitive) | F78B ✅ + F78C ✅ | Import Cognitive docs |
| F03 (RSSI+RGPD) | F78B ✅ + F78C ✅ | Import RSSI+RGPD docs |
| F06 (Atlas) | F78B ✅ + F78C ✅ | Import Atlas docs |
| P5 (OS3 Evidence) | P4 Spec ✅ | Spec OS3 dry-run |
| P6 (Graphiti/Brody/NPL wrappers) | P5 ✅ | Spec wrappers readonly |

---

## 15. Relation à F78B/F78C

F78B a audité les zips et confirmé :
- 57 .py dans zips → DO_NOT_IMPORT_RUNTIME (tests TB-46/TB-51 couvrent ce vecteur)
- .pytest_cache → QUARANTINE (tests TB-52 couvrent ce vecteur)
- .runtime_freezes → ARCHIVE_ONLY

F78C a réconcilié le XLSX et confirmé :
- 8 lignes packages/ → COLLISION_BLOCKING (tests TB-53 couvrent ce vecteur)
- XLSX target_path ≠ write authorization (tests TB-54 couvrent ce vecteur)

---

## 16. Tests required later (après gate humaine)

Voir `matrices/ANTI_BYPASS_TEST_MATRIX.md` pour les 60+ tests documentaires.

---

## 17. Proof expected later

```
Lean proofs attendus (post-P5) :
  periphery_non_sovereign_proof
  x108_sole_decision_authority_proof
  fail_closed_aggregate4_proof
  no_act_before_tau_proof

TLA+ specs attendues (post-P5) :
  AntiBypassInvariant.tla
  PeripheryNonSovereignty.tla
  FailClosedProperty.tla
```
