namespace Obsidia
namespace Gardien_Amont

structure UpstreamState where
  unknowns : Nat
  risk : Nat
  threshold : Nat
  action_ready : Bool

def no_unknowns (s : UpstreamState) : Prop :=
  s.unknowns = 0

def risk_bounded (s : UpstreamState) : Prop :=
  s.risk <= s.threshold

def upstream_admissible (s : UpstreamState) : Prop :=
  no_unknowns s ∧ risk_bounded s ∧ s.action_ready = true

theorem upstream_admissible_intro
    (s : UpstreamState)
    (hu : no_unknowns s)
    (hr : risk_bounded s)
    (ha : s.action_ready = true) :
    upstream_admissible s :=
  And.intro hu (And.intro hr ha)

theorem no_unknowns_from_upstream_admissible
    (s : UpstreamState)
    (h : upstream_admissible s) :
    no_unknowns s :=
  h.left

theorem risk_bounded_from_upstream_admissible
    (s : UpstreamState)
    (h : upstream_admissible s) :
    risk_bounded s :=
  h.right.left

theorem action_ready_from_upstream_admissible
    (s : UpstreamState)
    (h : upstream_admissible s) :
    s.action_ready = true :=
  h.right.right

end Gardien_Amont
end Obsidia
