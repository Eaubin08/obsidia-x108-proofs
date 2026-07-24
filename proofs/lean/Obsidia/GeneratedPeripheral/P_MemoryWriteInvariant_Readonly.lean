namespace Obsidia
namespace P_MemoryWriteInvariant_Readonly

structure MemoryBoundaryState where
  memory_write           : Bool
  canonical_memory_write : Bool
  graphiti_write         : Bool
  readonly               : Bool
  attestation_only       : Bool

def memoryReadonly (s : MemoryBoundaryState) : Prop :=
  s.memory_write = false ∧
  s.canonical_memory_write = false ∧
  s.graphiti_write = false ∧
  s.readonly = true ∧
  s.attestation_only = true

theorem P_MemoryWriteInvariant_Readonly
    (s : MemoryBoundaryState)
    (h : memoryReadonly s) :
    s.memory_write = false ∧ s.readonly = true := by
  exact And.intro h.left h.right.right.right.left

end P_MemoryWriteInvariant_Readonly
end Obsidia
