# Theorem Dependency Graph — P72

**Statut :** P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY  
**Date :** 2026-06-07

Ce document décrit les dépendances entre invariants et théorèmes. Un invariant A « dépend de » B si sa garantie repose sur celle de B.

---

## Graphe de dépendances

```
DETERMINISM (E2, D1, aggregate4_unanimous, no_two_distinct_supermajorities_4)
    |
    +---> NO_ACT_BEFORE_TAU (X108_no_act_before_tau, canonicalize_preserves_nonneg)
    |         |
    |         +---> HOLD_BEFORE_TAU (+ X108_kernel_never_blocks)
    |         |
    |         +---> NEGATIVE_CLOCK_SKEW_TO_HOLD (skew_negative_implies_hold)
    |         |
    |         +---> IRREVERSIBLE_ACTION_DELAY (X108_irreversible_after_tau_equals_base)
    |
    +---> REVERSIBLE_ACTION_BASELINE (X108_reversible_equals_base)
    |
    +---> THRESHOLD_CONSERVATION (aggregate4_fail_closed, no_two_distinct_supermajorities_4, _aux)
    |         |
    |         +---> BLOCK_PRIORITY_OVER_HOLD_ALLOW (aggregate4_fail_closed, G3)
    |         |
    |         +---> HOLD_PRIORITY_OVER_ALLOW (X108_no_act_before_tau, aggregate4_act, G3)
    |
    +---> GUARD_X108_FINAL_AUTHORITY (X108_kernel_never_blocks)
    |         |
    |         +---> SIGMA_POST_GUARD_VETO_ONLY (SPEC — P56D)
    |         |
    |         +---> KX108_ONLY_DECISION_AUTHORITY (SPEC — architectural)
    |                   |
    |                   +---> NO_PERIPHERY_DECISION_AUTHORITY (Python)
    |                   |         |
    |                   |         +---> NO_GRAPHITI_WRITE (Python P70)
    |                   |         |
    |                   |         +---> NO_MEMORY_WRITE_WITHOUT_GATE (Python P66)
    |                   |         |
    |                   |         +---> BUS_PROPOSE_ONLY (Python P61)
    |                   |
    |                   +---> DRY_RUN_ONLY_ADAPTERS (Python P71)
    |                             |
    |                             +---> SOURCE_PACK_NOT_CANON_BY_EXISTENCE (Python P71)
    |                             |
    |                             +---> NETWORK_EGRESS_REVIEW_REQUIRED (Python P70)
    |
    +---> NO_KERNEL_MUTATION_FROM_PERIPHERY (G1)
              |
              +---> ARCHIVE_NOT_RUNTIME (G2 MIXED)
```

---

## Invariants racine (pas de dépendances amont)

| Invariant | Justification |
|---|---|
| DETERMINISM | Base axiomatique du noyau — E2, D1 fondateurs |
| PYTHON_TESTED_NOT_LEAN_PROVEN | Meta-invariant documentaire — aucune dépendance |

---

## Invariants terminaux (pas de dépendances aval dans ce graph)

| Invariant | Couche |
|---|---|
| NEGATIVE_CLOCK_SKEW_TO_HOLD | OS0_KERNEL |
| REVERSIBLE_ACTION_BASELINE | OS0_KERNEL |
| IRREVERSIBLE_ACTION_DELAY | OS0_KERNEL |
| SIGMA_POST_GUARD_VETO_ONLY | OS2_SIGMA |
| NO_GRAPHITI_WRITE | OS4_PERIPHERY |
| NO_MEMORY_WRITE_WITHOUT_GATE | OS4_PERIPHERY |
| BUS_PROPOSE_ONLY | OS4_PERIPHERY |
| SOURCE_PACK_NOT_CANON_BY_EXISTENCE | OS5_SOURCES |
| NETWORK_EGRESS_REVIEW_REQUIRED | OS7_NETWORK |
| ROUTE_AUTH_BOUNDARY | OS6_ROUTES |
| ARCHIVE_NOT_RUNTIME | OS3_AUDIT_PROOF |

---

## Conséquence architecturale

La chaîne critique est :

```
DETERMINISM -> NO_ACT_BEFORE_TAU -> HOLD_BEFORE_TAU -> GUARD_X108_FINAL_AUTHORITY
```

Briser DETERMINISM invalide tous les invariants aval. C'est le nœud le plus critique du graphe.

---

## Invariants bloquant des extensions

Les invariants suivants bloquent activement les modifications de couches supérieures :

| Invariant | Couches bloquées |
|---|---|
| DETERMINISM | OS1_GUARD, OS2_SIGMA, OS4_PERIPHERY |
| NO_ACT_BEFORE_TAU | OS1_GUARD, OS4_PERIPHERY, OS7_NETWORK |
| GUARD_X108_FINAL_AUTHORITY | OS1_GUARD, OS2_SIGMA |
| THRESHOLD_CONSERVATION | OS0_KERNEL |
| KX108_ONLY_DECISION_AUTHORITY | OS0_KERNEL, OS1_GUARD, OS2_SIGMA, OS4_PERIPHERY |
