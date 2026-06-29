namespace Obsidia
namespace M1Sigma

structure SigmaState where
sigma : Nat
bound : Nat
cost : Nat
reserve : Nat

def sigma_within_bound (s : SigmaState) : Prop :=
s.sigma <= s.bound

def reserve_covers_cost (s : SigmaState) : Prop :=
s.cost <= s.reserve

def sigma_admissible (s : SigmaState) : Prop :=
And (sigma_within_bound s) (reserve_covers_cost s)

def zero_sigma_state (bound reserve : Nat) : SigmaState :=
{ sigma := 0, bound := bound, cost := 0, reserve := reserve }

theorem sigma_within_bound_intro
(s : SigmaState)
(h : s.sigma <= s.bound) :
sigma_within_bound s :=
h

theorem reserve_covers_cost_intro
(s : SigmaState)
(h : s.cost <= s.reserve) :
reserve_covers_cost s :=
h

theorem sigma_admissible_intro
(s : SigmaState)
(hs : sigma_within_bound s)
(hr : reserve_covers_cost s) :
sigma_admissible s :=
And.intro hs hr

theorem sigma_bound_from_admissible
(s : SigmaState)
(h : sigma_admissible s) :
sigma_within_bound s :=
h.left

theorem reserve_from_admissible
(s : SigmaState)
(h : sigma_admissible s) :
reserve_covers_cost s :=
h.right

theorem zero_sigma_within_bound
(bound reserve : Nat) :
sigma_within_bound (zero_sigma_state bound reserve) :=
Nat.zero_le bound

theorem zero_sigma_cost_covered
(bound reserve : Nat) :
reserve_covers_cost (zero_sigma_state bound reserve) :=
Nat.zero_le reserve

theorem zero_sigma_state_admissible
(bound reserve : Nat) :
sigma_admissible (zero_sigma_state bound reserve) :=
And.intro (Nat.zero_le bound) (Nat.zero_le reserve)

theorem sigma_state_fields_reflect
(s : SigmaState) :
s.sigma = s.sigma :=
rfl

end M1Sigma
end Obsidia
