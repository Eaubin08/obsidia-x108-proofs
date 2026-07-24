namespace Obsidia
namespace P_GraphitiReadonly_NoWrite

structure MemoryBoundaryState where
  graphiti_write : Bool
  readonly       : Bool

def graphitiReadonly (s : MemoryBoundaryState) : Prop :=
  s.graphiti_write = false ∧ s.readonly = true

theorem P_GraphitiReadonly_NoWrite
    (s : MemoryBoundaryState)
    (h : graphitiReadonly s) :
    s.graphiti_write = false := by
  exact h.left

end P_GraphitiReadonly_NoWrite
end Obsidia
