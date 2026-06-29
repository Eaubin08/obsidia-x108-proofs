namespace Obsidia
namespace DecisionTicketFormel

structure DecisionTicket where
  decision_id : Nat
  action_code : Nat
  tick : Nat
  coherence : Nat
  coherence_bound : Nat
  previous_hash : Nat
  current_hash : Nat
  result_code : Nat
  result_bound : Nat

def hash_links (previous next : DecisionTicket) : Prop :=
  next.previous_hash = previous.current_hash

def coherence_valid (t : DecisionTicket) : Prop :=
  t.coherence <= t.coherence_bound

def result_valid (t : DecisionTicket) : Prop :=
  t.result_code <= t.result_bound

def ticket_valid (t : DecisionTicket) : Prop :=
  And (coherence_valid t) (result_valid t)

def chain_valid_pair (previous next : DecisionTicket) : Prop :=
  hash_links previous next

def genesis_ticket (bound : Nat) : DecisionTicket :=
  { decision_id := 0, action_code := 0, tick := 0, coherence := 0, coherence_bound := bound, previous_hash := 0, current_hash := 0, result_code := 0, result_bound := bound }

theorem hash_links_intro
    (previous next : DecisionTicket)
    (h : next.previous_hash = previous.current_hash) :
    hash_links previous next :=
  h

theorem chain_valid_pair_intro
    (previous next : DecisionTicket)
    (h : hash_links previous next) :
    chain_valid_pair previous next :=
  h

theorem hash_links_from_chain_valid_pair
    (previous next : DecisionTicket)
    (h : chain_valid_pair previous next) :
    hash_links previous next :=
  h

theorem coherence_valid_intro
    (t : DecisionTicket)
    (h : t.coherence <= t.coherence_bound) :
    coherence_valid t :=
  h

theorem result_valid_intro
    (t : DecisionTicket)
    (h : t.result_code <= t.result_bound) :
    result_valid t :=
  h

theorem ticket_valid_intro
    (t : DecisionTicket)
    (hc : coherence_valid t)
    (hr : result_valid t) :
    ticket_valid t :=
  And.intro hc hr

theorem coherence_from_ticket_valid
    (t : DecisionTicket)
    (h : ticket_valid t) :
    coherence_valid t :=
  h.left

theorem result_from_ticket_valid
    (t : DecisionTicket)
    (h : ticket_valid t) :
    result_valid t :=
  h.right

theorem genesis_ticket_hash_self_linked
    (bound : Nat) :
    hash_links (genesis_ticket bound) (genesis_ticket bound) :=
  rfl

theorem genesis_ticket_chain_valid_pair
    (bound : Nat) :
    chain_valid_pair (genesis_ticket bound) (genesis_ticket bound) :=
  rfl

theorem genesis_ticket_coherence_valid
    (bound : Nat) :
    coherence_valid (genesis_ticket bound) :=
  Nat.zero_le bound

theorem genesis_ticket_result_valid
    (bound : Nat) :
    result_valid (genesis_ticket bound) :=
  Nat.zero_le bound

theorem genesis_ticket_valid
    (bound : Nat) :
    ticket_valid (genesis_ticket bound) :=
  And.intro (Nat.zero_le bound) (Nat.zero_le bound)

end DecisionTicketFormel
end Obsidia
