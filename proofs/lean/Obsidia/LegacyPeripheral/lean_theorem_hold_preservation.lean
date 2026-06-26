structure ActionState where
  is_hold : Bool
  can_act : Bool

def apply_hold_policy (s : ActionState) : ActionState :=
  if s.is_hold then
    { s with can_act := false }
  else
    s

theorem lean_theorem_hold_preservation (s : ActionState) (h : s.is_hold = true) : (apply_hold_policy s).can_act = false := by
  unfold apply_hold_policy
  simp [h]

#check lean_theorem_hold_preservation