-- Economie_Interne_Cognitive -- Economie interne : budget cognitif, allocation, ROI
-- Status : PROVISIONAL scaffold -- Palier 8
-- SOURCE_COVERAGE: economie_interne_cognitive | budget_cognitif | allocation_ressources
--                  ROI_cognitif | depense_cognitive | surplus_cognitif
--                  equilibre_budgetaire | contrainte_budget | optimisation_allocation
-- PROVISIONAL_BOUNDARY: economie cognitive approchee en Nat discret.
--   Budget = revenus - depenses. ROI = benefice / cout.
--   kernel_boundary: economie peripherique, non decisionnelle. KX108 seul est souverain.

namespace Obsidia
namespace EconomieInterneCognitive

structure EcoState where
  budget   : Nat
  depense  : Nat
  benefice : Nat

def budget_equilibre (e : EcoState) : Prop :=
  e.depense <= e.budget

def roi_positif (e : EcoState) : Prop :=
  e.benefice >= e.depense

def surplus_cognitif (e : EcoState) : Prop :=
  And (budget_equilibre e) (roi_positif e)

def eco_canonique : EcoState :=
  { budget := 100, depense := 60, benefice := 80 }

theorem eco_canonique_surplus : surplus_cognitif eco_canonique := by
  simp only [surplus_cognitif, budget_equilibre, roi_positif, eco_canonique]; omega

theorem surplus_implies_equilibre (e : EcoState) (h : surplus_cognitif e) :
    budget_equilibre e :=
  h.left

theorem surplus_implies_roi (e : EcoState) (h : surplus_cognitif e) :
    roi_positif e :=
  h.right

end EconomieInterneCognitive
end Obsidia
