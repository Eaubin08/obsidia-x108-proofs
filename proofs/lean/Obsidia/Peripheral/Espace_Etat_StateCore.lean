-- Espace_Etat_StateCore.lean
-- SOURCE: proofs/lean/Obsidia/Basic.lean
--   Derive de Metrics.S (seuil), decision (theta<=S->ACT),
--   G1_act_above_threshold, E2_no_act_below_threshold,
--   G2_boundary_inclusive, G3_monotonicity
-- Status : FORMAL -- Peripheral repair D4B-1bis via Obsidure AVDR
-- SOURCE_COVERAGE: espace_etat_core | etat_admissible | hold_non_admissible
--                  seuil_decision | decision_acte | etat_core_kernel
-- PROVISIONAL_BOUNDARY: espace d etat discret (Nat).
--   Admissible <=> value <= threshold (mirror Basic.lean: theta <= S -> ACT).
--   HOLD <=> NOT admissible (mirror E2_no_act_below_threshold).
--   kernel_boundary: evaluation peripherique, non decisionnelle. KX108 seul est souverain.

namespace Obsidia
namespace EspaceEtatStateCore

-- Mirror de Metrics {T_mean H_score A_score S} + theta, en Nat standalone
structure StateCore where
  value     : Nat
  threshold : Nat

-- Mirror G1: theta <= S -> ACT (valeur dans seuil -> admissible)
def admissible (s : StateCore) : Prop :=
  s.value ≤ s.threshold

-- Mirror E2: NOT(theta <= S) -> HOLD
def hold_state (s : StateCore) : Prop :=
  ¬ admissible s

-- Etat canonique (value=0, threshold=1 : toujours admissible)
def canonical : StateCore :=
  { value := 0, threshold := 1 }

-- Mirror D1_determinism: admissibilite deterministe
theorem canonical_admissible : admissible canonical := Nat.zero_le 1

-- Hold implique non-admissible (tautologie par definition)
theorem hold_not_admissible (s : StateCore) (h : hold_state s) :
    ¬ admissible s := h

-- Mirror E2_no_act_below_threshold: depassement seuil -> HOLD
theorem exceedance_implies_hold (s : StateCore) (h : s.threshold < s.value) :
    hold_state s := by
  intro hadm; exact Nat.not_le.mpr h hadm

-- Mirror G2_boundary_inclusive: value = threshold -> admissible
theorem boundary_admissible (s : StateCore) (h : s.value = s.threshold) :
    admissible s := by unfold admissible; omega

-- Mirror G3_monotonicity: agrandissement seuil preserve admissibilite (Nat pur, sans struct-update)
theorem admissible_monotone_threshold (v t1 t2 : Nat)
    (h1 : v ≤ t1) (h2 : t1 ≤ t2) :
    admissible { value := v, threshold := t2 } :=
  Nat.le_trans h1 h2

end EspaceEtatStateCore
end Obsidia
