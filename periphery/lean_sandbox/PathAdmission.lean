namespace Obsidia
namespace PathAdmission

inductive PathVerdict where
  | allow
  | hold
  | block
  deriving DecidableEq, Repr

structure PathState where
  verified : Bool
  risk : Nat
  threshold : Nat

def risk_ok (p : PathState) : Prop :=
  p.risk <= p.threshold

def admitted (p : PathState) : Prop :=
  p.verified = true ∧ risk_ok p

theorem admitted_intro
    (p : PathState)
    (hv : p.verified = true)
    (hr : risk_ok p) :
    admitted p :=
  And.intro hv hr

theorem verified_from_admitted
    (p : PathState)
    (h : admitted p) :
    p.verified = true :=
  h.left

theorem risk_from_admitted
    (p : PathState)
    (h : admitted p) :
    risk_ok p :=
  h.right

end PathAdmission
end Obsidia