namespace Obsidia
namespace P_CanonicalMemoryWrite_Blocked

structure MemoryBoundaryState where
  memory_write           : Bool
  canonical_memory_write : Bool

def noMemoryWrite (s : MemoryBoundaryState) : Prop :=
  s.memory_write = false ∧ s.canonical_memory_write = false

theorem P_CanonicalMemoryWrite_Blocked
    (s : MemoryBoundaryState)
    (h : noMemoryWrite s) :
    s.canonical_memory_write = false := by
  exact h.right

end P_CanonicalMemoryWrite_Blocked
end Obsidia
