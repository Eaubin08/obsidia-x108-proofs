namespace Obsidia
namespace NeantActif

-- Néant Actif
-- Type: concept — peripherique, non-decisionnel, runtime_bound=false

structure NeantActifState where
  coherent : Bool

def neantactif_coherent (s : NeantActifState) : Prop :=
  s.coherent = true

def neantactif_hold (s : NeantActifState) : Prop := ¬ neantactif_coherent s

theorem not_coherent_hold (s : NeantActifState) (h : s.coherent = false) :
    neantactif_hold s := by
  intro hc; simp [neantactif_coherent, h] at hc

theorem coherent_not_hold (s : NeantActifState) (h : neantactif_coherent s) :
    ¬ neantactif_hold s := fun nh => nh h

end NeantActif
end Obsidia
