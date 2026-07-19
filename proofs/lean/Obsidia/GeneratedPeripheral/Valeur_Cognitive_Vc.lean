-- Valeur_Cognitive_Vc -- Valeur cognitive Vc = utilite produite par unite d effort
-- Status : PROVISIONAL scaffold -- Palier 8
-- SOURCE_COVERAGE: valeur_cognitive_Vc | utilite_produite | effort_cognitif
--                  ratio_valeur_effort | Vc_positif | Vc_optimal | seuil_Vc
-- PROVISIONAL_BOUNDARY: Vc approchee en Nat discret (utilite/effort sur 100).
--   Vc = utilite / effort (approx discrete : utilite >= effort => Vc admissible).
--   kernel_boundary: calcul peripherique, non decisionnel. KX108 seul est souverain.

namespace Obsidia
namespace ValeurCognitiveVc

structure VcState where
  utilite : Nat
  effort  : Nat

def vc_admissible (s : VcState) : Prop :=
  And (s.effort > 0) (s.utilite <= 100)

def vc_positif (s : VcState) : Prop :=
  s.utilite >= s.effort

def vc_optimal (s : VcState) : Prop :=
  s.utilite >= s.effort * 2

def vc_canonique : VcState :=
  { utilite := 80, effort := 30 }

theorem vc_canonique_admissible : vc_admissible vc_canonique := by
  simp only [vc_admissible, vc_canonique]; omega

theorem vc_canonique_positif : vc_positif vc_canonique := by
  simp only [vc_positif, vc_canonique]; omega

theorem vc_canonique_optimal : vc_optimal vc_canonique := by
  simp only [vc_optimal, vc_canonique]; omega

theorem vc_optimal_implies_positif (s : VcState) (h : vc_optimal s) :
    vc_positif s := by
  simp only [vc_optimal] at h
  simp only [vc_positif]
  omega

end ValeurCognitiveVc
end Obsidia
