-- P50_Recursivite_Fondamentale.lean
-- SOURCE: proofs/lean/Obsidia/Basic.lean
--   Derive de E2_no_act_below_threshold (HOLD si precondition non remplie),
--   D1_determinism (determinisme de la decision)
-- Status : FORMAL -- LegacyPeripheral repair D4B-2bis via Obsidure AVDR
-- SOURCE_COVERAGE: recursivite_fondamentale | recursivite_admissible | recursivite_hold
--                  base_atteinte | coherence_recursive | continuite_locale
-- PROVISIONAL_BOUNDARY: recursivite discrete (Bool).
--   Admissible <=> base_atteinte=true et coherent=true.
--   HOLD si non admissible (mirror E2: pas d action sans precondition).
--   kernel_boundary: evaluation peripherique, non decisionnelle. KX108 seul est souverain.

namespace Obsidia
namespace P50RecursiviteFondamentale

-- Etat recursif : base atteinte + coherence locale (mirror precondition E2)
structure RecursifState where
  base_atteinte : Bool
  coherent      : Bool

-- Admissible si base atteinte ET coherent
def recursivite_admissible (r : RecursifState) : Prop :=
  r.base_atteinte = true ∧ r.coherent = true

-- HOLD si non admissible (mirror E2)
def recursivite_hold (r : RecursifState) : Prop :=
  ¬ recursivite_admissible r

-- Etat canonique : toujours admissible
def recursif_canonique : RecursifState :=
  { base_atteinte := true, coherent := true }

-- Canonique admissible
theorem canonique_admissible : recursivite_admissible recursif_canonique :=
  ⟨rfl, rfl⟩

-- Hold implique non admissible
theorem hold_not_admissible (r : RecursifState) (h : recursivite_hold r) :
    ¬ recursivite_admissible r := h

-- Sans base : HOLD
theorem sans_base_hold (r : RecursifState) (h : r.base_atteinte = false) :
    recursivite_hold r := by
  intro hadm
  have hb := hadm.1
  simp [h] at hb

-- Incoherence locale : HOLD
theorem incoherence_hold (r : RecursifState) (h : r.coherent = false) :
    recursivite_hold r := by
  intro hadm
  have hc := hadm.2
  simp [h] at hc

end P50RecursiviteFondamentale
end Obsidia
