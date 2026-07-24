namespace Obsidia
namespace LOI_COUT_CAUSAL

structure CausalCostState where
  act_cost : Nat
  hold_cost : Nat
  stabilisation_gain : Nat
  reserve : Nat

def action_has_cost (s : CausalCostState) : Prop :=
  0 < s.act_cost

def hold_has_cost (s : CausalCostState) : Prop :=
  0 < s.hold_cost

def hold_is_active (s : CausalCostState) : Prop :=
  0 < s.stabilisation_gain

def raw_causal_cost (s : CausalCostState) : Nat :=
  s.act_cost + s.hold_cost

def reserve_covers_causal_cost (s : CausalCostState) : Prop :=
  raw_causal_cost s <= s.reserve

def causal_cost_law_admissible (s : CausalCostState) : Prop :=
  And (action_has_cost s) (And (hold_has_cost s) (And (hold_is_active s) (reserve_covers_causal_cost s)))

def canonical_hold_state : CausalCostState :=
  { act_cost := 1, hold_cost := 1, stabilisation_gain := 1, reserve := 2 }

theorem causal_cost_law_admissible_intro
    (s : CausalCostState)
    (ha : action_has_cost s)
    (hh : hold_has_cost s)
    (hs : hold_is_active s)
    (hr : reserve_covers_causal_cost s) :
    causal_cost_law_admissible s :=
  And.intro ha (And.intro hh (And.intro hs hr))

theorem action_cost_from_causal_cost_law
    (s : CausalCostState)
    (h : causal_cost_law_admissible s) :
    action_has_cost s :=
  h.left

theorem hold_cost_from_causal_cost_law
    (s : CausalCostState)
    (h : causal_cost_law_admissible s) :
    hold_has_cost s :=
  h.right.left

theorem hold_active_from_causal_cost_law
    (s : CausalCostState)
    (h : causal_cost_law_admissible s) :
    hold_is_active s :=
  h.right.right.left

theorem reserve_from_causal_cost_law
    (s : CausalCostState)
    (h : causal_cost_law_admissible s) :
    reserve_covers_causal_cost s :=
  h.right.right.right

theorem canonical_action_has_cost :
    action_has_cost canonical_hold_state :=
  Nat.succ_pos 0

theorem canonical_hold_has_cost :
    hold_has_cost canonical_hold_state :=
  Nat.succ_pos 0

theorem canonical_hold_is_active :
    hold_is_active canonical_hold_state :=
  Nat.succ_pos 0

theorem canonical_raw_causal_cost :
    raw_causal_cost canonical_hold_state = 2 :=
  rfl

theorem canonical_reserve_covers_causal_cost :
    reserve_covers_causal_cost canonical_hold_state :=
  Nat.le_refl 2

theorem canonical_causal_cost_law_admissible :
    causal_cost_law_admissible canonical_hold_state :=
  And.intro (Nat.succ_pos 0) (And.intro (Nat.succ_pos 0) (And.intro (Nat.succ_pos 0) (Nat.le_refl 2)))

end LOI_COUT_CAUSAL
end Obsidia
