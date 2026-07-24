namespace Obsidia
namespace P88

def contradiction_pair (A : Prop) : Prop :=
  And A (Not A)

def non_contradictory (A : Prop) : Prop :=
  Not (contradiction_pair A)

theorem non_contradiction
    (A : Prop) :
    non_contradictory A :=
  fun h => h.right h.left

theorem no_true_and_not_true
    (A : Prop)
    (h : contradiction_pair A) :
    False :=
  h.right h.left

theorem contradiction_pair_eliminates
    (A : Prop) :
    Not (contradiction_pair A) :=
  fun h => h.right h.left

theorem cannot_hold_both
    (A : Prop)
    (ha : A)
    (hna : Not A) :
    False :=
  hna ha

end P88
end Obsidia
