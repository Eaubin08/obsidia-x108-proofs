# Theorem to Architecture Map — P72

**Statut :** P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY  
**Date :** 2026-06-07

Chaque théorème Lean 4 est mappé à la couche architecturale qu'il protège et aux invariants qu'il couvre.

---

## TemporalKernel.lean — `Obsidia.TemporalKernel`

### X108_no_act_before_tau
```
Si irr=true et elapsed<τ, alors decideX108 = HOLD
```
- **Couche :** OS0_KERNEL
- **Composant :** `decideX108` / `beforeTau`
- **Invariants :** NO_ACT_BEFORE_TAU, HOLD_BEFORE_TAU, KX108_ONLY_DECISION_AUTHORITY
- **Axiom-free :** oui (`#print axioms` vérifié)

### X108_after_tau_equals_base
```
Si Not (beforeTau τ elapsed irr = true), alors decideX108 = decision metrics theta
```
- **Couche :** OS0_KERNEL
- **Composant :** `decideX108`
- **Invariants :** IRREVERSIBLE_ACTION_DELAY, REVERSIBLE_ACTION_BASELINE

### X108_kernel_never_blocks
```
Not (decide3X108 τ metrics theta irr elapsed = Decision3.BLOCK)
```
- **Couche :** OS1_GUARD
- **Composant :** `decide3X108` / `liftDecision`
- **Invariants :** GUARD_X108_FINAL_AUTHORITY, HOLD_BEFORE_TAU, KX108_ONLY_DECISION_AUTHORITY
- **Note architecturale :** Guard X-108 ne peut jamais retourner BLOCK — autorité finale garantie.

### X108_reversible_equals_base
```
Pour irr=false, decideX108 τ metrics theta false elapsed = decision metrics theta
```
- **Couche :** OS0_KERNEL
- **Composant :** `decideX108` (branche irr=false)
- **Invariants :** REVERSIBLE_ACTION_BASELINE

### X108_irreversible_after_tau_equals_base
```
Pour irr=true et τ≤elapsed, decideX108 = decision metrics theta
```
- **Couche :** OS0_KERNEL
- **Composant :** `decideX108` (branche post-tau)
- **Invariants :** IRREVERSIBLE_ACTION_DELAY

---

## TemporalBridge.lean — `Obsidia.TemporalBridge`

### skew_negative_implies_hold
```
Si elapsed_raw i < 0 et irr=true et τ≥0 → decide_with_skew_handling = HOLD
```
- **Couche :** OS0_KERNEL
- **Composant :** `decide_with_skew_handling` / `canonicalize_elapsed`
- **Invariants :** NEGATIVE_CLOCK_SKEW_TO_HOLD, NO_ACT_BEFORE_TAU
- **Note :** Bridge entre les valeurs Int brutes et Nat du kernel. Protège contre les horloges corrompues.

### canonicalize_preserves_nonneg
```
canonicalize_elapsed e = Int.toNat e pour e≥0
```
- **Couche :** OS0_KERNEL
- **Composant :** `canonicalize_elapsed`
- **Invariants :** NO_ACT_BEFORE_TAU, NEGATIVE_CLOCK_SKEW_TO_HOLD
- **Note :** Garantit la cohérence Int→Nat lors du passage au kernel.

---

## Consensus.lean — `Obsidia`

### aggregate4_act
```
Si 3 <= countDec ACT [d1,d2,d3,d4], alors aggregate4 = ACT
```
- **Couche :** OS0_KERNEL
- **Composant :** `aggregate4`
- **Invariants :** HOLD_PRIORITY_OVER_ALLOW, THRESHOLD_CONSERVATION

### aggregate4_fail_closed
```
Si aucune supermajorité ACT/HOLD/BLOCK → aggregate4 = BLOCK
```
- **Couche :** OS0_KERNEL
- **Composant :** `aggregate4`
- **Invariants :** BLOCK_PRIORITY_OVER_HOLD_ALLOW, THRESHOLD_CONSERVATION
- **Note architecturale :** Fail-closed est le comportement par défaut prouvé. Toute modification du cas `else` invalide cette preuve.

### aggregate4_unanimous
```
aggregate4 d d d d = d (4 votants identiques)
```
- **Couche :** OS0_KERNEL
- **Composant :** `aggregate4`
- **Invariants :** DETERMINISM, THRESHOLD_CONSERVATION

### no_two_distinct_supermajorities_4
```
Impossible d'avoir simultaneously ≥3/4 ACT et ≥3/4 HOLD (ou tout autre paire distincte)
```
- **Couche :** OS0_KERNEL
- **Composant :** `aggregate4` / `countDec`
- **Invariants :** THRESHOLD_CONSERVATION, DETERMINISM

---

## Basic.lean — `Obsidia`

### D1 (via PROOF_INDEX.md)
Non-contradiction des règles de gouvernance.  
- **Couche :** OS0_KERNEL — **Invariant :** DETERMINISM

### E2 (via PROOF_INDEX.md)
Déterminisme du vote.  
- **Couche :** OS0_KERNEL — **Invariant :** DETERMINISM

### G1 (via PROOF_INDEX.md)
Immutabilité de la trace.  
- **Couche :** OS3_AUDIT_PROOF — **Invariant :** NO_KERNEL_MUTATION_FROM_PERIPHERY

### G2 (via PROOF_INDEX.md)
Cohérence du sceau Merkle.  
- **Couche :** OS3_AUDIT_PROOF — **Invariant :** ARCHIVE_NOT_RUNTIME

### G3 (via PROOF_INDEX.md)
Pas de contradiction circulaire.  
- **Couche :** OS0_KERNEL — **Invariants :** BLOCK_PRIORITY_OVER_HOLD_ALLOW, HOLD_PRIORITY_OVER_ALLOW

---

## Résumé par couche

| Couche | Nb théorèmes | Invariants couverts |
|---|---:|---|
| OS0_KERNEL | 12 | DETERMINISM, NO_ACT_BEFORE_TAU, HOLD_BEFORE_TAU, IRREV_DELAY, REV_BASELINE, NEG_SKEW, THRESHOLD, BLOCK_PRIO, HOLD_PRIO |
| OS1_GUARD | 1 | GUARD_X108_FINAL_AUTHORITY |
| OS3_AUDIT_PROOF | 2 | NO_KERNEL_MUTATION, ARCHIVE_NOT_RUNTIME |
