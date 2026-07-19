namespace Obsidia
namespace Local_update

structure LocalUpdate where
  before : Nat
  after : Nat
  delta : Nat
  budget : Nat
  propagated : Bool

def delta_within_budget (u : LocalUpdate) : Prop :=
  u.delta <= u.budget

def local_effect_bounded (u : LocalUpdate) : Prop :=
  u.after <= u.before + u.delta

def no_global_propagation (u : LocalUpdate) : Prop :=
  u.propagated = false

def local_update_admissible (u : LocalUpdate) : Prop :=
  And (delta_within_budget u) (And (local_effect_bounded u) (no_global_propagation u))

def identity_local_update (value budget : Nat) : LocalUpdate :=
  { before := value, after := value, delta := 0, budget := budget, propagated := false }

theorem local_update_admissible_intro
    (u : LocalUpdate)
    (hb : delta_within_budget u)
    (he : local_effect_bounded u)
    (hn : no_global_propagation u) :
    local_update_admissible u :=
  And.intro hb (And.intro he hn)

theorem delta_within_budget_from_local_update
    (u : LocalUpdate)
    (h : local_update_admissible u) :
    delta_within_budget u :=
  h.left

theorem local_effect_bounded_from_local_update
    (u : LocalUpdate)
    (h : local_update_admissible u) :
    local_effect_bounded u :=
  h.right.left

theorem no_global_propagation_from_local_update
    (u : LocalUpdate)
    (h : local_update_admissible u) :
    no_global_propagation u :=
  h.right.right

theorem identity_delta_within_budget
    (value budget : Nat) :
    delta_within_budget (identity_local_update value budget) :=
  Nat.zero_le budget

theorem identity_local_effect_bounded
    (value budget : Nat) :
    local_effect_bounded (identity_local_update value budget) := by
  unfold local_effect_bounded identity_local_update
  simp

theorem identity_no_global_propagation
    (value budget : Nat) :
    no_global_propagation (identity_local_update value budget) :=
  rfl

theorem identity_local_update_admissible
    (value budget : Nat) :
    local_update_admissible (identity_local_update value budget) :=
  And.intro (Nat.zero_le budget) (And.intro (identity_local_effect_bounded value budget) rfl)

end Local_update
end Obsidia
