namespace Obsidia
namespace PF_infini

structure PFInfinityState where
  cycle_input : Nat
  cycle_output : Nat
  recycled_energy : Nat
  loss : Nat
  next_input : Nat
  closure_ready : Bool

def no_free_energy (s : PFInfinityState) : Prop :=
  s.cycle_output <= s.cycle_input + s.recycled_energy

def differential_loss_closed (s : PFInfinityState) : Prop :=
  s.loss = 0

def recycled_energy_feeds_next (s : PFInfinityState) : Prop :=
  s.recycled_energy <= s.next_input

def closure_is_ready (s : PFInfinityState) : Prop :=
  s.closure_ready = true

def pf_infinite_closed (s : PFInfinityState) : Prop :=
  And (no_free_energy s)
    (And (differential_loss_closed s)
      (And (recycled_energy_feeds_next s) (closure_is_ready s)))

def canonical_pf_infinity_state : PFInfinityState :=
  { cycle_input := 1,
    cycle_output := 1,
    recycled_energy := 0,
    loss := 0,
    next_input := 1,
    closure_ready := true }

theorem pf_infinite_closed_intro
    (s : PFInfinityState)
    (hn : no_free_energy s)
    (hl : differential_loss_closed s)
    (hr : recycled_energy_feeds_next s)
    (hc : closure_is_ready s) :
    pf_infinite_closed s :=
  And.intro hn (And.intro hl (And.intro hr hc))

theorem no_free_energy_from_pf_infinite_closed
    (s : PFInfinityState)
    (h : pf_infinite_closed s) :
    no_free_energy s :=
  h.left

theorem differential_loss_closed_from_pf_infinite_closed
    (s : PFInfinityState)
    (h : pf_infinite_closed s) :
    differential_loss_closed s :=
  h.right.left

theorem recycled_energy_from_pf_infinite_closed
    (s : PFInfinityState)
    (h : pf_infinite_closed s) :
    recycled_energy_feeds_next s :=
  h.right.right.left

theorem closure_ready_from_pf_infinite_closed
    (s : PFInfinityState)
    (h : pf_infinite_closed s) :
    closure_is_ready s :=
  h.right.right.right

theorem canonical_no_free_energy :
    no_free_energy canonical_pf_infinity_state := by
  unfold no_free_energy canonical_pf_infinity_state
  simp

theorem canonical_differential_loss_closed :
    differential_loss_closed canonical_pf_infinity_state :=
  rfl

theorem canonical_recycled_energy_feeds_next :
    recycled_energy_feeds_next canonical_pf_infinity_state :=
  Nat.zero_le 1

theorem canonical_closure_is_ready :
    closure_is_ready canonical_pf_infinity_state :=
  rfl

theorem canonical_pf_infinite_closed :
    pf_infinite_closed canonical_pf_infinity_state :=
  And.intro canonical_no_free_energy
    (And.intro rfl
      (And.intro (Nat.zero_le 1) rfl))

end PF_infini
end Obsidia
