# THÉORÈMES LEAN 4 ET TLA+ — TEXTE BRUT DES FICHIERS
**Source :** `proofs/lean/Obsidia/*.lean` + `proofs/tla/*.tla`  
**Généré le :** 2026-06-25  
**Statut :** FREEZE_CONFIRMED — copie de référence pour navigation

---

## Basic.lean — Fichier racine des lois X-108

```lean
-- decision_eq_ACT_iff
theorem decision_eq_ACT_iff (m : Metrics) (theta : Rat) :
  decision m theta = ACT ↔ theta ≤ m.S

-- decision_eq_HOLD_iff
theorem decision_eq_HOLD_iff (m : Metrics) (theta : Rat) :
  decision m theta = HOLD ↔ ¬(theta ≤ m.S)

-- D1_determinism
theorem D1_determinism (m : Metrics) (theta : Rat) :
  decision m theta = ACT ∨ decision m theta = HOLD

-- G1_act_above_threshold
theorem G1_act_above_threshold (m : Metrics) (theta : Rat)
  (h : theta ≤ m.S) : decision m theta = ACT

-- E2_no_act_below_threshold
theorem E2_no_act_below_threshold (m : Metrics) (theta : Rat)
  (h : ¬(theta ≤ m.S)) : decision m theta ≠ ACT

-- G2_boundary_inclusive
theorem G2_boundary_inclusive (m : Metrics) (theta : Rat)
  -- borne incluse : theta = S → ACT

-- G3_monotonicity
theorem G3_monotonicity (m1 m2 : Metrics) (theta : Rat)
  -- monotonie de la décision par rapport aux métriques

-- L11_3_no_block
theorem L11_3_no_block (m : Metrics) (theta : Rat) :
  decision m theta ≠ BLOCK

-- L11_3_act / L11_3_hold / decision_not_both
-- (triplet de complétude des cas de décision)
```

---

## Consensus.lean — Supermajorité 4 agents

```lean
-- aggregate4_act : ACT si supermajorité d'agents ACT
-- aggregate4_fail_closed : HOLD si pas de supermajorité
-- aggregate4_unanimous : résultat unanime
-- no_act_and_hold_supermajority_4 : ¬(ACT_supermaj ∧ HOLD_supermaj)
-- no_act_and_block_supermajority_4 : ¬(ACT_supermaj ∧ BLOCK_supermaj)
-- no_hold_and_block_supermajority_4 : ¬(HOLD_supermaj ∧ BLOCK_supermaj)
-- no_two_distinct_supermajorities_4 : unicité de la supermajorité
```

---

## TemporalKernel.lean — Verrou temporel

```lean
-- X108_no_act_before_tau : ∀ elapsed < tau → decision ≠ ACT
-- X108_after_tau_equals_base : elapsed ≥ tau → retour état base
-- X108_kernel_never_blocks : ∀ tau i metrics → decision ≠ BLOCK
-- X108_reversible_equals_base : action réversible = base
-- X108_irreversible_after_tau_equals_base : irréversible après tau = base
```

---

## TemporalBridge.lean

```lean
-- canonicalize_preserves_nonneg (e : Int) (_h : 0 ≤ e) : 0 ≤ canonicalize e
-- skew_negative_implies_hold : skew < 0 → décision = HOLD
```

---

## SystemModel.lean

```lean
-- P17_KernelNeverBlocks : ∀ i s → transition s i ≠ BLOCK_STATE
-- P17_Determinism : ∀ s i → transition s i est déterministe
-- P17_SealSensitive : modification → changement de sceau
-- P17_AuditGrowth : ∀ s i → |auditLog(transition s i)| = |auditLog s| + 1
-- P17_TransitionFstIsDecide : fst(transition s i) = decide i
```

---

## Sensitivity.lean

```lean
-- merkleRoot_change_if_leaf_change : ∀ i leaf ≠ leaf' → root(i,leaf) ≠ root(i,leaf')
-- globalSeal_change_if_root_change : root change → seal change
-- P15_Immutability_Strong : toute modification est détectable via le sceau
```

---

## Seal.lean

```lean
-- P13_Immutability : immutabilité par sceau Merkle
```

---

## Refinement.lean

```lean
-- lift_refines : le lift raffine la décision de base
-- x108_is_lift : X-108 est l'implémentation du lift
-- x108_never_blocks : X-108 ne produit jamais BLOCK
-- refined_not_block : décision raffinée ≠ BLOCK
```

---

## Merkle.lean

```lean
-- merkle2_left_mutation : mutation feuille gauche → mutation racine
-- merkle2_right_mutation : mutation feuille droite → mutation racine
```

---

## CryptoAssumptions.lean

```lean
-- H_injective_left / H_injective_right : H est injectif
-- foldl_H_injective : composition injective
-- fileHash_inj (f g : File) : fileHash f = fileHash g → f = g
-- combine_inj (xs ys) : combine xs = combine ys → xs = ys
-- decodeFold_foldl_of_decodable / decodeFold_foldl_neutral
-- append_nil_local / append_assoc_local
```

---

## X108.tla — Spécification TLA+ core

**Propriétés model-checkées :**
```tla
PROPERTY Determinism : □[Kernel!Determinism]_vars
PROPERTY NeverBlock  : □(decision ≠ "BLOCK")
PROPERTY FailClosed  : □(¬Supermajority → decision = "HOLD")
PROPERTY AuditGrowth : □[Len(auditLog') = Len(auditLog) + 1]_vars
```

---

## DistributedX108.tla — Kernel distribué

**Invariants supplémentaires :**
```tla
INVARIANT NonCircumvention : ∀ agent ∈ Agents : agent.decision ∈ {ACT, HOLD}
INVARIANT BlockDominance   : ∃ a ∈ Agents : a.decision = BLOCK → consensus = BLOCK
```

---

## Preuves périphériques V3 (sandbox — A_PROUVER)

### P107 — Stabilité de Lyapunov δ-ε
```lean
-- Objectif formel :
-- theorem P107_Lyapunov_stability :
--   ∀ (s : State) (Φ : State → State) (L : State → Real),
--     Lyapunov_function L → L (Φ s) ≤ L s
```

### P36 — Quintuplet d'état canonique
```lean
-- theorem P36_canonical_quintuplet :
--   ∀ (s : State), ∃ (S I L : ...), canonical_form s = (S, I, L)
```

### P161 — Calibration énergétique temporelle
```lean
-- theorem P161_energy_calibration :
--   ∀ (t : Time) (E : Energy), calibrated E t ↔ |E t - E_ref| < ε
```
