structure ProcessState where
  is_qualified : Bool
  execute_action : Bool

def enforce_order (s : ProcessState) : ProcessState :=
  if s.is_qualified == false then
    { s with execute_action := false }
  else
    s

theorem lean_theorem_order_error_prevention (s : ProcessState) (h : s.is_qualified = false) : (enforce_order s).execute_action = false := by
  unfold enforce_order
  simp [h]
