import Std

namespace Obsidia
namespace GouvernanceExAnte

inductive Decision where
  | HOLD
  | BLOCK
  | ACT
  deriving DecidableEq, Repr

structure Action where
  risk : Nat

structure DomainState where
  threshold : Nat

def admissible (a : Action) (s : DomainState) : Prop :=
  a.risk ≤ s.threshold

def govern (a : Action) (s : DomainState) : Decision :=
  if a.risk ≤ s.threshold then Decision.ACT else Decision.HOLD

theorem act_implies_admissible
    (a : Action)
    (s : DomainState)
    (h : govern a s = Decision.ACT) :
    admissible a s := by
  unfold govern at h
  unfold admissible
  by_cases hr : a.risk ≤ s.threshold
  · exact hr
  · have hbad : Decision.HOLD = Decision.ACT := by
      simpa [hr] using h
    cases hbad

theorem admissible_self
    (a : Action)
    (s : DomainState)
    (h : admissible a s) :
    admissible a s :=
  h

end GouvernanceExAnte
end Obsidia