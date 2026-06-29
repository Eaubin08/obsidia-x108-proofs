namespace Obsidia
namespace Stratification_Gouvernee

structure LayerState where
  layer : Nat
  priority : Nat
  admissible : Bool

def layer_ordered (a b : LayerState) : Prop :=
  a.layer <= b.layer

def priority_respected (a b : LayerState) : Prop :=
  a.priority <= b.priority

def layer_admissible (s : LayerState) : Prop :=
  s.admissible = true

def governed_stratification (a b : LayerState) : Prop :=
  layer_ordered a b ∧ priority_respected a b ∧ layer_admissible a ∧ layer_admissible b

theorem governed_stratification_intro
    (a b : LayerState)
    (hl : layer_ordered a b)
    (hp : priority_respected a b)
    (ha : layer_admissible a)
    (hb : layer_admissible b) :
    governed_stratification a b :=
  And.intro hl (And.intro hp (And.intro ha hb))

theorem layer_ordered_from_governed
    (a b : LayerState)
    (h : governed_stratification a b) :
    layer_ordered a b :=
  h.left

theorem priority_respected_from_governed
    (a b : LayerState)
    (h : governed_stratification a b) :
    priority_respected a b :=
  h.right.left

theorem left_layer_admissible_from_governed
    (a b : LayerState)
    (h : governed_stratification a b) :
    layer_admissible a :=
  h.right.right.left

theorem right_layer_admissible_from_governed
    (a b : LayerState)
    (h : governed_stratification a b) :
    layer_admissible b :=
  h.right.right.right

end Stratification_Gouvernee
end Obsidia
