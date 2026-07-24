namespace Obsidia
namespace SYRIQ

-- SYRIQ
-- Type: unknown — peripherique, non-decisionnel, runtime_bound=false

structure SYRIQState where
  coherent : Bool

def syriq_coherent (s : SYRIQState) : Prop :=
  s.coherent = true

def syriq_hold (s : SYRIQState) : Prop := ¬ syriq_coherent s

theorem not_coherent_hold (s : SYRIQState) (h : s.coherent = false) :
    syriq_hold s := by
  intro hc; simp [syriq_coherent, h] at hc

theorem coherent_not_hold (s : SYRIQState) (h : syriq_coherent s) :
    ¬ syriq_hold s := fun nh => nh h

end SYRIQ
end Obsidia
