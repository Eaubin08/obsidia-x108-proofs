# PLAN3_P4_ANTI_BYPASS_TESTS_SPEC_REPORT
# runtime_contracts/anti_bypass_tests_spec/reports/
# Date: 2026-06-02
# Status: ANTI_BYPASS_SPEC_ONLY / NO_TEST_EXECUTION

---

## 1. Résumé

Plan 3 P4 crée la spec documentaire complète des futurs tests anti-bypass d'Obsidia X-108.
Aucun test n'est exécutable. Aucun fichier .py. Aucun runtime modifié. Aucun pack importé.

Ce P4 documente 51 scénarios de bypass, 60 tests futurs, 15 sources auditées, 25 failure modes,
et établit la matrice source-pack → boundary → test pour protéger X108 contre tout contournement.

---

## 2. Pourquoi P4 existe

F78B a confirmé que les zips sources contiennent des .py (57 fichiers) et des artefacts risqués.
F78C a confirmé que le XLSX est un plan de référence, pas une autorisation d'écriture.
Plan 3 P3 a établi le harness X108 théorique mais sans tests de non-contournement.

P4 répond à la question : comment vérifier demain qu'aucune couche ne bypasse X108 ?

---

## 3. Sources lues

| Source | Statut |
|--------|--------|
| runtime_contracts/contracts/* (7 contrats) | ✅ |
| runtime_contracts/boundaries/* (13 boundaries) | ✅ |
| runtime_contracts/x108_gateway_dry_run_harness/specs/X108_GATEWAY_DRY_RUN_HARNESS_SPEC.md | ✅ |
| runtime_contracts/x108_gateway_dry_run_harness/failure_modes/*.md | ✅ |
| _source_discovery/F78B_*/F78B_SOURCE_PACKS_DEEP_DIFF_REPORT.md | ✅ |
| _source_discovery/F78C_*/F78C_XLSX_RECONCILIATION_REPORT.md | ✅ |
| _source_discovery/F78C_*/F78C_XLSX_COVERAGE_GAPS.md | ✅ |

---

## 4. Fichiers créés

| Fichier | Contenu |
|---------|---------|
| `ANTI_BYPASS_TESTS_SPEC.md` | Spec principale (17 sections) |
| `scenarios/BYPASS_SCENARIO_CATALOG.md` | 51 scénarios en 20 familles |
| `matrices/ANTI_BYPASS_TEST_MATRIX.md` | 60 tests documentaires |
| `matrices/SOURCE_PACK_BYPASS_MATRIX.md` | 15 sources × bypass risk × tests |
| `failure_modes/ANTI_BYPASS_FAILURE_MODES.md` | 25 failure modes → fail_closed |
| `reports/PLAN3_P4_ANTI_BYPASS_TESTS_SPEC_REPORT.md` | Ce rapport |
| `reports/PLAN3_P4_SCOPE_VERIFICATION.md` | Vérification périmètre |
| `reports/PLAN3_P4_NEXT_STEPS.md` | P5→P7 + F07→F10 |

Total P4 : 8 fichiers

---

## 5. Test families

| Famille | IDs | Scénarios | Tests |
|---------|-----|-----------|-------|
| DIRECT_BYPASS | TB-01 → TB-10 | SC-01 à SC-03 | 10 |
| CONTEXT_SOVEREIGNTY | TB-11 → TB-20 | SC-07 à SC-12 | 10 |
| DOMAIN_OVERREACH | TB-21 → TB-35 | SC-13 à SC-31 | 15 |
| PIPELINE_ORDER | TB-36 → TB-45 | SC-33 à SC-40 | 10 |
| SOURCE_INTEGRITY | TB-46 → TB-55 | SC-41 à SC-51 | 10 |
| TEMPORAL | TB-56 → TB-60 | SC-11, SC-25 | 5 |

Total : 60 tests documentaires

---

## 6. Scenario catalog

51 scénarios en 20 familles couvrant :
- Tentatives d'ACT direct (3 scénarios)
- Tentatives ALLOW/HOLD/BLOCK direct (3)
- ContextPacket prétend à verdict (3)
- External Signals override (3)
- NPL verdict/diagnostic (3)
- P107/P161 Lean claim (3)
- Audio/Entropy law claim (2)
- Cognitive autonomy (3)
- Atlas runtime action (3)
- RSSI auto-block (3)
- RGPD certification (3)
- Tool-call avant ticket (2)
- Memory write avant gate (2)
- Graphiti/Brody write (2)
- Source inconnue (2)
- Zip sans F78B (2)
- XLSX write auth (2)
- .py import (3)
- packages/ recréé (2)
- RuntimeAdmissionContract skipped (2)

---

## 7. Test matrix

60 tests documentaires — tous `runtime_allowed_now=false`.
Voir `matrices/ANTI_BYPASS_TEST_MATRIX.md`.

Types de tests futurs :
- SCHEMA_VALIDATION (2)
- CONTRACT_VALIDATION (14)
- BOUNDARY_ASSERTION (21)
- DRY_RUN_HARNESS_CHECK (8)
- CLAIM_SCOPE_CHECK (10)
- SOURCE_PACK_GATE_CHECK (11)
- OS3_EVIDENCE_CHECK (4)
- X108_GATEWAY_CHECK (4)

---

## 8. Source pack bypass matrix

15 sources auditées — toutes `import_allowed_now=false` sauf External Signals (F04 partiel) et NPL (F04) :

| Source | Risk | Tests | Gate |
|--------|------|-------|------|
| External Signals | LOW | TB-17,20,43,57 | F04 DONE (partial) |
| NPL | LOW | TB-21,22 | F04 DONE |
| Audio/Entropy | MEDIUM | TB-25 | Advisory spec |
| P107/P161 | MEDIUM | TB-23,24 | Claim scope locked |
| Graphiti/Brody | MEDIUM | TB-09,10,15,35 | Readonly enforced |
| Cognitive | HIGH | TB-26,27,28 | F78B+F07 required |
| Atlas | HIGH | TB-29,30,51 | F78B+F06 required |
| RSSI | HIGH | TB-31,32,47,53 | F78B+F03 required |
| RGPD | HIGH | TB-33,34,48,54 | F78B+F03+F10 required |
| .py files | CRITICAL | TB-47,48 | DO_NOT_IMPORT_RUNTIME |
| .pytest_cache | CRITICAL | TB-50 | QUARANTINE |
| .runtime_freezes | HIGH | TB-51 | ARCHIVE_ONLY |
| packages/ | CRITICAL | TB-49 | BLOCKED absolu |
| XLSX | MEDIUM | TB-52 | Audit référence only |
| Raw markdowns | LOW | N/A | Indexation F78B |

---

## 9. Failure modes

25 failure modes — règle : `fail_closed / no_act / requires_x108_review / never_allow_by_default`
12 CRITICAL (BLOCK absolu) : direct_act_attempt, direct_decision_attempt, x108_gateway_skipped,
decision_ticket_forged, tool_call_before_ticket, memory_write_before_gate, graph_write_from_readonly,
external_signal_override, npl_verdict_attempt, python_file_import, packages_path_recreation, fail_open_detected

---

## 10. Ce qui est volontairement non créé

```
❌ tests/anti_bypass/*.py — PAS DE TESTS EXÉCUTABLES en P4
❌ conftest.py
❌ pytest fixtures
❌ runner scripts
❌ coverage reports
❌ exécutions CI/CD
```

---

## 11. Pourquoi ce ne sont pas des tests exécutables

P4 est SPEC_ONLY. Les fichiers .md décrivent des critères et scénarios.
Les tests exécutables seront créés dans `tests/anti_bypass/` après :
1. Gate humaine sur la spec P4
2. F07 (Cognitive) + F03 (RSSI/RGPD) + F06 (Atlas) selon le pack concerné
3. Plan 3 P5 OS3 Evidence validé
4. Lean proofs formels si requis

---

## 12. Pourquoi X108 reste seul droit de passage

```
D1_DETERMINISM : même input → même output
E2_NO_ACT : pas d'action sans décision explicite X108
aggregate4_fail_closed : BLOCK > HOLD > ALLOW — invariant absolu
C473 : wrapper_reauthoring_forbidden — loi de non-réautorisation

Même si tous les tests anti-bypass passent :
→ X108 reste la seule source de ALLOW/HOLD/BLOCK
→ Aucun test ne "débloque" les packs
→ Aucun test ne crée d'autorité périphérique
```

---

## 13. Relation F78B/F78C

F78B a identifié 57 .py dans les zips → TB-47, TB-48 couvrent ce vecteur.
F78B a identifié .pytest_cache → TB-50 couvre ce vecteur.
F78C a confirmé XLSX ≠ write authority → TB-52 couvre ce vecteur.
F78C a identifié 8 lignes packages/ → TB-49 couvre ce vecteur.

---

## 14. Gaps restants

| Gap | Phase |
|-----|-------|
| Tests exécutables anti-bypass | Après gate humaine + F03/F06/F07 |
| Lean proof periphery_non_sovereign | Post-P5 |
| TLA+ AntiBypassInvariant.tla | Post-P5 |
| Tests TB-47/48 (RSSI .py) | Après F03 |
| Tests TB-55 (Atlas .py) | Après F06 |
| Tests TB-26/27/28 (Cognitive) | Après F07 |

---

## 15. Verdict

```
PLAN3_P4_ANTI_BYPASS_TESTS_SPEC_READY
```
