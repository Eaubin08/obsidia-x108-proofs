structure SystemState where
  contradictions : Nat
  can_act : Bool

def enforce_stability (s : SystemState) : SystemState :=
  if s.contradictions > 0 then
    { s with can_act := false }
  else
    s

theorem lean_theorem_stability_before_action (s : SystemState) (h : s.contradictions > 0) : (enforce_stability s).can_act = false := by
  unfold enforce_stability
  simp [h]

#check lean_theorem_stability_before_action