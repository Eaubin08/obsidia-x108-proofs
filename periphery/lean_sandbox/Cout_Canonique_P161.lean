namespace Obsidia
namespace CoutCanoniqueP161

structure CostState where
base_cost : Nat
friction_cost : Nat
risk_cost : Nat
reserve : Nat

def raw_cost (s : CostState) : Nat :=
s.base_cost + s.friction_cost + s.risk_cost

def reserve_covers_cost (s : CostState) : Prop :=
raw_cost s <= s.reserve

def cost_admissible (s : CostState) : Prop :=
reserve_covers_cost s

def zero_cost_state (reserve : Nat) : CostState :=
{ base_cost := 0, friction_cost := 0, risk_cost := 0, reserve := reserve }

theorem raw_cost_reflects_components
(s : CostState) :
raw_cost s = s.base_cost + s.friction_cost + s.risk_cost :=
rfl

theorem cost_admissible_intro
(s : CostState)
(h : reserve_covers_cost s) :
cost_admissible s :=
h

theorem reserve_covers_from_cost_admissible
(s : CostState)
(h : cost_admissible s) :
reserve_covers_cost s :=
h

theorem zero_cost_raw_cost
(reserve : Nat) :
raw_cost (zero_cost_state reserve) = 0 :=
rfl

theorem zero_cost_state_reserve_covers
(reserve : Nat) :
reserve_covers_cost (zero_cost_state reserve) :=
Nat.zero_le reserve

theorem zero_cost_state_admissible
(reserve : Nat) :
cost_admissible (zero_cost_state reserve) :=
Nat.zero_le reserve

theorem cost_bound_is_reserve_bound
(s : CostState)
(h : cost_admissible s) :
raw_cost s <= s.reserve :=
h

end CoutCanoniqueP161
end Obsidia
