namespace Obsidia
namespace Information_cause

structure InformationCauseState where
  information_integrated : Bool
  belief_channel : Bool
  decision_channel : Bool
  action_channel : Bool
  trace_channel : Bool
  cause_strength : Nat
  state_delta : Nat

def integrated_information (s : InformationCauseState) : Prop :=
  s.information_integrated = true

def latent_cause_present (s : InformationCauseState) : Prop :=
  0 < s.cause_strength

def belief_can_change (s : InformationCauseState) : Prop :=
  s.belief_channel = true

def decision_can_change (s : InformationCauseState) : Prop :=
  s.decision_channel = true

def action_can_change (s : InformationCauseState) : Prop :=
  s.action_channel = true

def trace_can_change (s : InformationCauseState) : Prop :=
  s.trace_channel = true

def state_delta_possible (s : InformationCauseState) : Prop :=
  0 < s.state_delta

def information_as_cause (s : InformationCauseState) : Prop :=
  And (integrated_information s)
    (And (latent_cause_present s)
      (And (belief_can_change s)
        (And (decision_can_change s)
          (And (action_can_change s)
            (And (trace_can_change s) (state_delta_possible s))))))

def canonical_information_cause_state : InformationCauseState :=
  { information_integrated := true,
    belief_channel := true,
    decision_channel := true,
    action_channel := true,
    trace_channel := true,
    cause_strength := 1,
    state_delta := 1 }

theorem information_as_cause_intro
    (s : InformationCauseState)
    (hi : integrated_information s)
    (hl : latent_cause_present s)
    (hb : belief_can_change s)
    (hd : decision_can_change s)
    (ha : action_can_change s)
    (ht : trace_can_change s)
    (hs : state_delta_possible s) :
    information_as_cause s :=
  And.intro hi
    (And.intro hl
      (And.intro hb
        (And.intro hd
          (And.intro ha
            (And.intro ht hs)))))

theorem integrated_from_information_as_cause
    (s : InformationCauseState)
    (h : information_as_cause s) :
    integrated_information s :=
  h.left

theorem latent_cause_from_information_as_cause
    (s : InformationCauseState)
    (h : information_as_cause s) :
    latent_cause_present s :=
  h.right.left

theorem belief_from_information_as_cause
    (s : InformationCauseState)
    (h : information_as_cause s) :
    belief_can_change s :=
  h.right.right.left

theorem decision_from_information_as_cause
    (s : InformationCauseState)
    (h : information_as_cause s) :
    decision_can_change s :=
  h.right.right.right.left

theorem action_from_information_as_cause
    (s : InformationCauseState)
    (h : information_as_cause s) :
    action_can_change s :=
  h.right.right.right.right.left

theorem trace_from_information_as_cause
    (s : InformationCauseState)
    (h : information_as_cause s) :
    trace_can_change s :=
  h.right.right.right.right.right.left

theorem delta_from_information_as_cause
    (s : InformationCauseState)
    (h : information_as_cause s) :
    state_delta_possible s :=
  h.right.right.right.right.right.right

theorem canonical_integrated_information :
    integrated_information canonical_information_cause_state :=
  rfl

theorem canonical_latent_cause_present :
    latent_cause_present canonical_information_cause_state :=
  Nat.succ_pos 0

theorem canonical_belief_can_change :
    belief_can_change canonical_information_cause_state :=
  rfl

theorem canonical_decision_can_change :
    decision_can_change canonical_information_cause_state :=
  rfl

theorem canonical_action_can_change :
    action_can_change canonical_information_cause_state :=
  rfl

theorem canonical_trace_can_change :
    trace_can_change canonical_information_cause_state :=
  rfl

theorem canonical_state_delta_possible :
    state_delta_possible canonical_information_cause_state :=
  Nat.succ_pos 0

theorem canonical_information_as_cause :
    information_as_cause canonical_information_cause_state :=
  And.intro rfl
    (And.intro (Nat.succ_pos 0)
      (And.intro rfl
        (And.intro rfl
          (And.intro rfl
            (And.intro rfl (Nat.succ_pos 0))))))

end Information_cause
end Obsidia
