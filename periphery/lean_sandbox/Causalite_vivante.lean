namespace Obsidia
namespace Causalite_vivante

structure CausalLoopState where
  information_ready : Bool
  decision_ready : Bool
  action_done : Bool
  trace_recorded : Bool
  feedback_ready : Bool

def information_active (s : CausalLoopState) : Prop :=
  s.information_ready = true

def decision_active (s : CausalLoopState) : Prop :=
  s.decision_ready = true

def action_active (s : CausalLoopState) : Prop :=
  s.action_done = true

def trace_active (s : CausalLoopState) : Prop :=
  s.trace_recorded = true

def feedback_active (s : CausalLoopState) : Prop :=
  s.feedback_ready = true

def causal_chain_complete (s : CausalLoopState) : Prop :=
  And (information_active s) (And (decision_active s) (And (action_active s) (trace_active s)))

def causal_feedback_complete (s : CausalLoopState) : Prop :=
  And (causal_chain_complete s) (feedback_active s)

def living_causal_loop (s : CausalLoopState) : Prop :=
  causal_feedback_complete s

def canonical_causal_loop_state : CausalLoopState :=
  { information_ready := true, decision_ready := true, action_done := true, trace_recorded := true, feedback_ready := true }

theorem causal_chain_complete_intro
    (s : CausalLoopState)
    (hi : information_active s)
    (hd : decision_active s)
    (ha : action_active s)
    (ht : trace_active s) :
    causal_chain_complete s :=
  And.intro hi (And.intro hd (And.intro ha ht))

theorem causal_feedback_complete_intro
    (s : CausalLoopState)
    (hc : causal_chain_complete s)
    (hf : feedback_active s) :
    causal_feedback_complete s :=
  And.intro hc hf

theorem information_from_causal_feedback
    (s : CausalLoopState)
    (h : causal_feedback_complete s) :
    information_active s :=
  h.left.left

theorem decision_from_causal_feedback
    (s : CausalLoopState)
    (h : causal_feedback_complete s) :
    decision_active s :=
  h.left.right.left

theorem action_from_causal_feedback
    (s : CausalLoopState)
    (h : causal_feedback_complete s) :
    action_active s :=
  h.left.right.right.left

theorem trace_from_causal_feedback
    (s : CausalLoopState)
    (h : causal_feedback_complete s) :
    trace_active s :=
  h.left.right.right.right

theorem feedback_from_causal_feedback
    (s : CausalLoopState)
    (h : causal_feedback_complete s) :
    feedback_active s :=
  h.right

theorem living_loop_from_causal_feedback
    (s : CausalLoopState)
    (h : causal_feedback_complete s) :
    living_causal_loop s :=
  h

theorem canonical_causal_chain_complete :
    causal_chain_complete canonical_causal_loop_state :=
  And.intro rfl (And.intro rfl (And.intro rfl rfl))

theorem canonical_causal_feedback_complete :
    causal_feedback_complete canonical_causal_loop_state :=
  And.intro canonical_causal_chain_complete rfl

theorem canonical_living_causal_loop :
    living_causal_loop canonical_causal_loop_state :=
  canonical_causal_feedback_complete

end Causalite_vivante
end Obsidia
