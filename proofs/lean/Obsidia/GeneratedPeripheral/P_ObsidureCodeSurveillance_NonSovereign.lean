namespace Obsidia
namespace P_ObsidureCodeSurveillance_NonSovereign

structure CodeSurveillanceState where
  proposes_only    : Bool
  emits_act        : Bool
  runtime_mutation : Bool

def codeSurveillanceNonSovereign (s : CodeSurveillanceState) : Prop :=
  s.proposes_only = true ∧ s.emits_act = false ∧ s.runtime_mutation = false

theorem P_ObsidureCodeSurveillance_NonSovereign
    (s : CodeSurveillanceState)
    (h : codeSurveillanceNonSovereign s) :
    s.emits_act = false := by
  exact h.right.left

end P_ObsidureCodeSurveillance_NonSovereign
end Obsidia
