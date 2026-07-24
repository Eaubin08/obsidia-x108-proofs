# Invariant Graph Index — P72

**Statut :** P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY  
**Date :** 2026-06-07  
**Source :** docs/core_import/P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.json

Ce document est l'index de référence des 23 invariants d'Obsidia X-108.

---

## Lecture du statut formel

| Statut | Signification |
|---|---|
| `LEAN_PROVEN` | Théorème Lean 4 vérifié via `#print axioms` (sans axiomes non-standard) |
| `PYTHON_TESTED` | Couvert par tests pytest — comportement runtime validé, pas une preuve universelle |
| `SPEC_ONLY` | Contrainte architecturale documentée — aucune preuve formelle disponible |
| `DOC_ONLY` | Meta-règle documentaire — non testable directement |
| `MIXED_PROOF_STATUS` | Partiellement LEAN_PROVEN + PYTHON_TESTED |
| `UNPROVEN_REQUIRES_REVIEW` | Non couvert — revue obligatoire avant extension |

---

## Index complet — 23 invariants

| # | Invariant | Couche | Statut | Risque si brisé |
|---|---|---|---|---|
| 1 | DETERMINISM | OS0_KERNEL | LEAN_PROVEN | CRITICAL |
| 2 | NO_ACT_BEFORE_TAU | OS0_KERNEL | LEAN_PROVEN | CRITICAL |
| 3 | HOLD_BEFORE_TAU | OS0_KERNEL | LEAN_PROVEN | CRITICAL |
| 4 | IRREVERSIBLE_ACTION_DELAY | OS0_KERNEL | LEAN_PROVEN | CRITICAL |
| 5 | REVERSIBLE_ACTION_BASELINE | OS0_KERNEL | LEAN_PROVEN | HIGH |
| 6 | NEGATIVE_CLOCK_SKEW_TO_HOLD | OS0_KERNEL | LEAN_PROVEN | HIGH |
| 7 | THRESHOLD_CONSERVATION | OS0_KERNEL | LEAN_PROVEN | CRITICAL |
| 8 | BLOCK_PRIORITY_OVER_HOLD_ALLOW | OS0_KERNEL | LEAN_PROVEN | CRITICAL |
| 9 | HOLD_PRIORITY_OVER_ALLOW | OS0_KERNEL | LEAN_PROVEN | CRITICAL |
| 10 | KX108_ONLY_DECISION_AUTHORITY | OS0_KERNEL | SPEC_ONLY | CRITICAL |
| 11 | GUARD_X108_FINAL_AUTHORITY | OS1_GUARD | LEAN_PROVEN | CRITICAL |
| 12 | SIGMA_POST_GUARD_VETO_ONLY | OS2_SIGMA | SPEC_ONLY | HIGH |
| 13 | NO_KERNEL_MUTATION_FROM_PERIPHERY | OS3_AUDIT_PROOF | LEAN_PROVEN | CRITICAL |
| 14 | ARCHIVE_NOT_RUNTIME | OS3_AUDIT_PROOF | MIXED_PROOF_STATUS | HIGH |
| 15 | PYTHON_TESTED_NOT_LEAN_PROVEN | OS3_AUDIT_PROOF | DOC_ONLY | MEDIUM |
| 16 | NO_PERIPHERY_DECISION_AUTHORITY | OS4_PERIPHERY | PYTHON_TESTED | CRITICAL |
| 17 | NO_GRAPHITI_WRITE | OS4_PERIPHERY | PYTHON_TESTED | HIGH |
| 18 | NO_MEMORY_WRITE_WITHOUT_GATE | OS4_PERIPHERY | PYTHON_TESTED | HIGH |
| 19 | BUS_PROPOSE_ONLY | OS4_PERIPHERY | PYTHON_TESTED | HIGH |
| 20 | DRY_RUN_ONLY_ADAPTERS | OS5_SOURCES | PYTHON_TESTED | HIGH |
| 21 | SOURCE_PACK_NOT_CANON_BY_EXISTENCE | OS5_SOURCES | PYTHON_TESTED | MEDIUM |
| 22 | ROUTE_AUTH_BOUNDARY | OS6_ROUTES | PYTHON_TESTED | HIGH |
| 23 | NETWORK_EGRESS_REVIEW_REQUIRED | OS7_NETWORK | PYTHON_TESTED | HIGH |

---

## Répartition par couche

| Couche | Invariants | LEAN_PROVEN |
|---|---:|---:|
| OS0_KERNEL | 9 | 9* |
| OS1_GUARD | 1 | 1 |
| OS2_SIGMA | 1 | 0 |
| OS3_AUDIT_PROOF | 3 | 1 (+1 MIXED) |
| OS4_PERIPHERY | 4 | 0 |
| OS5_SOURCES | 2 | 0 |
| OS6_ROUTES | 1 | 0 |
| OS7_NETWORK | 1 | 0 |

*KX108_ONLY_DECISION_AUTHORITY est SPEC_ONLY bien que sur OS0_KERNEL.

---

## Fichiers de spec liés

- `THEOREM_TO_ARCHITECTURE_MAP.md` — mapping théorème → couche/composant
- `THEOREM_DEPENDENCY_GRAPH.md` — dépendances entre invariants
- `INVARIANT_TO_LAYER_MAP.md` — mapping invariant → couche détaillée
- `INVARIANT_TO_EXTENSION_RULES.md` — règles d'extension par invariant
- `LEAN_PROVEN_VS_PYTHON_TESTED_MATRIX.md` — matrice de comparaison
- `PERIPHERY_STABILIZATION_RULES.md` — règles de stabilisation périphérie
- `WHY_EXTENSIONS_DO_NOT_BREAK_X108.md` — argument de sécurité des extensions
- `FUTURE_FORMAL_TARGETS.md` — cibles de preuve future (P73+)
- `LEAN_PROVEN_VS_FUTURE_TARGETS_DELTA.md` — delta preuve vs cibles
