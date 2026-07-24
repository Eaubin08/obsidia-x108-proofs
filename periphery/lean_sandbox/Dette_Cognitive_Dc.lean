-- Dette_Cognitive_Dc -- Dette cognitive Dc = ecart cumule entre coherence reelle et cible
-- Status : PROVISIONAL scaffold -- Palier 8
-- SOURCE_COVERAGE: dette_cognitive_Dc | ecart_coherence | coherence_reelle
--                  coherence_cible | accumulation_ecart | remboursement_dette
--                  seuil_dette | dette_critique | amortissement
-- PROVISIONAL_BOUNDARY: dette cognitive approchee en Nat discret.
--   Dc = somme des ecarts (sigma_cib - sigma_reel) quand sigma_reel < sigma_cib.
--   kernel_boundary: dette peripherique, non decisionnelle. KX108 seul est souverain.

namespace Obsidia
namespace DetteCognitiveDc

structure DetteState where
  dette      : Nat
  seuil_crit : Nat
  amort      : Nat

def dette_nulle (d : DetteState) : Prop :=
  d.dette = 0

def dette_critique (d : DetteState) : Prop :=
  d.dette >= d.seuil_crit

def dette_amortie (d : DetteState) : Prop :=
  d.amort >= d.dette

def dette_canonique : DetteState :=
  { dette := 10, seuil_crit := 50, amort := 5 }

theorem dette_canonique_non_critique : Not (dette_critique dette_canonique) := by
  simp only [dette_critique, dette_canonique]; omega

theorem dette_nulle_implies_non_critique (d : DetteState)
    (hs : d.seuil_crit > 0) (h : dette_nulle d) : Not (dette_critique d) := by
  simp only [dette_nulle] at h
  simp only [dette_critique]
  omega

theorem dette_amortie_bounded (d : DetteState) (h : dette_amortie d) :
    d.amort >= d.dette :=
  h

end DetteCognitiveDc
end Obsidia
