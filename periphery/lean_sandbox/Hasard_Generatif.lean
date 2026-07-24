namespace Obsidia
namespace HasardGeneratif

-- Hasard Génératif
-- Type: concept — peripherique, non-decisionnel, runtime_bound=false

structure HasardGeneratifState where
  coherent : Bool

def hasardgeneratif_coherent (s : HasardGeneratifState) : Prop :=
  s.coherent = true

def hasardgeneratif_hold (s : HasardGeneratifState) : Prop := ¬ hasardgeneratif_coherent s

theorem not_coherent_hold (s : HasardGeneratifState) (h : s.coherent = false) :
    hasardgeneratif_hold s := by
  intro hc; simp [hasardgeneratif_coherent, h] at hc

theorem coherent_not_hold (s : HasardGeneratifState) (h : hasardgeneratif_coherent s) :
    ¬ hasardgeneratif_hold s := fun nh => nh h

end HasardGeneratif
end Obsidia
