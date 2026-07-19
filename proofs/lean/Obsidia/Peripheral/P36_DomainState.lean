namespace Obsidia
namespace P36DomainState

structure DomainState where
  risk_score     : Nat
  contradictions : Nat

def L (s : DomainState) : Nat :=
  s.risk_score + s.contradictions

def domain_stable (s : DomainState) : Prop :=
  L s = 0

def domain_hold (s : DomainState) : Prop := ¬ domain_stable s

theorem zero_state_stable : domain_stable { risk_score := 0, contradictions := 0 } := rfl

theorem risk_implies_hold (s : DomainState) (h : 0 < s.risk_score) :
    domain_hold s := by
  intro hs; simp [domain_stable, L] at hs; omega

theorem contradiction_implies_hold (s : DomainState) (h : 0 < s.contradictions) :
    domain_hold s := by
  intro hs; simp [domain_stable, L] at hs; omega

end P36DomainState
end Obsidia
