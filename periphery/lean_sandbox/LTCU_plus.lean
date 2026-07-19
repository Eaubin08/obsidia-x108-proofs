namespace Obsidia
namespace LTCUplus

-- LTCU+
-- Type: concept — peripherique, non-decisionnel, runtime_bound=false

structure LTCUplusState where
  coherent : Bool

def ltcuplus_coherent (s : LTCUplusState) : Prop :=
  s.coherent = true

def ltcuplus_hold (s : LTCUplusState) : Prop := ¬ ltcuplus_coherent s

theorem not_coherent_hold (s : LTCUplusState) (h : s.coherent = false) :
    ltcuplus_hold s := by
  intro hc; simp [ltcuplus_coherent, h] at hc

theorem coherent_not_hold (s : LTCUplusState) (h : ltcuplus_coherent s) :
    ¬ ltcuplus_hold s := fun nh => nh h

end LTCUplus
end Obsidia
