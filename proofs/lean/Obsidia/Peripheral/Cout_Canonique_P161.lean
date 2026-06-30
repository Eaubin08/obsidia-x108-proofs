-- Cout_Canonique_P161 -- Cout(A,t) = kappa(A)*(1+dM)*q(U)/Rc formule canonique P161 V5
-- Status : PROVISIONAL scaffold -- Palier 5 item 99/134 repair
-- SOURCE_COVERAGE: cout_canonique_P161 | kappa_action | vitesse_memoire_dM | urgence_U
--                  ressources_Rc | base_cost | friction_cost | risk_cost | reserve
--                  cost_admissible | zero_cost | P161_V5 | reserve_covers_cost
--                  kernel_boundary | action_cost_governance
-- PROVISIONAL_BOUNDARY: formule fermee canonique P161 V5 approximee en Nat et flags Bool.
--   Cout(A,t) = kappa(A) * (1 + ||dM(t)||) * q(U(t)) / Rc(t).
--   Le cout ne decide pas : il nourrit l admissibilite avant passage kernel.
--   reserve_covers_cost signifie que le cout brut reste couvert par les ressources disponibles.

namespace Obsidia
namespace CoutCanoniqueP161

structure CostState where
  base_cost : Nat
  friction_cost : Nat
  risk_cost : Nat
  reserve : Nat
  kappa_action : Nat
  vitesse_memoire_dM : Nat
  urgence_U : Nat
  ressources_Rc : Nat
  cost_computed : Bool
  reserve_covers_cost : Bool
  cost_admissible : Bool
  zero_cost : Bool
  P161_V5 : Bool
  kernel_boundary : Bool

def raw_cost (s : CostState) : Nat :=
  s.base_cost + s.friction_cost + s.risk_cost

def reserve_ok (s : CostState) : Prop :=
  s.reserve_covers_cost = true

def cost_ready (s : CostState) : Prop :=
  And (s.cost_computed = true)
  (And (s.P161_V5 = true)
       (s.kernel_boundary = true))

def cost_admissible_state (s : CostState) : Prop :=
  And (s.cost_admissible = true)
  (And (reserve_ok s)
       (cost_ready s))

def zero_cost_state (reserve : Nat) : CostState :=
  { base_cost := 0,
    friction_cost := 0,
    risk_cost := 0,
    reserve := reserve,
    kappa_action := 0,
    vitesse_memoire_dM := 0,
    urgence_U := 0,
    ressources_Rc := 1,
    cost_computed := true,
    reserve_covers_cost := true,
    cost_admissible := true,
    zero_cost := true,
    P161_V5 := true,
    kernel_boundary := true }

def cost_canonique : CostState :=
  { base_cost := 10,
    friction_cost := 2,
    risk_cost := 3,
    reserve := 20,
    kappa_action := 2,
    vitesse_memoire_dM := 1,
    urgence_U := 20,
    ressources_Rc := 5,
    cost_computed := true,
    reserve_covers_cost := true,
    cost_admissible := true,
    zero_cost := false,
    P161_V5 := true,
    kernel_boundary := true }

theorem raw_cost_reflects_components
    (s : CostState) :
    raw_cost s = s.base_cost + s.friction_cost + s.risk_cost :=
  rfl

theorem zero_cost_raw_cost
    (reserve : Nat) :
    raw_cost (zero_cost_state reserve) = 0 :=
  rfl

theorem zero_cost_state_admissible
    (reserve : Nat) :
    cost_admissible_state (zero_cost_state reserve) :=
  And.intro rfl (And.intro rfl (And.intro rfl (And.intro rfl rfl)))

theorem cost_canonique_admissible :
    cost_admissible_state cost_canonique :=
  And.intro rfl (And.intro rfl (And.intro rfl (And.intro rfl rfl)))

theorem cost_admissible_has_reserve
    (s : CostState)
    (h : cost_admissible_state s) :
    reserve_ok s :=
  h.right.left

theorem cost_admissible_has_kernel_boundary
    (s : CostState)
    (h : cost_admissible_state s) :
    s.kernel_boundary = true :=
  h.right.right.right.right

theorem cost_admissible_is_computed
    (s : CostState)
    (h : cost_admissible_state s) :
    s.cost_computed = true :=
  h.right.right.left

end CoutCanoniqueP161
end Obsidia
