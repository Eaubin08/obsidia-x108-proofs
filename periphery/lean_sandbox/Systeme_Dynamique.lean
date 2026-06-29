namespace Obsidia
namespace Systeme_Dynamique

structure DynamicState where
  time : Nat
  value : Nat
  stable : Bool

def evolves_to (a b : DynamicState) : Prop :=
  a.time <= b.time

def value_nonincreasing (a b : DynamicState) : Prop :=
  b.value <= a.value

def stable_state (s : DynamicState) : Prop :=
  s.stable = true

def dynamic_admissible (a b : DynamicState) : Prop :=
  evolves_to a b ∧ value_nonincreasing a b ∧ stable_state b

theorem dynamic_admissible_intro
    (a b : DynamicState)
    (he : evolves_to a b)
    (hv : value_nonincreasing a b)
    (hs : stable_state b) :
    dynamic_admissible a b :=
  And.intro he (And.intro hv hs)

theorem evolves_to_from_dynamic_admissible
    (a b : DynamicState)
    (h : dynamic_admissible a b) :
    evolves_to a b :=
  h.left

theorem value_nonincreasing_from_dynamic_admissible
    (a b : DynamicState)
    (h : dynamic_admissible a b) :
    value_nonincreasing a b :=
  h.right.left

theorem stable_state_from_dynamic_admissible
    (a b : DynamicState)
    (h : dynamic_admissible a b) :
    stable_state b :=
  h.right.right

end Systeme_Dynamique
end Obsidia
