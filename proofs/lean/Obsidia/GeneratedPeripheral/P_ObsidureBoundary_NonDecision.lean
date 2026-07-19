namespace Obsidia
namespace P_ObsidureBoundary_NonDecision

structure BoundaryState where
  allowed_to_decide : Bool
  emits_act         : Bool

def nonDecisionBoundary (s : BoundaryState) : Prop :=
  s.allowed_to_decide = false ∧ s.emits_act = false

theorem P_ObsidureBoundary_NonDecision
    (s : BoundaryState)
    (h : nonDecisionBoundary s) :
    s.allowed_to_decide = false := by
  exact h.left

end P_ObsidureBoundary_NonDecision
end Obsidia
