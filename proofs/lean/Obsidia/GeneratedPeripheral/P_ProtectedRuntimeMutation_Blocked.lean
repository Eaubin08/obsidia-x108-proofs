namespace Obsidia
namespace P_ProtectedRuntimeMutation_Blocked

structure RuntimeMutationState where
  runtime_mutation_requested : Bool
  mutation_blocked           : Bool

def protectedRuntimeMutationBlocked (s : RuntimeMutationState) : Prop :=
  s.runtime_mutation_requested = true → s.mutation_blocked = true

theorem P_ProtectedRuntimeMutation_Blocked
    (s : RuntimeMutationState)
    (h : protectedRuntimeMutationBlocked s)
    (hr : s.runtime_mutation_requested = true) :
    s.mutation_blocked = true := by
  exact h hr

end P_ProtectedRuntimeMutation_Blocked
end Obsidia
