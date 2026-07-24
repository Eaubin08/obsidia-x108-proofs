namespace Obsidia
namespace BALMA

-- BALMA
-- Type: unknown — peripherique, non-decisionnel, runtime_bound=false

structure BALMAState where
  coherent : Bool

def balma_coherent (s : BALMAState) : Prop :=
  s.coherent = true

def balma_hold (s : BALMAState) : Prop := ¬ balma_coherent s

theorem not_coherent_hold (s : BALMAState) (h : s.coherent = false) :
    balma_hold s := by
  intro hc; simp [balma_coherent, h] at hc

theorem coherent_not_hold (s : BALMAState) (h : balma_coherent s) :
    ¬ balma_hold s := fun nh => nh h

end BALMA
end Obsidia
