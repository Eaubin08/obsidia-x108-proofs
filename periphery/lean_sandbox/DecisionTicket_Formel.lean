-- DecisionTicket_Formel -- ticket de decision et chaine de hachage
-- Status : CANONICAL_CANDIDATE scaffold -- Palier 6 item 113/134
-- SOURCE_COVERAGE: decisionticket_formel | decision_ticket | ticket_id | action_a | time_t
--                  context_c | invariant_i | delta_tau | risk_r | h_prev | h_current
--                  hash_chain_ready | receipt_ready | audit_trace_ready | replay_ready
--                  kernel_boundary | non_sovereign_ticket
-- PROVISIONAL_BOUNDARY: le ticket de decision est encode par Nat et flags Bool.
--   Ticket = (id, a, t, c, i, delta_tau, r, h_prev, h_current).
--   La chaine de hachage rend la decision auditable et rejouable.
--   Le ticket trace une decision, mais ne decide pas : kernel_boundary reste obligatoire.

namespace Obsidia
namespace DecisionTicketFormel

structure DecisionTicketState where
  ticket_id : Nat
  action_a : Bool
  time_t : Nat
  context_c : Bool
  invariant_i : Bool
  delta_tau : Nat
  risk_r : Nat
  h_prev : Nat
  h_current : Nat
  fields_ready : Bool
  hash_chain_ready : Bool
  receipt_ready : Bool
  audit_trace_ready : Bool
  replay_ready : Bool
  kernel_boundary : Bool
  non_sovereign_ticket : Bool

def ticket_fields_ready (t : DecisionTicketState) : Prop :=
  And (t.action_a = true)
  (And (t.context_c = true)
  (And (t.invariant_i = true)
       (t.fields_ready = true)))

def hash_and_receipt_ready (t : DecisionTicketState) : Prop :=
  And (t.hash_chain_ready = true)
  (And (t.receipt_ready = true)
       (t.audit_trace_ready = true))

def decision_ticket_admissible (t : DecisionTicketState) : Prop :=
  And (ticket_fields_ready t)
  (And (hash_and_receipt_ready t)
  (And (t.replay_ready = true)
  (And (t.kernel_boundary = true)
       (t.non_sovereign_ticket = true))))

def decision_ticket_canonique : DecisionTicketState :=
  { ticket_id := 113,
    action_a := true,
    time_t := 1,
    context_c := true,
    invariant_i := true,
    delta_tau := 0,
    risk_r := 0,
    h_prev := 10,
    h_current := 11,
    fields_ready := true,
    hash_chain_ready := true,
    receipt_ready := true,
    audit_trace_ready := true,
    replay_ready := true,
    kernel_boundary := true,
    non_sovereign_ticket := true }

theorem decision_ticket_canonique_admissible :
    decision_ticket_admissible decision_ticket_canonique :=
  And.intro
    (And.intro rfl
      (And.intro rfl
        (And.intro rfl rfl)))
    (And.intro
      (And.intro rfl
        (And.intro rfl rfl))
      (And.intro rfl
        (And.intro rfl rfl)))

theorem decision_ticket_has_fields
    (t : DecisionTicketState)
    (h : decision_ticket_admissible t) :
    ticket_fields_ready t :=
  h.left

theorem decision_ticket_has_hash_chain
    (t : DecisionTicketState)
    (h : decision_ticket_admissible t) :
    hash_and_receipt_ready t :=
  h.right.left

theorem decision_ticket_has_replay
    (t : DecisionTicketState)
    (h : decision_ticket_admissible t) :
    t.replay_ready = true :=
  h.right.right.left

theorem decision_ticket_has_kernel_boundary
    (t : DecisionTicketState)
    (h : decision_ticket_admissible t) :
    t.kernel_boundary = true :=
  h.right.right.right.left

theorem decision_ticket_is_non_sovereign
    (t : DecisionTicketState)
    (h : decision_ticket_admissible t) :
    t.non_sovereign_ticket = true :=
  h.right.right.right.right

theorem hash_and_receipt_has_audit_trace
    (t : DecisionTicketState)
    (h : hash_and_receipt_ready t) :
    t.audit_trace_ready = true :=
  h.right.right

end DecisionTicketFormel
end Obsidia
