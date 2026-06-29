namespace Obsidia
namespace Lambda_t

structure LambdaState where
  t : Nat
  value : Nat

def active (s : LambdaState) : Prop :=
  0 < s.value

def time_ordered (a b : LambdaState) : Prop :=
  a.t <= b.t

def lambda_admissible (a b : LambdaState) : Prop :=
  active a ∧ active b ∧ time_ordered a b

theorem lambda_admissible_intro
    (a b : LambdaState)
    (ha : active a)
    (hb : active b)
    (ht : time_ordered a b) :
    lambda_admissible a b :=
  And.intro ha (And.intro hb ht)

theorem active_left_from_lambda_admissible
    (a b : LambdaState)
    (h : lambda_admissible a b) :
    active a :=
  h.left

theorem active_right_from_lambda_admissible
    (a b : LambdaState)
    (h : lambda_admissible a b) :
    active b :=
  h.right.left

theorem time_ordered_from_lambda_admissible
    (a b : LambdaState)
    (h : lambda_admissible a b) :
    time_ordered a b :=
  h.right.right

end Lambda_t
end Obsidia
