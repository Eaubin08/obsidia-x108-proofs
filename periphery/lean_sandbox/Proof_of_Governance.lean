namespace Obsidia
namespace Proof_of_Governance

structure GovernanceState where
  admitted : Bool
  authorized : Bool
  traced : Bool
  reversible : Bool

def admission_ok (s : GovernanceState) : Prop :=
  s.admitted = true

def authority_ok (s : GovernanceState) : Prop :=
  s.authorized = true

def trace_ok (s : GovernanceState) : Prop :=
  s.traced = true

def governance_proved (s : GovernanceState) : Prop :=
  admission_ok s ∧ authority_ok s ∧ trace_ok s

def action_governed (s : GovernanceState) : Prop :=
  governance_proved s ∧ s.reversible = true

theorem governance_proved_intro
    (s : GovernanceState)
    (ha : admission_ok s)
    (hu : authority_ok s)
    (ht : trace_ok s) :
    governance_proved s :=
  And.intro ha (And.intro hu ht)

theorem admission_from_governance_proved
    (s : GovernanceState)
    (h : governance_proved s) :
    admission_ok s :=
  h.left

theorem authority_from_governance_proved
    (s : GovernanceState)
    (h : governance_proved s) :
    authority_ok s :=
  h.right.left

theorem trace_from_governance_proved
    (s : GovernanceState)
    (h : governance_proved s) :
    trace_ok s :=
  h.right.right

theorem action_governed_intro
    (s : GovernanceState)
    (hg : governance_proved s)
    (hr : s.reversible = true) :
    action_governed s :=
  And.intro hg hr

theorem governance_from_action_governed
    (s : GovernanceState)
    (h : action_governed s) :
    governance_proved s :=
  h.left

end Proof_of_Governance
end Obsidia
