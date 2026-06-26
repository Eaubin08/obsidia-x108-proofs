structure MemoryState where
  is_readonly : Bool
  decision_authority : Nat

def enforce_boundary (m : MemoryState) : MemoryState :=
  if m.is_readonly then 
    { m with decision_authority := 0 } 
  else 
    m

theorem lean_theorem_memory_non_sovereignty (m : MemoryState) (h : m.is_readonly = true) : (enforce_boundary m).decision_authority = 0 := by
  unfold enforce_boundary
  simp [h]

#check lean_theorem_memory_non_sovereignty