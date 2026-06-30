structure DomainState where
  risk_score : Nat
  contradictions : Nat

def L (s : DomainState) : Nat :=
  s.risk_score + s.contradictions

def Phi (s : DomainState) : DomainState :=
  if s.contradictions > 0 then
    { s with risk_score := 0, contradictions := 0 }
  else
    s

theorem P36 (s : DomainState) : L (Phi s) <= L s := by
  unfold Phi
  split
  · simp [L]
  · omega
